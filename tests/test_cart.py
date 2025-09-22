import pytest
from database.crud import add_to_cart, get_cart_items, update_cart_item_quantity, remove_from_cart
from database.db_helper import init_db
from database.models import Product, Category, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


@pytest.fixture
def db_session():
    # Создаём временную БД для тестов
    engine = create_engine("sqlite:///:memory:")

    # Создаём таблицы
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


def test_add_to_cart(db_session):
    """Тест добавления товара в корзину"""
    user_id = 123456
    product_id = 1

    # Добавляем товар
    add_to_cart(db_session, user_id, product_id, quantity=2)

    # Проверяем
    items = get_cart_items(db_session, user_id)
    assert len(items) == 1
    assert items[0].product_id == product_id
    assert items[0].quantity == 2


def test_update_quantity(db_session):
    """Тест изменения количества"""
    user_id = 123456
    product_id = 1

    # Добавляем товар
    item = add_to_cart(db_session, user_id, product_id, quantity=1)

    # Увеличиваем количество
    update_cart_item_quantity(db_session, item.id, 5)

    # Проверяем
    items = get_cart_items(db_session, user_id)
    assert items[0].quantity == 5


def test_remove_from_cart(db_session):
    """Тест удаления товара"""
    user_id = 123456
    product_id = 1

    # Добавляем товар
    item = add_to_cart(db_session, user_id, product_id, quantity=1)

    # Удаляем
    remove_from_cart(db_session, item.id)

    # Проверяем
    items = get_cart_items(db_session, user_id)
    assert len(items) == 0