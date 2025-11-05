"""
Tests para BaseModel
"""
import pytest
from app.models.base_model import BaseModel


class TestBaseModel:
    """Tests para BaseModel"""
    
    def test_base_model_has_to_dict_method(self):
        """Test: BaseModel tiene método to_dict"""
        class TestModel(BaseModel):
            def __init__(self):
                self.id = 1
                self.name = "Test"
            
            def to_dict(self):
                return {'id': self.id, 'name': self.name}
            
            def validate(self):
                pass
        
        model = TestModel()
        assert hasattr(model, 'to_dict')
        assert model.to_dict() == {'id': 1, 'name': 'Test'}
    
    def test_base_model_has_validate_method(self):
        """Test: BaseModel tiene método validate"""
        class TestModel(BaseModel):
            def __init__(self):
                self.name = None
            
            def to_dict(self):
                return {'name': self.name}
            
            def validate(self):
                if not self.name:
                    raise ValueError("Name is required")
        
        model = TestModel()
        model.name = "Test"
        model.validate()
        
        model.name = None
        with pytest.raises(ValueError):
            model.validate()
    
    def test_base_model_abstract_methods_must_be_implemented(self):
        """Test: BaseModel requiere implementación de métodos abstractos"""
        class IncompleteModel(BaseModel):
            def to_dict(self):
                pass
        
        with pytest.raises(TypeError):
            IncompleteModel()

