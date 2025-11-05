from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseModel(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate(self) -> None:
        pass


