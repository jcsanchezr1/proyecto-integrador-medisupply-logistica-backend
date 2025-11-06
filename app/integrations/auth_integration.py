import os
import requests
import logging
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)


class AuthIntegration:
    def __init__(self):
        self.auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://autenticador:8080')
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        try:
            url = f"{self.auth_service_url}/auth/user/{user_id}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Usuario obtenido exitosamente' and data.get('data'):
                    return data['data']
                elif data.get('success') and data.get('data'):
                    return data['data']
                return None
            elif response.status_code == 404:
                return None
            else:
                logger.warning(f"Error al consultar usuario: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con servicio de autenticador: {str(e)}")
            raise Exception(f"Error al consultar servicio de autenticador: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado al consultar usuario: {str(e)}")
            raise Exception(f"Error al consultar servicio de autenticador: {str(e)}")
    
    def get_users_by_ids(self, user_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        users_dict = {}
        unique_ids = list(set(user_ids))
        
        for user_id in unique_ids:
            try:
                user = self.get_user_by_id(user_id)
                if user:
                    users_dict[user_id] = user
            except Exception as e:
                logger.warning(f"Error al obtener usuario {user_id}: {str(e)}")
                continue
        
        return users_dict

