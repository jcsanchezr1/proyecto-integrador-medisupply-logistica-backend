"""
Tests para los controladores de rutas
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from app.controllers.route_controller import (
    RouteCreateController,
    RouteListController,
    RouteDetailController,
    RouteDeleteAllController
)
from app.exceptions.custom_exceptions import LogisticsValidationError, LogisticsBusinessLogicError
from app.models.route import Route
from datetime import date, timedelta


class TestRouteCreateController:
    """Tests para RouteCreateController"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with patch('app.controllers.route_controller.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            self.controller = RouteCreateController()
            self.controller.route_service = Mock()
    
    def test_post_success(self):
        """Test: Creación exitosa de ruta"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        route_data = {
            'assigned_truck': 'CAM-001',
            'delivery_date': tomorrow
        }
        
        mock_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date.today() + timedelta(days=1),
            orders_count=5
        )
        self.controller.route_service.create_route.return_value = mock_route
        
        with self.app.test_request_context(json=route_data):
            response = self.controller.post()
        
        assert response[1] == 201
        assert response[0]['success'] is True
        assert response[0]['message'] == 'Ruta creada exitosamente'
        assert 'data' in response[0]
        self.controller.route_service.create_route.assert_called_once()
    
    def test_post_empty_json(self):
        """Test: Error cuando el JSON está vacío"""
        from flask import request
        
        with self.app.test_request_context():
            with patch.object(request, 'get_json', return_value=None):
                response = self.controller.post()
        
        assert response[1] == 400
        assert response[0]['success'] is False
        assert 'Error de validación' in response[0]['error']
    
    def test_post_validation_error(self):
        """Test: Error de validación"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        route_data = {
            'assigned_truck': 'CAM-999',
            'delivery_date': tomorrow
        }
        
        self.controller.route_service.create_route.side_effect = LogisticsValidationError("Camión inválido")
        
        with self.app.test_request_context(json=route_data):
            response = self.controller.post()
        
        assert response[1] == 400
        assert response[0]['success'] is False
        assert 'Error de validación' in response[0]['error']
    
    def test_post_business_logic_error(self):
        """Test: Error de lógica de negocio"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        route_data = {
            'assigned_truck': 'CAM-001',
            'delivery_date': tomorrow
        }
        
        self.controller.route_service.create_route.side_effect = LogisticsBusinessLogicError("No hay pedidos")
        
        with self.app.test_request_context(json=route_data):
            response = self.controller.post()
        
        assert response[1] == 422
        assert response[0]['success'] is False
        assert 'Error de lógica de negocio' in response[0]['error']
    
    def test_post_internal_error(self):
        """Test: Error interno del servidor"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        route_data = {
            'assigned_truck': 'CAM-001',
            'delivery_date': tomorrow
        }
        
        self.controller.route_service.create_route.side_effect = Exception("Unexpected error")
        
        with self.app.test_request_context(json=route_data):
            response = self.controller.post()
        
        assert response[1] == 500
        assert response[0]['success'] is False


class TestRouteListController:
    """Tests para RouteListController"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        with patch('app.controllers.route_controller.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            self.controller = RouteListController()
            self.controller.route_service = Mock()
    
    def test_get_success(self):
        """Test: Obtener lista de rutas exitosamente"""
        mock_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        self.controller.route_service.get_routes_paginated.return_value = [mock_route]
        self.controller.route_service.count_routes.return_value = 1
        
        with self.app.test_request_context('/?page=1&per_page=10'):
            response = self.controller.get()
        
        assert response[1] == 200
        assert response[0]['success'] is True
        assert 'data' in response[0]
        assert 'routes' in response[0]['data']
        assert 'pagination' in response[0]['data']
    
    def test_get_with_filters(self):
        """Test: Obtener lista de rutas con filtros"""
        mock_route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        self.controller.route_service.get_routes_paginated.return_value = [mock_route]
        self.controller.route_service.count_routes.return_value = 1
        
        with self.app.test_request_context('/?page=1&per_page=10&route_code=ROU-0001&assigned_truck=CAM-001&delivery_date=2025-12-26'):
            response = self.controller.get()
        
        assert response[1] == 200
        assert response[0]['success'] is True
    
    def test_get_invalid_page(self):
        """Test: Error cuando page es inválido"""
        with self.app.test_request_context('/?page=0'):
            response = self.controller.get()
        
        assert response[1] == 400
        assert response[0]['success'] is False
    
    def test_get_invalid_per_page_low(self):
        """Test: Error cuando per_page es muy bajo"""
        with self.app.test_request_context('/?page=1&per_page=0'):
            response = self.controller.get()
        
        assert response[1] == 400
        assert response[0]['success'] is False
    
    def test_get_invalid_per_page_high(self):
        """Test: Error cuando per_page es muy alto"""
        with self.app.test_request_context('/?page=1&per_page=101'):
            response = self.controller.get()
        
        assert response[1] == 400
        assert response[0]['success'] is False
    
    def test_get_validation_error(self):
        """Test: Error de validación"""
        self.controller.route_service.get_routes_paginated.side_effect = LogisticsValidationError("Fecha inválida")
        
        with self.app.test_request_context('/?page=1&per_page=10&delivery_date=invalid'):
            response = self.controller.get()
        
        assert response[1] == 400
        assert response[0]['success'] is False
    
    def test_get_business_logic_error(self):
        """Test: Error de lógica de negocio"""
        self.controller.route_service.get_routes_paginated.side_effect = LogisticsBusinessLogicError("Error de BD")
        
        with self.app.test_request_context('/?page=1&per_page=10'):
            response = self.controller.get()
        
        assert response[1] == 500
        assert response[0]['success'] is False
    
    def test_get_exception_handling(self):
        """Test: Manejo de excepciones generales"""
        self.controller.route_service.get_routes_paginated.side_effect = Exception("Unexpected error")
        
        with self.app.test_request_context('/?page=1&per_page=10'):
            response = self.controller.get()
        
        assert response[1] == 500
        assert response[0]['success'] is False
    
    def test_get_pagination_info(self):
        """Test: Verificar información de paginación"""
        mock_routes = [
            Route(route_code=f"ROU-{i:04d}", assigned_truck="CAM-001", delivery_date=date(2025, 12, 26), orders_count=5)
            for i in range(1, 11)
        ]
        self.controller.route_service.get_routes_paginated.return_value = mock_routes
        self.controller.route_service.count_routes.return_value = 25
        
        with self.app.test_request_context('/?page=1&per_page=10'):
            response = self.controller.get()
        
        pagination = response[0]['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['per_page'] == 10
        assert pagination['total'] == 25
        assert pagination['total_pages'] == 3
        assert pagination['has_next'] is True
        assert pagination['has_prev'] is False


class TestRouteDetailController:
    """Tests para RouteDetailController"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        with patch('app.controllers.route_controller.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            self.controller = RouteDetailController()
            self.controller.route_service = Mock()
    
    def test_get_success(self):
        """Test: Obtener detalle de ruta exitosamente"""
        route_data = {
            'route': {
                'id': 1,
                'route_code': 'ROU-0001',
                'assigned_truck': 'CAM-001',
                'delivery_date': '2025-12-26',
                'orders_count': 5
            },
            'clients': [
                {
                    'id': 'client-1',
                    'name': 'Cliente 1',
                    'email': 'cliente1@test.com',
                    'latitude': 10.0,
                    'longitude': -75.0
                }
            ]
        }
        
        self.controller.route_service.get_route_with_clients.return_value = route_data
        
        with self.app.test_request_context('/routes/1'):
            response = self.controller.get(1)
        
        assert response[1] == 200
        assert response[0]['success'] is True
        assert 'data' in response[0]
        assert 'route' in response[0]['data']
        assert 'clients' in response[0]['data']
    
    def test_get_not_found(self):
        """Test: Error cuando la ruta no existe"""
        self.controller.route_service.get_route_with_clients.side_effect = LogisticsBusinessLogicError("Ruta no encontrada")
        
        with self.app.test_request_context('/routes/999'):
            response = self.controller.get(999)
        
        assert response[1] == 404
        assert response[0]['success'] is False
        assert 'Error de lógica de negocio' in response[0]['error']
    
    def test_get_internal_error(self):
        """Test: Error interno del servidor"""
        self.controller.route_service.get_route_with_clients.side_effect = Exception("Unexpected error")
        
        with self.app.test_request_context('/routes/1'):
            response = self.controller.get(1)
        
        assert response[1] == 500
        assert response[0]['success'] is False


class TestRouteDeleteAllController:
    """Tests para RouteDeleteAllController"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        with patch('app.controllers.route_controller.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            self.controller = RouteDeleteAllController()
            self.controller.route_repository = Mock()
    
    def test_delete_success(self):
        """Test: Eliminar todas las rutas exitosamente"""
        self.controller.route_repository.delete_all.return_value = 5
        
        with self.app.test_request_context():
            response = self.controller.delete()
        
        assert response[1] == 200
        assert response[0]['success'] is True
        assert response[0]['data']['deleted_count'] == 5
        assert 'Se eliminaron 5 rutas' in response[0]['message']
    
    def test_delete_empty(self):
        """Test: Eliminar cuando no hay rutas"""
        self.controller.route_repository.delete_all.return_value = 0
        
        with self.app.test_request_context():
            response = self.controller.delete()
        
        assert response[1] == 200
        assert response[0]['data']['deleted_count'] == 0
    
    def test_delete_internal_error(self):
        """Test: Error interno del servidor"""
        self.controller.route_repository.delete_all.side_effect = Exception("Database error")
        
        with self.app.test_request_context():
            response = self.controller.delete()
        
        assert response[1] == 500
        assert response[0]['success'] is False

