"""
Tests para el modelo Route
"""
import pytest
from datetime import datetime, date
from app.models.route import Route


class TestRoute:
    """Tests para el modelo Route"""
    
    def test_route_creation(self):
        """Test: Creación de ruta con todos los campos"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date,
            orders_count=5,
            id=1
        )
        
        assert route.id == 1
        assert route.route_code == "ROU-0001"
        assert route.assigned_truck == "CAM-001"
        assert route.delivery_date == delivery_date
        assert route.orders_count == 5
        assert route.created_at is not None
        assert route.updated_at is not None
    
    def test_route_creation_with_datetime(self):
        """Test: Creación de ruta con created_at y updated_at personalizados"""
        created_at = datetime(2025, 1, 1, 10, 0, 0)
        updated_at = datetime(2025, 1, 1, 11, 0, 0)
        delivery_date = date(2025, 12, 26)
        
        route = Route(
            route_code="ROU-0002",
            assigned_truck="CAM-002",
            delivery_date=delivery_date,
            orders_count=3,
            id=2,
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert route.created_at == created_at
        assert route.updated_at == updated_at
    
    def test_route_validate_success(self):
        """Test: Validación exitosa de ruta"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date,
            orders_count=5
        )
        
        route.validate()
    
    def test_route_validate_empty_route_code(self):
        """Test: Error al validar ruta con route_code vacío"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code="",
            assigned_truck="CAM-001",
            delivery_date=delivery_date
        )
        
        with pytest.raises(ValueError, match="El código de ruta es obligatorio"):
            route.validate()
    
    def test_route_validate_none_route_code(self):
        """Test: Error al validar ruta con route_code None"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code=None,
            assigned_truck="CAM-001",
            delivery_date=delivery_date
        )
        
        with pytest.raises(ValueError, match="El código de ruta es obligatorio"):
            route.validate()
    
    def test_route_validate_empty_assigned_truck(self):
        """Test: Error al validar ruta con assigned_truck vacío"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code="ROU-0001",
            assigned_truck="",
            delivery_date=delivery_date
        )
        
        with pytest.raises(ValueError, match="El camión asignado es obligatorio"):
            route.validate()
    
    def test_route_validate_none_assigned_truck(self):
        """Test: Error al validar ruta con assigned_truck None"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code="ROU-0001",
            assigned_truck=None,
            delivery_date=delivery_date
        )
        
        with pytest.raises(ValueError, match="El camión asignado es obligatorio"):
            route.validate()
    
    def test_route_validate_none_delivery_date(self):
        """Test: Error al validar ruta con delivery_date None"""
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=None
        )
        
        with pytest.raises(ValueError, match="La fecha de entrega es obligatoria"):
            route.validate()
    
    def test_route_to_dict(self):
        """Test: Conversión de ruta a diccionario"""
        delivery_date = date(2025, 12, 26)
        created_at = datetime(2025, 1, 1, 10, 0, 0)
        updated_at = datetime(2025, 1, 1, 11, 0, 0)
        
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date,
            orders_count=5,
            id=1,
            created_at=created_at,
            updated_at=updated_at
        )
        
        result = route.to_dict()
        
        assert result['id'] == 1
        assert result['route_code'] == "ROU-0001"
        assert result['assigned_truck'] == "CAM-001"
        assert result['delivery_date'] == "2025-12-26"
        assert result['orders_count'] == 5
        assert result['created_at'] == "2025-01-01T10:00:00"
        assert result['updated_at'] == "2025-01-01T11:00:00"
    
    def test_route_to_dict_with_none_dates(self):
        """Test: Conversión de ruta a diccionario con fechas None (se asignan automáticamente)"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date,
            orders_count=5,
            id=1
        )
        
        result = route.to_dict()
        
        assert result['created_at'] is not None
        assert result['updated_at'] is not None
        assert isinstance(result['created_at'], str)
        assert isinstance(result['updated_at'], str)
    
    def test_generate_route_code(self):
        """Test: Generación de código de ruta"""
        code1 = Route.generate_route_code(1)
        code2 = Route.generate_route_code(10)
        code3 = Route.generate_route_code(100)
        code4 = Route.generate_route_code(1000)
        
        assert code1 == "ROU-0001"
        assert code2 == "ROU-0010"
        assert code3 == "ROU-0100"
        assert code4 == "ROU-1000"
    
    def test_generate_route_code_zero_padding(self):
        """Test: Generación de código de ruta con padding de ceros"""
        code = Route.generate_route_code(42)
        assert code == "ROU-0042"
    
    def test_route_orders_count_default(self):
        """Test: Valor por defecto de orders_count"""
        delivery_date = date(2025, 12, 26)
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=delivery_date
        )
        
        assert route.orders_count == 0

