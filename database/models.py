from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")

class Profile(Base):
    __tablename__ = 'users_profile'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Telegram user ID (уникальный)
    user_name = Column(String(100))
    user_phone = Column(String(20))
    user_address = Column(String(300))

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    photo_url = Column(String(300))  # Можно URL или путь к файлу
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Telegram user ID
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)

    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))
    status = Column(String(50), default="new")  # new / confirmed / delivered / cancelled
    total_amount = Column(Float, nullable=False)
    customer_name = Column(String(100))
    customer_phone = Column(String(20))
    customer_address = Column(String(300))
    delivery_method = Column(String(50))
    order_number = Column(String(20), unique=True, nullable=False)
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Float, nullable=False)  # Цена товара на момент заказа

    order = relationship("Order", back_populates="items")
    product = relationship("Product")