"""
Tests para RouteService
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime, date, timedelta
from app.services.route_service import RouteService
from app.repositories.route_repository import RouteRepository
from app.exceptions.custom_exceptions import LogisticsValidationError, LogisticsBusinessLogicError
from app.models.route import Route
from app.integrations.orders_integration import OrdersIntegration
from app.integrations.auth_integration import AuthIntegration


class TestRouteService:
    """Tests para RouteService"""
    
    @pytest.fixture
    def mock_route_repository(self):
        """Mock del RouteRepository"""
        return MagicMock(spec=RouteRepository)
    
    @pytest.fixture
    def mock_orders_integration(self):
        """Mock del OrdersIntegration"""
        return MagicMock(spec=OrdersIntegration)
    
    @pytest.fixture
    def mock_auth_integration(self):
        """Mock del AuthIntegration"""
        return MagicMock(spec=AuthIntegration)
    
    @pytest.fixture
    def route_service(self, mock_route_repository, mock_orders_integration, mock_auth_integration):
        """Instancia de RouteService con dependencias mockeadas"""
        service = RouteService(mock_route_repository)
        service.orders_integration = mock_orders_integration
        service.auth_integration = mock_auth_integration
        return service
    
    @pytest.fixture
    def valid_route_data(self):
        """Datos válidos para crear una ruta"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        return {
            'assigned_truck': 'CAM-001',
            'delivery_date': tomorrow
        }
    
    def test_create_route_success(self, route_service, mock_route_repository, mock_orders_integration, valid_route_data):
        """Test: Creación exitosa de ruta"""
        delivery_date = date.today() + timedelta(days=1)
        mock_orders_integration.has_orders_for_truck_and_date.return_value = True
        
        mock_orders = [
            {'id': 1, 'client_id': 'client-1'},
            {'id': 2, 'client_id': 'client-2'}
        ]
        mock_orders_integration.get_orders_by_truck_and_date.return_value = mock_orders
        
        mock_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date,
            orders_count=2
        )
        mock_route_repository.get_next_sequence_number.return_value = 1
        mock_route_repository.get_route_by_truck_and_date.return_value = None
        mock_route_repository.create.return_value = mock_route
        
        result = route_service.create_route(valid_route_data)
        
        assert result.route_code == "ROU-0001"
        assert result.orders_count == 2
        mock_orders_integration.has_orders_for_truck_and_date.assert_called_once()
        mock_route_repository.create.assert_called_once()
    
    def test_create_route_missing_assigned_truck(self, route_service):
        """Test: Error cuando falta assigned_truck"""
        route_data = {
            'delivery_date': '2025-12-26'
        }
        
        with pytest.raises(LogisticsValidationError, match="El campo 'assigned_truck' es obligatorio"):
            route_service.create_route(route_data)
    
    def test_create_route_missing_delivery_date(self, route_service):
        """Test: Error cuando falta delivery_date"""
        route_data = {
            'assigned_truck': 'CAM-001'
        }
        
        with pytest.raises(LogisticsValidationError, match="El campo 'delivery_date' es obligatorio"):
            route_service.create_route(route_data)
    
    def test_create_route_invalid_truck(self, route_service):
        """Test: Error cuando el camión no es válido"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        route_data = {
            'assigned_truck': 'CAM-999',
            'delivery_date': tomorrow
        }
        
        with pytest.raises(LogisticsValidationError, match="no es válido"):
            route_service.create_route(route_data)
    
    def test_create_route_invalid_date_format(self, route_service):
        """Test: Error cuando el formato de fecha es inválido"""
        route_data = {
            'assigned_truck': 'CAM-001',
            'delivery_date': 'invalid-date'
        }
        
        with pytest.raises(LogisticsValidationError, match="formato de 'delivery_date'"):
            route_service.create_route(route_data)
    
    def test_create_route_date_as_date_object(self, route_service, mock_route_repository, mock_orders_integration):
        """Test: Crear ruta con delivery_date como objeto date"""
        delivery_date = date.today() + timedelta(days=1)
        route_data = {
            'assigned_truck': 'CAM-001',
            'delivery_date': delivery_date
        }
        
        mock_orders_integration.has_orders_for_truck_and_date.return_value = True
        mock_orders_integration.get_orders_by_truck_and_date.return_value = [{'id': 1}]
        mock_route_repository.get_route_by_truck_and_date.return_value = None
        mock_route_repository.get_next_sequence_number.return_value = 1
        
        mock_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date,
            orders_count=1
        )
        mock_route_repository.create.return_value = mock_route
        
        result = route_service.create_route(route_data)
        
        assert result.route_code == "ROU-0001"
    
    def test_create_route_past_date(self, route_service):
        """Test: Error cuando la fecha es en el pasado o hoy"""
        today = date.today().isoformat()
        route_data = {
            'assigned_truck': 'CAM-001',
            'delivery_date': today
        }
        
        with pytest.raises(LogisticsValidationError, match="día siguiente"):
            route_service.create_route(route_data)
    
    def test_create_route_duplicate_truck_and_date(self, route_service, mock_route_repository, mock_orders_integration, valid_route_data):
        """Test: Error cuando el camión ya tiene una ruta para esa fecha"""
        delivery_date = date.today() + timedelta(days=1)
        existing_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date,
            orders_count=2
        )
        
        mock_route_repository.get_route_by_truck_and_date.return_value = existing_route
        
        with pytest.raises(LogisticsBusinessLogicError, match="ya tiene una ruta asignada"):
            route_service.create_route(valid_route_data)
    
    def test_create_route_no_orders(self, route_service, mock_route_repository, mock_orders_integration, valid_route_data):
        """Test: Error cuando el camión no tiene pedidos para esa fecha"""
        delivery_date = date.today() + timedelta(days=1)
        mock_route_repository.get_route_by_truck_and_date.return_value = None
        mock_orders_integration.has_orders_for_truck_and_date.return_value = False
        
        with pytest.raises(LogisticsBusinessLogicError, match="no tiene pedidos asignados"):
            route_service.create_route(valid_route_data)
    
    def test_get_routes_paginated_success(self, route_service, mock_route_repository):
        """Test: Obtener rutas paginadas exitosamente"""
        mock_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        mock_route_repository.get_routes_paginated.return_value = [mock_route]
        mock_route_repository.count_routes.return_value = 1
        
        result = route_service.get_routes_paginated(page=1, per_page=10)
        
        assert len(result) == 1
        assert result[0].route_code == "ROU-0001"
    
    def test_get_routes_paginated_with_filters(self, route_service, mock_route_repository):
        """Test: Obtener rutas paginadas con filtros"""
        mock_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        mock_route_repository.get_routes_paginated.return_value = [mock_route]
        
        result = route_service.get_routes_paginated(
            page=1,
            per_page=10,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date="2025-12-26"
        )
        
        assert len(result) == 1
    
    def test_get_routes_paginated_invalid_date(self, route_service):
        """Test: Error al obtener rutas con fecha inválida"""
        with pytest.raises(LogisticsValidationError, match="formato de 'delivery_date'"):
            route_service.get_routes_paginated(
                page=1,
                per_page=10,
                delivery_date="invalid-date"
            )
    
    def test_count_routes_success(self, route_service, mock_route_repository):
        """Test: Contar rutas exitosamente"""
        mock_route_repository.count_routes.return_value = 5
        
        result = route_service.count_routes()
        
        assert result == 5
    
    def test_count_routes_with_filters(self, route_service, mock_route_repository):
        """Test: Contar rutas con filtros"""
        mock_route_repository.count_routes.return_value = 2
        
        result = route_service.count_routes(
            route_code="ROU-0001",
            assigned_truck="CAM-001"
        )
        
        assert result == 2
    
    def test_get_route_with_clients_success(self, route_service, mock_route_repository, mock_orders_integration, mock_auth_integration):
        """Test: Obtener ruta con clientes exitosamente"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=2
        )
        
        mock_route_repository.get_by_id.return_value = route
        
        mock_orders = [
            {'id': 1, 'client_id': 'client-1'},
            {'id': 2, 'client_id': 'client-2'},
            {'id': 3, 'client_id': 'client-1'}
        ]
        mock_orders_integration.get_orders_by_truck_and_date.return_value = mock_orders
        
        mock_users = {
            'client-1': {
                'id': 'client-1',
                'name': 'Cliente 1',
                'email': 'cliente1@test.com',
                'latitude': 10.0,
                'longitude': -75.0
            },
            'client-2': {
                'id': 'client-2',
                'name': 'Cliente 2',
                'email': 'cliente2@test.com',
                'latitude': 11.0,
                'longitude': -76.0
            }
        }
        mock_auth_integration.get_users_by_ids.return_value = mock_users
        
        result = route_service.get_route_with_clients(1)
        
        assert 'route' in result
        assert 'clients' in result
        assert len(result['clients']) == 2
        assert result['route']['route_code'] == "ROU-0001"
    
    def test_get_route_with_clients_not_found(self, route_service, mock_route_repository):
        """Test: Error cuando la ruta no existe"""
        mock_route_repository.get_by_id.return_value = None
        
        with pytest.raises(LogisticsBusinessLogicError, match="Ruta no encontrada"):
            route_service.get_route_with_clients(999)
    
    def test_get_route_with_clients_no_client_ids(self, route_service, mock_route_repository, mock_orders_integration, mock_auth_integration):
        """Test: Obtener ruta con pedidos sin client_id"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=2
        )
        
        mock_route_repository.get_by_id.return_value = route
        mock_orders_integration.get_orders_by_truck_and_date.return_value = [
            {'id': 1, 'client_id': None},
            {'id': 2}
        ]
        mock_auth_integration.get_users_by_ids.return_value = {}
        
        result = route_service.get_route_with_clients(1)
        
        assert len(result['clients']) == 0
    
    def test_create_route_exception_handling(self, route_service, mock_route_repository, mock_orders_integration, valid_route_data):
        """Test: Manejo de excepciones inesperadas al crear ruta"""
        delivery_date = date.today() + timedelta(days=1)
        mock_route_repository.get_route_by_truck_and_date.return_value = None
        mock_orders_integration.has_orders_for_truck_and_date.return_value = True
        mock_orders_integration.get_orders_by_truck_and_date.return_value = [{'id': 1}]
        mock_route_repository.get_next_sequence_number.side_effect = Exception("Unexpected error")
        
        with pytest.raises(LogisticsBusinessLogicError):
            route_service.create_route(valid_route_data)
    
    def test_get_routes_paginated_exception(self, route_service, mock_route_repository):
        """Test: Manejo de excepciones al obtener rutas paginadas"""
        mock_route_repository.get_routes_paginated.side_effect = Exception("Database error")
        
        with pytest.raises(LogisticsBusinessLogicError):
            route_service.get_routes_paginated(page=1, per_page=10)
    
    def test_count_routes_exception(self, route_service, mock_route_repository):
        """Test: Manejo de excepciones al contar rutas"""
        mock_route_repository.count_routes.side_effect = Exception("Database error")
        
        with pytest.raises(LogisticsBusinessLogicError):
            route_service.count_routes()
    
    def test_get_route_with_clients_exception(self, route_service, mock_route_repository, mock_orders_integration):
        """Test: Manejo de excepciones al obtener ruta con clientes"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=2
        )
        
        mock_route_repository.get_by_id.return_value = route
        mock_orders_integration.get_orders_by_truck_and_date.side_effect = Exception("Integration error")
        
        with pytest.raises(LogisticsBusinessLogicError):
            route_service.get_route_with_clients(1)
    
    def test_get_routes_paginated_with_invalid_date_string(self, route_service):
        """Test: Error con formato de fecha inválido en get_routes_paginated"""
        with pytest.raises(LogisticsValidationError):
            route_service.get_routes_paginated(
                page=1,
                per_page=10,
                delivery_date="not-a-date"
            )
    
    def test_count_routes_with_invalid_date_string(self, route_service):
        """Test: Error con formato de fecha inválido en count_routes"""
        with pytest.raises(LogisticsValidationError):
            route_service.count_routes(delivery_date="not-a-date")

