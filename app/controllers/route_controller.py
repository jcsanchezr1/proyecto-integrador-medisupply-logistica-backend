from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple
from ..services.route_service import RouteService
from ..repositories.route_repository import RouteRepository
from ..exceptions.custom_exceptions import LogisticsValidationError, LogisticsBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session, SessionLocal


class RouteCreateController(BaseController):
    def __init__(self):
        session = SessionLocal()
        self.route_repository = RouteRepository(session)
        self.route_service = RouteService(self.route_repository)
    
    @auto_close_session
    def post(self):
        try:
            json_data = request.get_json()
            if not json_data:
                return self.error_response(
                    "Error de validación",
                    "El cuerpo de la petición JSON está vacío",
                    400
                )
            
            route = self.route_service.create_route(json_data)
            
            return self.created_response(
                data=route.to_dict(),
                message="Ruta creada exitosamente"
            )
            
        except LogisticsValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except LogisticsBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 422)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)


class RouteListController(BaseController):
    def __init__(self):
        session = SessionLocal()
        self.route_repository = RouteRepository(session)
        self.route_service = RouteService(self.route_repository)
    
    @auto_close_session
    def get(self):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            route_code = request.args.get('route_code', type=str)
            assigned_truck = request.args.get('assigned_truck', type=str)
            delivery_date = request.args.get('delivery_date', type=str)
            
            if page < 1:
                return self.error_response(
                    "Error de validación",
                    "El parámetro 'page' debe ser mayor a 0",
                    400
                )
            
            if per_page < 1 or per_page > 100:
                return self.error_response(
                    "Error de validación",
                    "El parámetro 'per_page' debe estar entre 1 y 100",
                    400
                )
            
            routes = self.route_service.get_routes_paginated(
                page=page,
                per_page=per_page,
                route_code=route_code,
                assigned_truck=assigned_truck,
                delivery_date=delivery_date
            )
            
            total = self.route_service.count_routes(
                route_code=route_code,
                assigned_truck=assigned_truck,
                delivery_date=delivery_date
            )
            
            total_pages = (total + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            return self.success_response(
                data={
                    'routes': [route.to_dict() for route in routes],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'total_pages': total_pages,
                        'has_next': has_next,
                        'has_prev': has_prev,
                        'next_page': page + 1 if has_next else None,
                        'prev_page': page - 1 if has_prev else None
                    }
                },
                message="Rutas obtenidas exitosamente"
            )
            
        except LogisticsValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except LogisticsBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)


class RouteDeleteAllController(BaseController):
    def __init__(self):
        session = SessionLocal()
        self.route_repository = RouteRepository(session)
        self.route_service = RouteService(self.route_repository)
    
    @auto_close_session
    def delete(self):
        try:
            count = self.route_repository.delete_all()
            
            return self.success_response(
                data={'deleted_count': count},
                message=f"Se eliminaron {count} rutas exitosamente"
            )
            
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)


class RouteDetailController(BaseController):
    def __init__(self):
        session = SessionLocal()
        self.route_repository = RouteRepository(session)
        self.route_service = RouteService(self.route_repository)
    
    @auto_close_session
    def get(self, route_id: int):
        try:
            route_data = self.route_service.get_route_with_clients(route_id)
            
            return self.success_response(
                data=route_data,
                message="Ruta obtenida exitosamente"
            )
            
        except LogisticsBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 404)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)

