from fastapi import APIRouter, Depends, HTTPException, Query, Form
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import joinedload
from api.models.order import OrderResponse,  UpdateStatusRequest
from database.crud import get_all_orders
from database.db_helper import get_db
from database.models import Order, OrderItem

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/orders/", response_model=list[OrderResponse])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    orders = get_all_orders(db)
    return orders[skip:skip + limit]



templates = Jinja2Templates(directory="templates")

@router.get("/orders-page/", response_class=HTMLResponse, name="orders_page")
async def get_orders_page(
    request: Request,
    date_from: str = Query(None),
    date_to: str = Query(None),
    status: str = Query(None)
):
    db_gen = get_db()
    db: Session = next(db_gen)

    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)  # ← загружаем товары
    )

    # Фильтр по дате "от"
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Order.created_at >= date_from_obj)
        except ValueError:
            pass

    # Фильтр по дате "до"
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= date_to_obj)
        except ValueError:
            pass

    # Фильтр по статусу
    if status:
        query = query.filter(Order.status == status)

    # Сортировка
    query = query.order_by(Order.created_at.desc())
    orders = query.all()

    # Добавляем названия товаров
    for order in orders:
        for item in order.items:
            if hasattr(item, 'product') and item.product:
                item.product_name = item.product.name
            else:
                item.product_name = "Товар не найден"

    context = {
        "request": request,
        "orders": orders,
        "date_from": date_from,
        "date_to": date_to,
        "status": status
    }

    return templates.TemplateResponse("orders.html", context)


@router.get("/orders-page/user-orders/", response_class=HTMLResponse)
def get_user_orders(
        request: Request,
        user_id: int = Query(None, description="ID пользователя"),
        date_from: str = Query(None),
        date_to: str = Query(None),
        status: str = Query(None),
        db: Session = Depends(get_db)
):
    # Начинаем строить запрос с загрузкой связанных данных
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)  # ← загружаем товары
    )

    # Фильтр по пользователю (если указан)
    if user_id:
        query = query.filter(Order.user_id == user_id)

    # Фильтр по дате "от"
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Order.created_at >= date_from_obj)
        except ValueError:
            pass

    # Фильтр по дате "до"
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= date_to_obj)
        except ValueError:
            pass

    # Фильтр по статусу
    if status:
        query = query.filter(Order.status == status)

    # Сортировка
    orders = query.order_by(Order.created_at.desc()).all()

    # Добавляем названия товаров к каждому item
    for order in orders:
        for item in order.items:
            if hasattr(item, 'product') and item.product:
                item.product_name = item.product.name
            else:
                item.product_name = "Товар не найден"

    return templates.TemplateResponse("orders.html", {
        "request": request,
        "orders": orders,
        "date_from": date_from,
        "date_to": date_to,
        "status": status
    })


@router.post("/update-status-json", name="update_order_status_json")
async def update_order_status_json(
    request: Request,
    data: UpdateStatusRequest,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    valid_statuses = ["new", "confirmed", "cancelled", "delivered"]
    if data.new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Недопустимый статус: {data.new_status}")

    order.status = data.new_status
    db.commit()
    db.refresh(order)

    return {"status": "ok", "new_status": data.new_status}