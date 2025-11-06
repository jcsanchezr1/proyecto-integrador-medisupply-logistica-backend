import pytest
from app.controllers.health_controller import HealthCheckView


class TestHealthCheckView:
    def test_get_method_exists(self):
        assert hasattr(HealthCheckView, 'get')
    
    def test_get_method_signature(self):
        import inspect
        sig = inspect.signature(HealthCheckView.get)
        assert len(sig.parameters) == 1
    
    def test_get_response(self):
        view = HealthCheckView()
        response, status_code = view.get()
        
        assert response == "pong"
        assert status_code == 200


