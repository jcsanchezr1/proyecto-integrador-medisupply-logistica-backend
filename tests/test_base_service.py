"""
Tests para BaseService
"""
import pytest
from abc import ABC
from app.services.base_service import BaseService


class TestBaseService:
    """Tests para BaseService"""
    
    def test_base_service_is_abstract(self):
        """Test: BaseService es una clase abstracta"""
        assert issubclass(BaseService, ABC)
    
    def test_base_service_cannot_be_instantiated(self):
        """Test: BaseService no puede ser instanciada directamente"""
        with pytest.raises(TypeError):
            BaseService()
    
    def test_base_service_has_abstract_methods(self):
        """Test: BaseService tiene métodos abstractos"""
        assert hasattr(BaseService, 'create')
        assert hasattr(BaseService, 'get_by_id')
        assert hasattr(BaseService, 'get_all')
        assert hasattr(BaseService, 'update')
        assert hasattr(BaseService, 'delete')
    
    def test_base_service_abstract_methods_must_be_implemented(self):
        """Test: BaseService requiere implementación de métodos abstractos"""
        class IncompleteService(BaseService):
            def create(self, data):
                pass
        
        with pytest.raises(TypeError):
            IncompleteService()

