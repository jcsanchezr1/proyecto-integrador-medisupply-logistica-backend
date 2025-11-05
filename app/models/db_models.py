from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class RouteDB(Base):
    __tablename__ = 'routes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    route_code = Column(String(20), unique=True, nullable=False)
    assigned_truck = Column(String(20), nullable=False)
    delivery_date = Column(Date, nullable=False)
    orders_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
