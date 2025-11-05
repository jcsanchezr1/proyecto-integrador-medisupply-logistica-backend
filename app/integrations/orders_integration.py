import os
import requests
import logging
from typing import List, Dict, Any
from datetime import date

logger = logging.getLogger(__name__)


class OrdersIntegration:
    def __init__(self):
        self.orders_service_url = os.getenv('ORDERS_SERVICE_URL', 'http://pedidos:8080')
    
    def get_orders_by_truck_and_date(self, truck: str, delivery_date: date) -> List[Dict[str, Any]]:
        try:
            url = f"{self.orders_service_url}/orders/by-truck"
            params = {
                'assigned_truck': truck,
                'scheduled_delivery_date': delivery_date.isoformat()
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    return data['data']
                return []
            elif response.status_code == 404:
                return []
            else:
                logger.warning(f"Error al consultar pedidos: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con servicio de pedidos: {str(e)}")
            raise Exception(f"Error al consultar servicio de pedidos: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado al consultar pedidos: {str(e)}")
            raise Exception(f"Error al consultar servicio de pedidos: {str(e)}")
    
    def has_orders_for_truck_and_date(self, truck: str, delivery_date: date) -> bool:
        orders = self.get_orders_by_truck_and_date(truck, delivery_date)
        return len(orders) > 0

