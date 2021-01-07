
from abc import ABC, abstractmethod

class IotEntity(ABC):
    def __init__(self):
        self.id = None

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass

    @classmethod
    def from_dict(cls, cfg):
        instance = cls()
        instance.__dict__.update(cfg)
        return instance

