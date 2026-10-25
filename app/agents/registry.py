from typing import Dict, Type
from app.agents.base import BaseDetectorAgent

class AgentRegistry:
    _instance = None
    _agents: Dict[str, Type[BaseDetectorAgent]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
        return cls._instance

    def register(self, name: str, agent_class: Type[BaseDetectorAgent]):
        self._agents[name] = agent_class

    def get(self, name: str) -> BaseDetectorAgent:
        if name not in self._agents:
            raise ValueError(f"Agent {name} not found")
        return self._agents[name]()

    def list_agents(self) -> list:
        return [agent().get_config() for agent in self._agents.values()]

registry = AgentRegistry()

def register_detector(name: str):
    def decorator(cls):
        registry.register(name, cls)
        return cls
    return decorator
