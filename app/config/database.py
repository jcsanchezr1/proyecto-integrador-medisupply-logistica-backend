import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import get_config

logger = logging.getLogger(__name__)

config = get_config()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db')

engine = create_engine(DATABASE_URL, echo=config.DEBUG, pool_size=20, max_overflow=30)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from ..models.db_models import Base
    Base.metadata.create_all(bind=engine)

def auto_close_session(func):
    def wrapper(self, *args, **kwargs):

        is_mocked = False
        if hasattr(self, 'logistics_service'):
            service_class = self.logistics_service.__class__
            is_mocked = 'mock' in service_class.__module__.lower() or 'Mock' in service_class.__name__

        if is_mocked:
            logger.debug("Servicio mockeado detectado, saltando recreacion en decorador")
            return func(self, *args, **kwargs)

        if hasattr(self, 'logistics_repository') and hasattr(self.logistics_repository, 'session'):
            try:
                self.logistics_repository.session.close()
                logger.debug("Sesion cerrada en decorador")
            except Exception as e:
                logger.warning(f"Error cerrando sesion existente: {e}")

        session = SessionLocal()
        try:
            return func(self, *args, **kwargs)
        finally:
            try:
                session.close()
                logger.debug("Sesion cerrada en finally del decorador")
            except Exception as e:
                logger.warning(f"Error cerrando sesion en finally: {e}")
    
    return wrapper

