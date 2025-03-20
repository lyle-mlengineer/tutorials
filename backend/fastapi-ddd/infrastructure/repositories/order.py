# infrastructure/repositories/order.py

import logging
from asyncpg import Pool
from asyncpg.exceptions import PostgresError
from domain.models.order import Order
from domain.repositories.order import OrderRepository
from domain.vo import Money, OrderStatus
from exceptions import OrderCreationError


logger = logging.getLogger(__name__)


class AsyncpgOrderRepository(OrderRepository):
    def __init__(self, pool: Pool):
        self._pool = pool

    async def save(self, order: Order) -> None:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    order_id = await conn.fetchval('''
                        INSERT INTO orders (
                            customer_id, status
                        ) VALUES ($1, $2)
                        RETURNING id
                    ''', str(order.customer_id),
                        order.status.value)
                except PostgresError as e:
                    logger.exception("Failed to create order")
                    raise OrderCreationError("Failed to create order")
                try:
                    await conn.executemany('''
                        INSERT INTO order_items (
                            order_id, product_id, quantity, unit_price
                        ) VALUES ($1, $2, $3, $4)
                    ''', [(
                        order_id,
                        str(item.product_id),
                        item.quantity,
                        int(item.unit_price * 100)  # Convert dollars to cents
                    ) for item in order.items])
                except PostgresError as e:
                    logger.exception("Failed to create order items")
                    raise OrderCreationError("Failed to create order items")
                order.id = order_id