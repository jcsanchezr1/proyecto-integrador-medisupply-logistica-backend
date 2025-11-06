import logging
from typing import List, Optional
from datetime import datetime, date, timedelta
from ..models.route import Route
from ..repositories.route_repository import RouteRepository
from ..exceptions.custom_exceptions import LogisticsValidationError, LogisticsBusinessLogicError
from ..integrations.orders_integration import OrdersIntegration
from ..integrations.auth_integration import AuthIntegration

logger = logging.getLogger(__name__)

VALID_TRUCKS = ["CAM-001", "CAM-002", "CAM-003", "CAM-004", "CAM-005"]


class RouteService:
    def __init__(self, route_repository: RouteRepository):
        self.route_repository = route_repository
        self.orders_integration = OrdersIntegration()
        self.auth_integration = AuthIntegration()
    
    def create_route(self, route_data: dict) -> Route:
        try:
            if not route_data.get('assigned_truck'):
                raise LogisticsValidationError("El campo 'assigned_truck' es obligatorio")
            
            if not route_data.get('delivery_date'):
                raise LogisticsValidationError("El campo 'delivery_date' es obligatorio")
            
            assigned_truck = route_data['assigned_truck'].strip()
            
            if assigned_truck not in VALID_TRUCKS:
                raise LogisticsValidationError(
                    f"El camión '{assigned_truck}' no es válido. Camiones permitidos: {', '.join(VALID_TRUCKS)}"
                )
            
            try:
                if isinstance(route_data['delivery_date'], str):
                    delivery_date = datetime.fromisoformat(route_data['delivery_date'].replace('Z', '+00:00')).date()
                else:
                    delivery_date = route_data['delivery_date']
            except (ValueError, AttributeError) as e:
                raise LogisticsValidationError("El formato de 'delivery_date' debe ser ISO 8601 válido (YYYY-MM-DD)")
            
            today = date.today()
            tomorrow = today + timedelta(days=1)
            
            if delivery_date < tomorrow:
                raise LogisticsValidationError(
                    "La fecha de entrega debe ser a partir del día siguiente. No se puede el mismo día o días anteriores."
                )
            
            existing_route = self.route_repository.get_route_by_truck_and_date(assigned_truck, delivery_date)
            if existing_route:
                raise LogisticsBusinessLogicError(
                    f"El camión {assigned_truck} ya tiene una ruta asignada para la fecha {delivery_date.isoformat()}"
                )
            
            logger.info(f"Verificando pedidos para camión {assigned_truck} en fecha {delivery_date.isoformat()}")
            
            has_orders = self.orders_integration.has_orders_for_truck_and_date(assigned_truck, delivery_date)
            
            if not has_orders:
                raise LogisticsBusinessLogicError(
                    f"El camión {assigned_truck} no tiene pedidos asignados para la fecha {delivery_date.isoformat()}"
                )
            
            orders = self.orders_integration.get_orders_by_truck_and_date(assigned_truck, delivery_date)
            orders_count = len(orders)
            
            sequence_number = self.route_repository.get_next_sequence_number()
            route_code = Route.generate_route_code(sequence_number)
            
            route = Route(
                route_code=route_code,
                assigned_truck=assigned_truck,
                delivery_date=delivery_date,
                orders_count=orders_count
            )
            
            route.validate()
            
            created_route = self.route_repository.create(route)
            logger.info(f"Ruta {created_route.route_code} creada exitosamente")
            
            return created_route
            
        except LogisticsValidationError:
            raise
        except LogisticsBusinessLogicError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear ruta: {str(e)}")
            raise LogisticsBusinessLogicError(f"Error al crear ruta: {str(e)}")
    
    def get_routes_paginated(
        self,
        page: int,
        per_page: int,
        route_code: Optional[str] = None,
        assigned_truck: Optional[str] = None,
        delivery_date: Optional[str] = None
    ) -> List[Route]:
        try:
            offset = (page - 1) * per_page
            
            parsed_date = None
            if delivery_date:
                try:
                    parsed_date = datetime.fromisoformat(delivery_date.replace('Z', '+00:00')).date()
                except (ValueError, AttributeError):
                    raise LogisticsValidationError("El formato de 'delivery_date' debe ser YYYY-MM-DD")
            
            routes = self.route_repository.get_routes_paginated(
                limit=per_page,
                offset=offset,
                route_code=route_code,
                assigned_truck=assigned_truck,
                delivery_date=parsed_date
            )
            
            return routes
            
        except LogisticsValidationError:
            raise
        except Exception as e:
            logger.error(f"Error al obtener rutas paginadas: {str(e)}")
            raise LogisticsBusinessLogicError(f"Error al obtener rutas: {str(e)}")
    
    def count_routes(
        self,
        route_code: Optional[str] = None,
        assigned_truck: Optional[str] = None,
        delivery_date: Optional[str] = None
    ) -> int:
        try:
            parsed_date = None
            if delivery_date:
                try:
                    parsed_date = datetime.fromisoformat(delivery_date.replace('Z', '+00:00')).date()
                except (ValueError, AttributeError):
                    raise LogisticsValidationError("El formato de 'delivery_date' debe ser YYYY-MM-DD")
            
            return self.route_repository.count_routes(
                route_code=route_code,
                assigned_truck=assigned_truck,
                delivery_date=parsed_date
            )
            
        except LogisticsValidationError:
            raise
        except Exception as e:
            logger.error(f"Error al contar rutas: {str(e)}")
            raise LogisticsBusinessLogicError(f"Error al contar rutas: {str(e)}")
    
    def get_route_with_clients(self, route_id: int) -> dict:
        try:
            route = self.route_repository.get_by_id(route_id)
            if not route:
                raise LogisticsBusinessLogicError("Ruta no encontrada")
            
            delivery_date = route.delivery_date
            assigned_truck = route.assigned_truck
            
            orders = self.orders_integration.get_orders_by_truck_and_date(assigned_truck, delivery_date)
            
            client_ids = set()
            for order in orders:
                if order.get('client_id'):
                    client_ids.add(order['client_id'])
            
            clients_data = self.auth_integration.get_users_by_ids(list(client_ids))
            
            clients_list = []
            for user_id, user_data in clients_data.items():
                clients_list.append({
                    'id': user_data.get('id'),
                    'name': user_data.get('name'),
                    'email': user_data.get('email'),
                    'address': user_data.get('address'),
                    'phone': user_data.get('phone'),
                    'latitude': user_data.get('latitude'),
                    'longitude': user_data.get('longitude')
                })
            
            return {
                'route': route.to_dict(),
                'clients': clients_list
            }
            
        except LogisticsBusinessLogicError:
            raise
        except Exception as e:
            logger.error(f"Error al obtener ruta con clientes: {str(e)}")
            raise LogisticsBusinessLogicError(f"Error al obtener ruta con clientes: {str(e)}")

