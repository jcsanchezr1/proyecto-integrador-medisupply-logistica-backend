import pytest
from unittest.mock import patch, MagicMock
import sys

def pytest_configure(config):
    mock_requests = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'id': 1,
        'name': 'Producto Test',
        'photo_url': 'https://example.com/test.jpg',
        'price': 100.0
    }
    mock_response.status_code = 200
    mock_requests.get.return_value = mock_response
    mock_requests.exceptions.RequestException = Exception
    
    mock_session = MagicMock()
    mock_session.query.return_value = mock_session
    mock_session.filter.return_value = mock_session
    mock_session.all.return_value = []
    mock_session.first.return_value = None
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    
    mock_engine = MagicMock()
    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session
    
    mock_sqlalchemy_exceptions = MagicMock()
    mock_sqlalchemy_exceptions.SQLAlchemyError = Exception
    mock_sqlalchemy_exceptions.IntegrityError = Exception
    
    sys.modules['requests'] = mock_requests
    
    mock_sqlalchemy = MagicMock()
    mock_sqlalchemy.ext = MagicMock()
    mock_sqlalchemy.ext.declarative = MagicMock()
    mock_sqlalchemy.ext.declarative.declarative_base = MagicMock()
    mock_sqlalchemy.orm = MagicMock()
    mock_sqlalchemy.orm.sessionmaker = mock_sessionmaker
    mock_sqlalchemy.orm.Session = mock_session
    mock_sqlalchemy.exc = mock_sqlalchemy_exceptions
    mock_sqlalchemy.engine = MagicMock()
    mock_sqlalchemy.engine.create_engine = MagicMock(return_value=mock_engine)
    mock_sqlalchemy.Column = MagicMock()
    mock_sqlalchemy.Integer = MagicMock()
    mock_sqlalchemy.String = MagicMock()
    mock_sqlalchemy.DateTime = MagicMock()
    mock_sqlalchemy.Float = MagicMock()
    mock_sqlalchemy.ForeignKey = MagicMock()
    mock_sqlalchemy.Enum = MagicMock()
    mock_sqlalchemy.relationship = MagicMock()
    mock_sqlalchemy.cascade = MagicMock()
    
    sys.modules['sqlalchemy'] = mock_sqlalchemy
    sys.modules['sqlalchemy.ext'] = mock_sqlalchemy.ext
    sys.modules['sqlalchemy.ext.declarative'] = mock_sqlalchemy.ext.declarative
    sys.modules['sqlalchemy.orm'] = mock_sqlalchemy.orm
    sys.modules['sqlalchemy.exc'] = mock_sqlalchemy.exc
    sys.modules['sqlalchemy.engine'] = mock_sqlalchemy.engine


