"""
Tests para settings.py
"""
import pytest
from unittest.mock import patch
from app.config.settings import get_config, Config, DevelopmentConfig, ProductionConfig


class TestSettings:
    """Tests para settings.py"""
    
    def test_get_config_development(self):
        """Test: get_config retorna DevelopmentConfig por defecto"""
        with patch.dict('os.environ', {}, clear=True):
            with patch('os.getenv', side_effect=lambda key, default=None: 'development' if key == 'FLASK_ENV' else default):
                config = get_config()
                assert isinstance(config, DevelopmentConfig)
    
    @patch.dict('os.environ', {'FLASK_ENV': 'production'}, clear=False)
    def test_get_config_production(self):
        """Test: get_config retorna ProductionConfig cuando FLASK_ENV=production"""
        config = get_config()
        assert isinstance(config, ProductionConfig)
        assert config.DEBUG is False
    
    def test_config_default_values(self):
        """Test: Config tiene valores por defecto"""
        with patch('os.getenv', side_effect=lambda key, default=None: default):
            config = Config()
            assert config.DEBUG == True
            assert config.HOST == '0.0.0.0'
    
    def test_development_config(self):
        """Test: DevelopmentConfig tiene DEBUG=True"""
        config = DevelopmentConfig()
        assert config.DEBUG is True
    
    def test_production_config(self):
        """Test: ProductionConfig tiene DEBUG=False"""
        config = ProductionConfig()
        assert config.DEBUG is False

