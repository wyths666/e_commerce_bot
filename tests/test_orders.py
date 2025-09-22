import pytest
from database.crud import add_to_cart, create_order, get_orders_by_user, clear_cart
from database.models import Product, Category, Base
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

    product1 = Product(
        name="Товар 1",
        description="Описание 1",
        price=100.0,
        category_id=category.id
    )
    product2 = Product(
        name="Товар 2",
        description="Описание 2",
        price=200.0,
        category_id=category.id
    )
    db.add_all([product1, product2])
    db.commit()

    yield db
    db.close()


def test_create_order(db_session):
    """Тест создания заказа"""
    user_id = 123456
    product1_id = 1
    product2_id = 2

    # Добавляем товары в корзину
    add_to_cart(db_session, user_id, product1_id, quantity=2)  # 2 × 100 = 200
    add_to_cart(db_session, user_id, product2_id, quantity=1)  # 1 × 200 = 200

    # Создаём заказ
    order = create_order(
        db=db_session,
        user_id=user_id,
        total_amount=400.0,
        customer_name="Иван Иванов",
        customer_phone="+79991234567",
        customer_address="Москва, ул. Тестовая, 1",
        delivery_method="Курьером"
    )

    # Проверяем
    assert order is not None
    assert order.user_id == user_id
    assert order.total_amount == 400.0
    assert order.customer_name == "Иван Иванов"
    assert order.customer_phone == "+79991234567"
    assert order.customer_address == "Москва, ул. Тестовая, 1"
    assert order.delivery_method == "Курьером"
    assert order.status == "new"
    assert len(order.order_number) > 10  # Номер заказа сгенерирован


def test_order_number_unique(db_session):
    """Тест уникальности номера заказа"""
    user_id = 123456
    product_id = 1

    add_to_cart(db_session, user_id, product_id, quantity=1)

    # Создаём два заказа
    order1 = create_order(
        db=db_session,
        user_id=user_id,
        total_amount=100.0,
        customer_name="Иван",
        customer_phone="+79991234567",
        customer_address="Адрес",
        delivery_method="Курьером"
    )

    add_to_cart(db_session, user_id, product_id, quantity=1)  # Снова добавляем в корзину

    order2 = create_order(
        db=db_session,
        user_id=user_id,
        total_amount=100.0,
        customer_name="Иван",
        customer_phone="+79991234567",
        customer_address="Адрес",
        delivery_method="Курьером"
    )

    # Проверяем, что номера разные
    assert order1.order_number != order2.order_number


def test_get_orders_by_user(db_session):
    """Тест получения заказов пользователя"""
    user_id = 123456
    another_user_id = 654321
    product_id = 1

    # Создаём заказы для разных пользователей
    add_to_cart(db_session, user_id, product_id, quantity=1)
    order1 = create_order(
        db=db_session,
        user_id=user_id,
        total_amount=100.0,
        customer_name="Иван",
        customer_phone="+79991234567",
        customer_address="Адрес",
        delivery_method="Курьером"
    )

    add_to_cart(db_session, another_user_id, product_id, quantity=1)
    order2 = create_order(
        db=db_session,
        user_id=another_user_id,
        total_amount=100.0,
        customer_name="Петр",
        customer_phone="+79997654321",
        customer_address="Адрес 2",
        delivery_method="Самовывоз"
    )

    # Получаем заказы пользователя
    user_orders = get_orders_by_user(db_session, user_id)

    # Проверяем
    assert len(user_orders) == 1
    assert user_orders[0].id == order1.id
    assert user_orders[0].customer_name == "Иван"


def test_clear_cart_after_order(db_session):
    """Тест очистки корзины после заказа"""
    from database.crud import get_cart_items

    user_id = 123456
    product_id = 1

    # Добавляем товар в корзину
    add_to_cart(db_session, user_id, product_id, quantity=3)

    # Проверяем, что корзина не пуста
    items_before = get_cart_items(db_session, user_id)
    assert len(items_before) == 1

    # Создаём заказ
    order = create_order(
        db=db_session,
        user_id=user_id,
        total_amount=100.0,
        customer_name="Иван",
        customer_phone="+79991234567",
        customer_address="Адрес",
        delivery_method="Курьером"
    )

    # Проверяем, что корзина пуста
    items_after = get_cart_items(db_session, user_id)
    assert len(items_after) == 0