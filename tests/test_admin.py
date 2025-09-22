import pytest
from database.crud import get_all_orders, update_order_status, get_categories, add_to_cart
from database.models import Product, Category, Order, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


@pytest.fixture
def db_session():
    # Создаём временную БД для тестов
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Добавляем тестовые данные
    category = Category(name="Тестовая категория")
    db.add(category)
    db.commit()

    product = Product(
        name="Тестовый товар",
        description="Описание",
        price=100.0,
        category_id=category.id
    )
    db.add(product)
    db.commit()

    yield db
    db.close()


def test_add_product(db_session):
    """Тест добавления товара"""
    category = db_session.query(Category).first()

    new_product = Product(
        name="Новый товар",
        description="Новое описание",
        price=200.0,
        category_id=category.id
    )
    db_session.add(new_product)
    db_session.commit()

    # Проверяем
    products = db_session.query(Product).all()
    assert len(products) == 2
    assert products[1].name == "Новый товар"
    assert products[1].price == 200.0


def test_edit_product(db_session):
    """Тест редактирования товара"""
    product = db_session.query(Product).first()

    # Изменяем данные
    product.name = "Обновлённый товар"
    product.price = 150.0
    db_session.commit()

    # Проверяем
    updated_product = db_session.query(Product).filter(Product.id == product.id).first()
    assert updated_product.name == "Обновлённый товар"
    assert updated_product.price == 150.0


def test_delete_product(db_session):
    """Тест удаления товара"""
    product = db_session.query(Product).first()
    product_id = product.id

    # Удаляем товар
    db_session.delete(product)
    db_session.commit()

    # Проверяем
    deleted_product = db_session.query(Product).filter(Product.id == product_id).first()
    assert deleted_product is None


def test_change_order_status(db_session):
    """Тест изменения статуса заказа"""
    # Создаём тестовый заказ
    order = Order(
        user_id=123456,
        total_amount=100.0,
        customer_name="Иван Иванов",
        customer_phone="+79991234567",
        customer_address="Адрес",
        delivery_method="Курьером",
        order_number="ORD-TEST-001",
        status="new"
    )
    db_session.add(order)
    db_session.commit()

    # Изменяем статус
    updated_order = update_order_status(db_session, order.id, "confirmed")

    # Проверяем
    assert updated_order is not None
    assert updated_order.status == "confirmed"


def test_get_all_orders(db_session):
    """Тест получения всех заказов"""
    # Создаём несколько заказов
    order1 = Order(
        user_id=123456,
        total_amount=100.0,
        customer_name="Иван",
        customer_phone="+79991234567",
        customer_address="Адрес 1",
        delivery_method="Курьером",
        order_number="ORD-TEST-001"
    )
    order2 = Order(
        user_id=654321,
        total_amount=200.0,
        customer_name="Петр",
        customer_phone="+79997654321",
        customer_address="Адрес 2",
        delivery_method="Самовывоз",
        order_number="ORD-TEST-002"
    )
    db_session.add_all([order1, order2])
    db_session.commit()

    # Получаем все заказы
    orders = get_all_orders(db_session)

    # Проверяем
    assert len(orders) == 2
    assert orders[0].order_number == "ORD-TEST-001"
    assert orders[1].order_number == "ORD-TEST-002"