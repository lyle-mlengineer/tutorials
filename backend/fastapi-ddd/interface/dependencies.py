# interface/dependencies.py

from fastapi import Depends
from asyncpg import create_pool, Pool
from application.services import OrderService
from infrastructure.repositories import AsyncpgOrderRepository
from infrastructure.services import InventoryServiceImpl

async def get_pool() -> Pool:
    return await create_pool(
        user='postgres',
        password='postgres',
        database='postgres',
        host='localhost'
    )

async def get_order_service(
    pool: Pool = Depends(get_pool)
) -> OrderService:
    return OrderService(
        order_repository=AsyncpgOrderRepository(pool),
        inventory_service=InventoryServiceImpl()
    )
