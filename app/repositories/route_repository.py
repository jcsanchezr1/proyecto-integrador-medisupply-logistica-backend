from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func, desc
from datetime import date
from ..models.route import Route
from ..models.db_models import RouteDB
from .base_repository import BaseRepository


class RouteRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def create(self, route: Route) -> Route:
        try:
            db_route = RouteDB(
                route_code=route.route_code,
                assigned_truck=route.assigned_truck,
                delivery_date=route.delivery_date,
                orders_count=route.orders_count
            )
            self.session.add(db_route)
            self.session.commit()
            self.session.refresh(db_route)
            
            return self._db_to_model(db_route)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al crear ruta: {str(e)}")
    
    def get_by_id(self, route_id: int) -> Optional[Route]:
        try:
            db_route = self.session.query(RouteDB).filter(RouteDB.id == route_id).first()
            if db_route:
                return self._db_to_model(db_route)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener ruta: {str(e)}")
    
    def get_all(self) -> List[Route]:
        try:
            db_routes = self.session.query(RouteDB).order_by(desc(RouteDB.delivery_date)).all()
            return [self._db_to_model(db_route) for db_route in db_routes]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener rutas: {str(e)}")
    
    def get_routes_paginated(
        self,
        limit: int,
        offset: int,
        route_code: Optional[str] = None,
        assigned_truck: Optional[str] = None,
        delivery_date: Optional[date] = None
    ) -> List[Route]:
        try:
            query = self.session.query(RouteDB)
            
            if route_code:
                query = query.filter(RouteDB.route_code.ilike(f"%{route_code}%"))
            
            if assigned_truck:
                query = query.filter(RouteDB.assigned_truck.ilike(f"%{assigned_truck}%"))
            
            if delivery_date:
                query = query.filter(RouteDB.delivery_date == delivery_date)
            
            query = query.order_by(desc(RouteDB.delivery_date))
            query = query.limit(limit).offset(offset)
            
            db_routes = query.all()
            return [self._db_to_model(db_route) for db_route in db_routes]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener rutas paginadas: {str(e)}")
    
    def count_routes(
        self,
        route_code: Optional[str] = None,
        assigned_truck: Optional[str] = None,
        delivery_date: Optional[date] = None
    ) -> int:
        try:
            query = self.session.query(func.count(RouteDB.id))
            
            if route_code:
                query = query.filter(RouteDB.route_code.ilike(f"%{route_code}%"))
            
            if assigned_truck:
                query = query.filter(RouteDB.assigned_truck.ilike(f"%{assigned_truck}%"))
            
            if delivery_date:
                query = query.filter(RouteDB.delivery_date == delivery_date)
            
            return query.scalar() or 0
        except SQLAlchemyError as e:
            raise Exception(f"Error al contar rutas: {str(e)}")
    
    def get_route_by_truck_and_date(self, truck: str, delivery_date: date) -> Optional[Route]:
        try:
            db_route = self.session.query(RouteDB).filter(
                and_(
                    RouteDB.assigned_truck == truck,
                    RouteDB.delivery_date == delivery_date
                )
            ).first()
            
            if db_route:
                return self._db_to_model(db_route)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener ruta por camión y fecha: {str(e)}")
    
    def get_next_sequence_number(self) -> int:
        try:
            last_route = self.session.query(RouteDB).order_by(desc(RouteDB.id)).first()
            if last_route:
                return last_route.id + 1
            return 1
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener siguiente número de secuencia: {str(e)}")
    
    def update(self, route: Route) -> Route:
        try:
            db_route = self.session.query(RouteDB).filter(RouteDB.id == route.id).first()
            if not db_route:
                raise Exception("Ruta no encontrada")
            
            db_route.route_code = route.route_code
            db_route.assigned_truck = route.assigned_truck
            db_route.delivery_date = route.delivery_date
            db_route.orders_count = route.orders_count
            
            self.session.commit()
            return self._db_to_model(db_route)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al actualizar ruta: {str(e)}")
    
    def delete(self, route_id: int) -> bool:
        try:
            db_route = self.session.query(RouteDB).filter(RouteDB.id == route_id).first()
            if not db_route:
                return False
            
            self.session.delete(db_route)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al eliminar ruta: {str(e)}")
    
    def delete_all(self) -> int:
        try:
            count = self.session.query(RouteDB).count()
            self.session.query(RouteDB).delete()
            self.session.commit()
            return count
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al eliminar todas las rutas: {str(e)}")
    
    def _db_to_model(self, db_route: RouteDB) -> Route:
        return Route(
            id=db_route.id,
            route_code=db_route.route_code,
            assigned_truck=db_route.assigned_truck,
            delivery_date=db_route.delivery_date,
            orders_count=db_route.orders_count,
            created_at=db_route.created_at,
            updated_at=db_route.updated_at
        )

