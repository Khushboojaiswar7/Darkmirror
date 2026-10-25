from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.analysis import AgentOutput

class BaseDetectorAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    async def analyze(self, messages: List[Dict[str, Any]], **kwargs) -> AgentOutput:
        pass

    def get_config(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description
        }
