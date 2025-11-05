from datetime import datetime, date
from typing import Dict, Any, Optional
from .base_model import BaseModel


class Route(BaseModel):
    def __init__(
        self,
        route_code: str,
        assigned_truck: str,
        delivery_date: date,
        orders_count: int = 0,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.route_code = route_code
        self.assigned_truck = assigned_truck
        self.delivery_date = delivery_date
        self.orders_count = orders_count
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'route_code': self.route_code,
            'assigned_truck': self.assigned_truck,
            'delivery_date': self.delivery_date.isoformat() if isinstance(self.delivery_date, date) else str(self.delivery_date),
            'orders_count': self.orders_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def validate(self) -> None:
        if not self.route_code:
            raise ValueError("El código de ruta es obligatorio")
        if not self.assigned_truck:
            raise ValueError("El camión asignado es obligatorio")
        if not self.delivery_date:
            raise ValueError("La fecha de entrega es obligatoria")
    
    @staticmethod
    def generate_route_code(sequence_number: int) -> str:
        return f"ROU-{sequence_number:04d}"


