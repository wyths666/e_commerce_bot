from datetime import datetime
from pydantic import BaseModel

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float
    total: float = None

    def __init__(self, **data):
        super().__init__(**data)
        self.total = self.quantity * self.price


class OrderResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_amount: float
    customer_name: str
    customer_phone: str
    customer_address: str
    delivery_method: str
    order_number: str
    items: list[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: str


class UpdateStatusRequest(BaseModel):
    order_id: int
    new_status: str


