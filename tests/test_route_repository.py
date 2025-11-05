"""
Tests para RouteRepository
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.route_repository import RouteRepository
from app.models.route import Route
from app.models.db_models import RouteDB


class TestRouteRepository:
    """Tests para RouteRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock de sesión de SQLAlchemy"""
        return MagicMock()
    
    @pytest.fixture
    def route_repository(self, mock_session):
        """Instancia de RouteRepository con sesión mockeada"""
        return RouteRepository(mock_session)
    
    @pytest.fixture
    def sample_route_db(self):
        """Mock de RouteDB con todos los atributos necesarios"""
        mock_route = MagicMock()
        mock_route.id = 1
        mock_route.route_code = "ROU-0001"
        mock_route.assigned_truck = "CAM-001"
        mock_route.delivery_date = date(2025, 12, 26)
        mock_route.orders_count = 5
        mock_route.created_at = datetime(2025, 1, 1, 10, 0, 0)
        mock_route.updated_at = datetime(2025, 1, 1, 11, 0, 0)
        return mock_route
    
    def test_db_to_model(self, route_repository, sample_route_db):
        """Test: Conversión de RouteDB a Route"""
        result = route_repository._db_to_model(sample_route_db)
        
        assert result.id == sample_route_db.id
        assert result.route_code == sample_route_db.route_code
        assert result.assigned_truck == sample_route_db.assigned_truck
        assert result.delivery_date == sample_route_db.delivery_date
        assert result.orders_count == sample_route_db.orders_count
        assert result.created_at == sample_route_db.created_at
        assert result.updated_at == sample_route_db.updated_at
    
    def test_create_success(self, route_repository, mock_session, sample_route_db):
        """Test: Crear ruta exitosamente"""
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        
        with patch.object(route_repository, 'create') as mock_create:
            mock_create.return_value = route
            
            result = route_repository.create(route)
            
            assert result == route
            mock_create.assert_called_once_with(route)
    
    def test_create_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en create"""
        route = Route(
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        
        with patch.object(route_repository, 'create') as mock_create:
            mock_create.side_effect = Exception("Error al crear ruta: Database error")
            
            with pytest.raises(Exception, match="Error al crear ruta: Database error"):
                route_repository.create(route)
            
            mock_create.assert_called_once_with(route)
    
    def test_get_by_id_success(self, route_repository, mock_session, sample_route_db):
        """Test: Obtener ruta por ID exitosamente"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        
        with patch.object(route_repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = route
            
            result = route_repository.get_by_id(1)
            
            assert result == route
            mock_get_by_id.assert_called_once_with(1)
    
    def test_get_by_id_not_found(self, route_repository, mock_session):
        """Test: Ruta no encontrada por ID"""
        with patch.object(route_repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = None
            
            result = route_repository.get_by_id(999)
            
            assert result is None
            mock_get_by_id.assert_called_once_with(999)
    
    def test_get_by_id_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en get_by_id"""
        with patch.object(route_repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.side_effect = Exception("Error al obtener ruta: Database error")
            
            with pytest.raises(Exception, match="Error al obtener ruta: Database error"):
                route_repository.get_by_id(1)
            
            mock_get_by_id.assert_called_once_with(1)
    
    def test_get_all_success(self, route_repository, mock_session, sample_route_db):
        """Test: Obtener todas las rutas exitosamente"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        
        with patch.object(route_repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = [route]
            
            result = route_repository.get_all()
            
            assert len(result) == 1
            assert result[0].id == 1
            mock_get_all.assert_called_once()
    
    def test_get_all_empty(self, route_repository, mock_session):
        """Test: Obtener todas las rutas cuando no hay ninguna"""
        with patch.object(route_repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = []
            
            result = route_repository.get_all()
            
            assert len(result) == 0
            mock_get_all.assert_called_once()
    
    def test_get_all_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en get_all"""
        with patch.object(route_repository, 'get_all') as mock_get_all:
            mock_get_all.side_effect = Exception("Error al obtener rutas: Database error")
            
            with pytest.raises(Exception, match="Error al obtener rutas: Database error"):
                route_repository.get_all()
            
            mock_get_all.assert_called_once()
    
    def test_get_routes_paginated_success(self, route_repository, mock_session, sample_route_db):
        """Test: Obtener rutas paginadas exitosamente"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        
        with patch.object(route_repository, 'get_routes_paginated') as mock_get_paginated:
            mock_get_paginated.return_value = [route]
            
            result = route_repository.get_routes_paginated(limit=10, offset=0)
            
            assert len(result) == 1
            assert result[0].id == 1
            mock_get_paginated.assert_called_once()
    
    def test_get_routes_paginated_with_filters(self, route_repository, mock_session, sample_route_db):
        """Test: Obtener rutas paginadas con filtros"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        
        with patch.object(route_repository, 'get_routes_paginated') as mock_get_paginated:
            mock_get_paginated.return_value = [route]
            
            result = route_repository.get_routes_paginated(
                limit=10,
                offset=0,
                route_code="ROU-0001",
                assigned_truck="CAM-001",
                delivery_date=date(2025, 12, 26)
            )
            
            assert len(result) == 1
            mock_get_paginated.assert_called_once()
    
    def test_get_routes_paginated_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en get_routes_paginated"""
        with patch.object(route_repository, 'get_routes_paginated') as mock_get_paginated:
            mock_get_paginated.side_effect = Exception("Error al obtener rutas paginadas: Database error")
            
            with pytest.raises(Exception, match="Error al obtener rutas paginadas: Database error"):
                route_repository.get_routes_paginated(limit=10, offset=0)
            
            mock_get_paginated.assert_called_once()
    
    def test_count_routes_success(self, route_repository, mock_session):
        """Test: Contar rutas exitosamente"""
        with patch.object(route_repository, 'count_routes') as mock_count:
            mock_count.return_value = 5
            
            result = route_repository.count_routes()
            
            assert result == 5
            mock_count.assert_called_once()
    
    def test_count_routes_with_filters(self, route_repository, mock_session):
        """Test: Contar rutas con filtros"""
        with patch.object(route_repository, 'count_routes') as mock_count:
            mock_count.return_value = 2
            
            result = route_repository.count_routes(
                route_code="ROU-0001",
                assigned_truck="CAM-001"
            )
            
            assert result == 2
            mock_count.assert_called_once()
    
    def test_count_routes_zero(self, route_repository, mock_session):
        """Test: Contar rutas cuando no hay ninguna"""
        with patch.object(route_repository, 'count_routes') as mock_count:
            mock_count.return_value = 0
            
            result = route_repository.count_routes()
            
            assert result == 0
            mock_count.assert_called_once()
    
    def test_count_routes_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en count_routes"""
        with patch.object(route_repository, 'count_routes') as mock_count:
            mock_count.side_effect = Exception("Error al contar rutas: Database error")
            
            with pytest.raises(Exception, match="Error al contar rutas: Database error"):
                route_repository.count_routes()
            
            mock_count.assert_called_once()
    
    def test_get_route_by_truck_and_date_success(self, route_repository, mock_session, sample_route_db):
        """Test: Obtener ruta por camión y fecha exitosamente"""
        route = Route(
            id=1,
            route_code="ROU-0001",
            assigned_truck="CAM-001",
            delivery_date=date(2025, 12, 26),
            orders_count=5
        )
        
        with patch.object(route_repository, 'get_route_by_truck_and_date') as mock_get:
            mock_get.return_value = route
            
            result = route_repository.get_route_by_truck_and_date("CAM-001", date(2025, 12, 26))
            
            assert result == route
            mock_get.assert_called_once()
    
    def test_get_route_by_truck_and_date_not_found(self, route_repository, mock_session):
        """Test: Ruta no encontrada por camión y fecha"""
        with patch.object(route_repository, 'get_route_by_truck_and_date') as mock_get:
            mock_get.return_value = None
            
            result = route_repository.get_route_by_truck_and_date("CAM-999", date(2025, 12, 26))
            
            assert result is None
            mock_get.assert_called_once()
    
    def test_get_route_by_truck_and_date_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en get_route_by_truck_and_date"""
        with patch.object(route_repository, 'get_route_by_truck_and_date') as mock_get:
            mock_get.side_effect = Exception("Error al obtener ruta por camión y fecha: Database error")
            
            with pytest.raises(Exception, match="Error al obtener ruta por camión y fecha: Database error"):
                route_repository.get_route_by_truck_and_date("CAM-001", date(2025, 12, 26))
            
            mock_get.assert_called_once()
    
    def test_get_next_sequence_number_first(self, route_repository, mock_session):
        """Test: Obtener siguiente número de secuencia cuando no hay rutas"""
        with patch.object(route_repository, 'get_next_sequence_number') as mock_get_next:
            mock_get_next.return_value = 1
            
            result = route_repository.get_next_sequence_number()
            
            assert result == 1
            mock_get_next.assert_called_once()
    
    def test_get_next_sequence_number_incremental(self, route_repository, mock_session):
        """Test: Obtener siguiente número de secuencia incremental"""
        with patch.object(route_repository, 'get_next_sequence_number') as mock_get_next:
            mock_get_next.return_value = 6
            
            result = route_repository.get_next_sequence_number()
            
            assert result == 6
            mock_get_next.assert_called_once()
    
    def test_get_next_sequence_number_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en get_next_sequence_number"""
        with patch.object(route_repository, 'get_next_sequence_number') as mock_get_next:
            mock_get_next.side_effect = Exception("Error al obtener siguiente número de secuencia: Database error")
            
            with pytest.raises(Exception, match="Error al obtener siguiente número de secuencia: Database error"):
                route_repository.get_next_sequence_number()
            
            mock_get_next.assert_called_once()
    
    def test_update_success(self, route_repository, mock_session, sample_route_db):
        """Test: Actualizar ruta exitosamente"""
        route = Route(
            id=1,
            route_code="ROU-0002",
            assigned_truck="CAM-002",
            delivery_date=date(2025, 12, 27),
            orders_count=10
        )
        
        with patch.object(route_repository, 'update') as mock_update:
            mock_update.return_value = route
            
            result = route_repository.update(route)
            
            assert result == route
            mock_update.assert_called_once_with(route)
    
    def test_update_not_found(self, route_repository, mock_session):
        """Test: Error al actualizar ruta no encontrada"""
        route = Route(
            id=999,
            route_code="ROU-0002",
            assigned_truck="CAM-002",
            delivery_date=date(2025, 12, 27),
            orders_count=10
        )
        
        with patch.object(route_repository, 'update') as mock_update:
            mock_update.side_effect = Exception("Ruta no encontrada")
            
            with pytest.raises(Exception, match="Ruta no encontrada"):
                route_repository.update(route)
            
            mock_update.assert_called_once_with(route)
    
    def test_update_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en update"""
        route = Route(
            id=1,
            route_code="ROU-0002",
            assigned_truck="CAM-002",
            delivery_date=date(2025, 12, 27),
            orders_count=10
        )
        
        with patch.object(route_repository, 'update') as mock_update:
            mock_update.side_effect = Exception("Error al actualizar ruta: Database error")
            
            with pytest.raises(Exception, match="Error al actualizar ruta: Database error"):
                route_repository.update(route)
            
            mock_update.assert_called_once_with(route)
    
    def test_delete_success(self, route_repository, mock_session, sample_route_db):
        """Test: Eliminar ruta exitosamente"""
        with patch.object(route_repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            result = route_repository.delete(1)
            
            assert result is True
            mock_delete.assert_called_once_with(1)
    
    def test_delete_not_found(self, route_repository, mock_session):
        """Test: Eliminar ruta no encontrada"""
        with patch.object(route_repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            result = route_repository.delete(999)
            
            assert result is False
            mock_delete.assert_called_once_with(999)
    
    def test_delete_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en delete"""
        with patch.object(route_repository, 'delete') as mock_delete:
            mock_delete.side_effect = Exception("Error al eliminar ruta: Database error")
            
            with pytest.raises(Exception, match="Error al eliminar ruta: Database error"):
                route_repository.delete(1)
            
            mock_delete.assert_called_once_with(1)
    
    def test_delete_all_success(self, route_repository, mock_session):
        """Test: Eliminar todas las rutas exitosamente"""
        with patch.object(route_repository, 'delete_all') as mock_delete_all:
            mock_delete_all.return_value = 5
            
            result = route_repository.delete_all()
            
            assert result == 5
            mock_delete_all.assert_called_once()
    
    def test_delete_all_empty(self, route_repository, mock_session):
        """Test: Eliminar todas las rutas cuando no hay ninguna"""
        with patch.object(route_repository, 'delete_all') as mock_delete_all:
            mock_delete_all.return_value = 0
            
            result = route_repository.delete_all()
            
            assert result == 0
            mock_delete_all.assert_called_once()
    
    def test_delete_all_database_error(self, route_repository, mock_session):
        """Test: Error de base de datos en delete_all"""
        with patch.object(route_repository, 'delete_all') as mock_delete_all:
            mock_delete_all.side_effect = Exception("Error al eliminar todas las rutas: Database error")
            
            with pytest.raises(Exception, match="Error al eliminar todas las rutas: Database error"):
                route_repository.delete_all()
            
            mock_delete_all.assert_called_once()
