"""
Tests para BaseRepository
"""
import pytest
from abc import ABC
from unittest.mock import MagicMock
from app.repositories.base_repository import BaseRepository


class TestBaseRepository:
    """Tests para BaseRepository"""
    
    def test_base_repository_is_abstract(self):
        """Test: BaseRepository es una clase abstracta"""
        assert issubclass(BaseRepository, ABC)
    
    def test_base_repository_cannot_be_instantiated(self):
        """Test: BaseRepository no puede ser instanciada directamente"""
        mock_session = MagicMock()
        
        with pytest.raises(TypeError):
            BaseRepository(mock_session)
    
    def test_base_repository_has_abstract_methods(self):
        """Test: BaseRepository tiene métodos abstractos"""
        assert hasattr(BaseRepository, 'create')
        assert hasattr(BaseRepository, 'get_by_id')
        assert hasattr(BaseRepository, 'get_all')
        assert hasattr(BaseRepository, 'update')
        assert hasattr(BaseRepository, 'delete')
    
    def test_base_repository_session_attribute(self):
        """Test: BaseRepository tiene atributo session en __init__"""
        class ConcreteRepository(BaseRepository):
            def create(self, entity):
                pass
            
            def get_by_id(self, entity_id):
                pass
            
            def get_all(self):
                pass
            
            def update(self, entity):
                pass
            
            def delete(self, entity_id):
                pass
        
        mock_session = MagicMock()
        repo = ConcreteRepository(mock_session)
        
        assert repo.session == mock_session
    
    def test_base_repository_abstract_methods(self):
        """Test: BaseRepository tiene métodos abstractos que deben ser implementados"""
        class IncompleteRepository(BaseRepository):
            def create(self, entity):
                pass
            
            def get_by_id(self, entity_id):
                pass
        
        mock_session = MagicMock()
        
        with pytest.raises(TypeError):
            IncompleteRepository(mock_session)

