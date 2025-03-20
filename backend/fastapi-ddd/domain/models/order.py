# domain/models/order.py

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from domain.vo import Money, OrderStatus
from exceptions import InvalidOrderDataError


class OrderItem(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)
    unit_price: Money
    
    def calculate_subtotal(self) -> Money:
        return self.unit_price * self.quantity

class Order(BaseModel):
    id: int | None = None
    customer_id: UUID
    items: List[OrderItem]
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    created_at: datetime | None = None

    def calculate_total(self) -> Money:
        return sum((item.calculate_subtotal() for item in self.items),
                  start=Money(0))

    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)

    def submit(self) -> None:
        if not self.items:
            raise InvalidOrderDataError("Cannot submit empty order")
        self.status = OrderStatus.SUBMITTED

    @model_validator(mode='after')
    def validate_items(self) -> 'Order':
        if not self.items:
            raise InvalidOrderDataError("Order must have at least one item")
        return self