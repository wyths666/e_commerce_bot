from sqlalchemy.orm import Session
from . import models
import uuid
from datetime import datetime

from .models import OrderItem, Order


# === Категории ===
def get_categories(db: Session):
    return db.query(models.Category).all()

def get_category_by_id(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

# === Товары ===
def get_products_by_category(db: Session, category_id: int):
    return db.query(models.Product).filter(models.Product.category_id == category_id).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

# === Корзина ===
def get_cart_items(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1):
    # Проверяем, есть ли уже такой товар в корзине
    item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id
    ).first()
    if item:
        item.quantity += quantity
    else:
        item = models.CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(item)
    db.commit()
    db.refresh(item)
    return item

def update_cart_item_quantity(db: Session, cart_item_id: int, quantity: int):
    item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if item and quantity > 0:
        item.quantity = quantity
        db.commit()
        return item
    elif item and quantity == 0:
        db.delete(item)
        db.commit()
    return None

def remove_from_cart(db: Session, cart_item_id: int):
    item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if item:
        db.delete(item)
        db.commit()

def clear_cart(db: Session, user_id: int):
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()

# === Заказы ===
def create_order(db: Session, user_id: int, total_amount: float, customer_name: str,
                 customer_phone: str, customer_address: str, delivery_method: str, items_data: list):
    # Генерируем уникальный номер заказа
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    # Создаём заказ
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_address=customer_address,
        delivery_method=delivery_method,
        order_number=order_number
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # ✅ Создаём связи между заказом и товарами
    for item_data in items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.add(order_item)

    db.commit()
    return order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def get_all_orders(db: Session):
    return db.query(models.Order).all()

def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
        return order
    return None

def get_user_profile(db: Session, user_id: int):
    return db.query(models.Profile).filter(models.Profile.user_id == user_id).first()


def get_order_with_items(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()

    if order:
        # Получаем товары в заказе
        items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        return {
            "order": order,
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.price_at_time,
                    "total": item.quantity * item.price_at_time
                }
                for item in items
            ]
        }
    return None

def user_cancel_order(db: Session, order_id: int, status: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None

    if status == "new":
        order.status = "cancelled"
        db.commit()
        db.refresh(order)  # ✅ Обновляем объект
        return order
    else:
        return None

def update_product(db: Session, product_id: int, **kwargs):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
        db.commit()
        return product
    return None

def get_all_users(db: Session):
    return db.query(models.Profile).all()

def get_order_with_details(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def format_orders_with_product_names(db: Session, orders):
    for order in orders:
        for item in order.items:
            product = get_product_by_id(db, item.product_id)
            item.product_name = product.name if product else "Неизвестный товар"
    return orders