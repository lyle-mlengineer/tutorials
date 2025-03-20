# application/services/order.py

from typing import List
from uuid import UUID

from domain.models.order import Order, OrderItem
from domain.repositories.order import OrderRepository
from domain.services.inventory import InventoryService


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        inventory_service: InventoryService
    ):
        self._order_repository = order_repository
        self._inventory_service = inventory_service

    async def create_order(
        self,
        customer_id: UUID,
        items: List[OrderItem]
    ) -> Order:
        # Reserve inventory
        for item in items:
            await self._inventory_service.reserve(
                item.product_id,
                item.quantity
            )
        # Create and save order
        order = Order(customer_id=customer_id, items=items)
        await self._order_repository.save(order)
        return order