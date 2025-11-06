"""
Tests para OrdersIntegration
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from app.integrations.orders_integration import OrdersIntegration
import requests


class TestOrdersIntegration:
    """Tests para OrdersIntegration"""
    
    @pytest.fixture
    def orders_integration(self):
        """Instancia de OrdersIntegration"""
        return OrdersIntegration()
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_success(self, mock_get, orders_integration):
        """Test: Obtener pedidos por camión y fecha exitosamente"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': [
                {'id': 1, 'client_id': 'client-1'},
                {'id': 2, 'client_id': 'client-2'}
            ]
        }
        mock_get.return_value = mock_response
        
        result = orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert len(result) == 2
        assert result[0]['id'] == 1
        mock_get.assert_called_once()
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_empty(self, mock_get, orders_integration):
        """Test: Obtener pedidos cuando no hay datos"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': []
        }
        mock_get.return_value = mock_response
        
        result = orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert len(result) == 0
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_404(self, mock_get, orders_integration):
        """Test: Obtener pedidos cuando no se encuentran (404)"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert len(result) == 0
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_other_status(self, mock_get, orders_integration):
        """Test: Obtener pedidos con otro código de estado"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert len(result) == 0
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_no_success(self, mock_get, orders_integration):
        """Test: Obtener pedidos cuando success es False"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': False,
            'data': []
        }
        mock_get.return_value = mock_response
        
        result = orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert len(result) == 0
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_no_data(self, mock_get, orders_integration):
        """Test: Obtener pedidos cuando no hay campo data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True
        }
        mock_get.return_value = mock_response
        
        result = orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert len(result) == 0
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_request_exception(self, mock_get, orders_integration):
        """Test: Error de conexión con servicio de pedidos"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(Exception, match="Error al consultar servicio de pedidos"):
            orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_by_truck_and_date_general_exception(self, mock_get, orders_integration):
        """Test: Error general al consultar pedidos"""
        mock_get.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Error al consultar servicio de pedidos"):
            orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
    
    @patch('app.integrations.orders_integration.OrdersIntegration.get_orders_by_truck_and_date')
    def test_has_orders_for_truck_and_date_true(self, mock_get_orders, orders_integration):
        """Test: Verificar si hay pedidos cuando existen"""
        mock_get_orders.return_value = [{'id': 1}, {'id': 2}]
        
        result = orders_integration.has_orders_for_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert result is True
    
    @patch('app.integrations.orders_integration.OrdersIntegration.get_orders_by_truck_and_date')
    def test_has_orders_for_truck_and_date_false(self, mock_get_orders, orders_integration):
        """Test: Verificar si hay pedidos cuando no existen"""
        mock_get_orders.return_value = []
        
        result = orders_integration.has_orders_for_truck_and_date('CAM-001', date(2025, 12, 26))
        
        assert result is False
    
    @patch('app.integrations.orders_integration.os.getenv')
    @patch('app.integrations.orders_integration.requests.get')
    def test_orders_service_url_from_env(self, mock_get, mock_getenv, orders_integration):
        """Test: URL del servicio desde variable de entorno"""
        mock_getenv.return_value = 'http://custom-url:8080'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': []}
        mock_get.return_value = mock_response
        
        integration = OrdersIntegration()
        integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))
        
        call_args = mock_get.call_args
        assert 'http://custom-url:8080' in str(call_args)
    
    @patch('app.integrations.orders_integration.requests.get')
    def test_get_orders_exception_handling(self, mock_get, orders_integration):
        """Test: Manejo de excepciones generales (no RequestException)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        def side_effect_json():
            raise TypeError("Unexpected type error")
        
        mock_response.json = side_effect_json
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="Error al consultar servicio de pedidos"):
            orders_integration.get_orders_by_truck_and_date('CAM-001', date(2025, 12, 26))

