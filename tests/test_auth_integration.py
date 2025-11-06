"""
Tests para AuthIntegration
"""
import pytest
from unittest.mock import patch, MagicMock
from app.integrations.auth_integration import AuthIntegration
import requests


class TestAuthIntegration:
    """Tests para AuthIntegration"""
    
    @pytest.fixture
    def auth_integration(self):
        """Instancia de AuthIntegration"""
        return AuthIntegration()
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_success_with_message(self, mock_get, auth_integration):
        """Test: Obtener usuario por ID exitosamente con mensaje"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'Usuario obtenido exitosamente',
            'data': {
                'id': 'user-1',
                'name': 'Usuario 1',
                'email': 'user1@test.com',
                'latitude': 10.0,
                'longitude': -75.0
            }
        }
        mock_get.return_value = mock_response
        
        result = auth_integration.get_user_by_id('user-1')
        
        assert result is not None
        assert result['id'] == 'user-1'
        assert result['name'] == 'Usuario 1'
        mock_get.assert_called_once()
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_success_with_success(self, mock_get, auth_integration):
        """Test: Obtener usuario por ID exitosamente con success"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'id': 'user-1',
                'name': 'Usuario 1'
            }
        }
        mock_get.return_value = mock_response
        
        result = auth_integration.get_user_by_id('user-1')
        
        assert result is not None
        assert result['id'] == 'user-1'
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_not_found(self, mock_get, auth_integration):
        """Test: Usuario no encontrado (404)"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = auth_integration.get_user_by_id('user-999')
        
        assert result is None
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_other_status(self, mock_get, auth_integration):
        """Test: Obtener usuario con otro código de estado"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = auth_integration.get_user_by_id('user-1')
        
        assert result is None
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_no_data(self, mock_get, auth_integration):
        """Test: Obtener usuario cuando no hay datos"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'Usuario obtenido exitosamente'
        }
        mock_get.return_value = mock_response
        
        result = auth_integration.get_user_by_id('user-1')
        
        assert result is None
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_request_exception(self, mock_get, auth_integration):
        """Test: Error de conexión con servicio de autenticador"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(Exception, match="Error al consultar servicio de autenticador"):
            auth_integration.get_user_by_id('user-1')
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_general_exception(self, mock_get, auth_integration):
        """Test: Error general al consultar usuario"""
        mock_get.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Error al consultar servicio de autenticador"):
            auth_integration.get_user_by_id('user-1')
    
    @patch('app.integrations.auth_integration.AuthIntegration.get_user_by_id')
    def test_get_users_by_ids_success(self, mock_get_user, auth_integration):
        """Test: Obtener múltiples usuarios exitosamente"""
        mock_get_user.side_effect = [
            {'id': 'user-1', 'name': 'Usuario 1'},
            {'id': 'user-2', 'name': 'Usuario 2'}
        ]
        
        result = auth_integration.get_users_by_ids(['user-1', 'user-2'])
        
        assert len(result) == 2
        assert 'user-1' in result
        assert 'user-2' in result
        assert mock_get_user.call_count == 2
    
    @patch('app.integrations.auth_integration.AuthIntegration.get_user_by_id')
    def test_get_users_by_ids_with_duplicates(self, mock_get_user, auth_integration):
        """Test: Obtener usuarios con IDs duplicados"""
        mock_get_user.side_effect = [
            {'id': 'user-1', 'name': 'Usuario 1'}
        ]
        
        result = auth_integration.get_users_by_ids(['user-1', 'user-1', 'user-1'])
        
        assert len(result) == 1
        assert 'user-1' in result
        assert mock_get_user.call_count == 1
    
    @patch('app.integrations.auth_integration.AuthIntegration.get_user_by_id')
    def test_get_users_by_ids_with_errors(self, mock_get_user, auth_integration):
        """Test: Obtener usuarios con algunos errores"""
        def side_effect(user_id):
            if user_id == 'user-1':
                return {'id': 'user-1', 'name': 'Usuario 1'}
            elif user_id == 'user-2':
                raise Exception("Error")
            else:
                return None
        
        mock_get_user.side_effect = side_effect
        
        result = auth_integration.get_users_by_ids(['user-1', 'user-2', 'user-3'])
        
        assert len(result) == 1
        assert 'user-1' in result
    
    @patch('app.integrations.auth_integration.AuthIntegration.get_user_by_id')
    def test_get_users_by_ids_all_errors(self, mock_get_user, auth_integration):
        """Test: Obtener usuarios cuando todos fallan"""
        mock_get_user.side_effect = Exception("Error")
        
        result = auth_integration.get_users_by_ids(['user-1', 'user-2'])
        
        assert len(result) == 0
    
    @patch('app.integrations.auth_integration.AuthIntegration.get_user_by_id')
    def test_get_users_by_ids_empty_list(self, mock_get_user, auth_integration):
        """Test: Obtener usuarios con lista vacía"""
        result = auth_integration.get_users_by_ids([])
        
        assert len(result) == 0
        mock_get_user.assert_not_called()
    
    @patch('app.integrations.auth_integration.os.getenv')
    @patch('app.integrations.auth_integration.requests.get')
    def test_auth_service_url_from_env(self, mock_get, mock_getenv, auth_integration):
        """Test: URL del servicio desde variable de entorno"""
        mock_getenv.return_value = 'http://custom-url:8080'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'Usuario obtenido exitosamente',
            'data': {'id': 'user-1'}
        }
        mock_get.return_value = mock_response
        
        integration = AuthIntegration()
        integration.get_user_by_id('user-1')
        
        call_args = mock_get.call_args
        assert 'http://custom-url:8080' in str(call_args)
    
    @patch('app.integrations.auth_integration.requests.get')
    def test_get_user_by_id_exception_handling(self, mock_get, auth_integration):
        """Test: Manejo de excepciones generales (no RequestException)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        def side_effect_json():
            raise TypeError("Unexpected type error")
        
        mock_response.json = side_effect_json
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="Error al consultar servicio de autenticador"):
            auth_integration.get_user_by_id('user-1')

