# interface/api/orders.py

from fastapi import APIRouter, Depends, HTTPException
from application.services import OrderService
from domain.models.order import OrderItem
from exceptions import (
    InsufficientItemsError,
    InvalidOrderDataError,
    OrderCreationError
)
from interface.dependencies import get_order_service
from interface.schemas import CreateOrderRequest, OrderResponse


router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    order_service: OrderService = Depends(get_order_service)
):
    try:
        order = await order_service.create_order(
            customer_id=request.customer_id,
            items=[
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                for item in request.items
            ]
        )
        return OrderResponse.parse_obj(order)
    except InsufficientItemsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidOrderDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OrderCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))