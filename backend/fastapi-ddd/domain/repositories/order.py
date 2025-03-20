# domain/repositories/order.py

from abc import ABC, abstractmethod

from domain.models.order import Order


class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None:
        pass