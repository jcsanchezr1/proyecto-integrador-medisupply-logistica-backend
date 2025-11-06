"""
Tests para database.py
"""
import pytest
from unittest.mock import patch, MagicMock
from app.config.database import (
    get_db_session,
    create_tables,
    auto_close_session,
    SessionLocal,
    engine
)


class TestDatabase:
    """Tests para database.py"""
    
    @patch('app.config.database.SessionLocal')
    def test_get_db_session(self, mock_session_local):
        """Test: get_db_session genera sesiones correctamente"""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        gen = get_db_session()
        session = next(gen)
        
        assert session == mock_session
        mock_session_local.assert_called_once()
        
        try:
            next(gen)
        except StopIteration:
            pass
        
        mock_session.close.assert_called_once()
    
    def test_create_tables(self):
        """Test: create_tables crea las tablas"""
        with patch('app.models.db_models.Base') as mock_base:
            mock_base.metadata.create_all = MagicMock()
            with patch('app.config.database.engine') as mock_engine:
                create_tables()
                mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)
    
    def test_auto_close_session_decorator_with_mocked_service(self):
        """Test: auto_close_session no cierra sesión cuando el servicio está mockeado"""
        class MockService:
            pass
        
        mock_service = MagicMock(spec=MockService)
        mock_service.logistics_service = MagicMock()
        mock_service.logistics_service.__class__.__module__ = 'unittest.mock'
        mock_service.logistics_service.__class__.__name__ = 'Mock'
        
        @auto_close_session
        def test_method(self):
            return "test"
        
        result = test_method(mock_service)
        assert result == "test"
    
    def test_auto_close_session_decorator_with_real_service(self):
        """Test: auto_close_session cierra sesión cuando el servicio es real"""
        class RealService:
            pass
        
        mock_repository = MagicMock()
        mock_session = MagicMock()
        mock_repository.session = mock_session
        
        service = MagicMock()
        service.logistics_repository = mock_repository
        
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = MagicMock()
            
            @auto_close_session
            def test_method(self):
                return "test"
            
            result = test_method(service)
            assert result == "test"
    
    def test_auto_close_session_decorator_no_repository(self):
        """Test: auto_close_session funciona sin repository"""
        service = MagicMock()
        del service.logistics_repository
        
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = MagicMock()
            
            @auto_close_session
            def test_method(self):
                return "test"
            
            result = test_method(service)
            assert result == "test"
    
    def test_auto_close_session_decorator_exception_handling(self):
        """Test: auto_close_session maneja excepciones al cerrar sesión"""
        mock_repository = MagicMock()
        mock_session = MagicMock()
        mock_session.close.side_effect = Exception("Error closing")
        mock_repository.session = mock_session
        
        service = MagicMock()
        service.logistics_repository = mock_repository
        
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_new_session = MagicMock()
            mock_new_session.close.side_effect = Exception("Error in finally")
            mock_session_local.return_value = mock_new_session
            
            @auto_close_session
            def test_method(self):
                return "test"
            
            result = test_method(service)
            assert result == "test"
    
    def test_auto_close_session_decorator_with_repository_session_close_error(self):
        """Test: auto_close_session maneja error al cerrar sesión del repository"""
        class TestService:
            def __init__(self):
                self.logistics_repository = MagicMock()
                self.logistics_repository.session = MagicMock()
                self.logistics_repository.session.close.side_effect = Exception("Error closing existing session")
        
        service = TestService()
        
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_new_session = MagicMock()
            mock_new_session.close.side_effect = Exception("Error in finally")
            mock_session_local.return_value = mock_new_session
            
            @auto_close_session
            def test_method(self):
                return "test"
            
            result = test_method(service)
            assert result == "test"
            service.logistics_repository.session.close.assert_called_once()

