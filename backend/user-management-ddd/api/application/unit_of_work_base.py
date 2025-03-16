from abc import ABC, abstractmethod


class UnitOfWorkBase(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        pass
