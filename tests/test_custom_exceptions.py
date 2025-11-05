"""
Tests para custom_exceptions
"""
import pytest
from app.exceptions.custom_exceptions import (
    LogisticsException,
    LogisticsNotFoundError,
    LogisticsValidationError,
    LogisticsBusinessLogicError
)


class TestCustomExceptions:
    """Tests para las excepciones personalizadas"""
    
    def test_logistics_exception(self):
        """Test: LogisticsException es una excepción"""
        with pytest.raises(LogisticsException):
            raise LogisticsException("Test error")
    
    def test_logistics_not_found_error(self):
        """Test: LogisticsNotFoundError hereda de LogisticsException"""
        with pytest.raises(LogisticsNotFoundError):
            raise LogisticsNotFoundError("Not found")
        
        assert issubclass(LogisticsNotFoundError, LogisticsException)
    
    def test_logistics_validation_error(self):
        """Test: LogisticsValidationError hereda de LogisticsException"""
        with pytest.raises(LogisticsValidationError):
            raise LogisticsValidationError("Validation error")
        
        assert issubclass(LogisticsValidationError, LogisticsException)
    
    def test_logistics_business_logic_error(self):
        """Test: LogisticsBusinessLogicError hereda de LogisticsException"""
        with pytest.raises(LogisticsBusinessLogicError):
            raise LogisticsBusinessLogicError("Business logic error")
        
        assert issubclass(LogisticsBusinessLogicError, LogisticsException)
    
    def test_exception_message(self):
        """Test: Las excepciones pueden tener mensajes"""
        try:
            raise LogisticsValidationError("Custom message")
        except LogisticsValidationError as e:
            assert str(e) == "Custom message"
    
    def test_exception_inheritance_chain(self):
        """Test: Cadena de herencia de excepciones"""
        assert issubclass(LogisticsNotFoundError, LogisticsException)
        assert issubclass(LogisticsValidationError, LogisticsException)
        assert issubclass(LogisticsBusinessLogicError, LogisticsException)
        assert issubclass(LogisticsException, Exception)

