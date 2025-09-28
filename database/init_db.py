# Запуск командой python -m database.init_db
from .db_helper import init_db, engine
from .models import Base, Category, Product, Profile
from sqlalchemy.orm import sessionmaker

def add_demo_data():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Проверяем, есть ли уже категории
    if db.query(Category).count() == 0:
        cat1 = Category(name="Женская коллекция")
        cat2 = Category(name="Детская коллекция")
        cat3 = Category(name="Мужская коллекция")
        db.add_all([cat1, cat2, cat3])
        db.commit()

        # Добавляем товары
        products = [
            Product(name="Kyoto", description="Материал: пластик", price=2999.0, photo_url="https://static.insales-cdn.com/r/2zT2hjTUWd0/rs:fit:1000:0:1/q:100/plain/images/products/1/5201/1014182993/11056-C1-3.jpg@webp", category_id=1),
            Product(name="Patty", description="Материал: пластик", price=6999.0, photo_url="https://static.insales-cdn.com/r/qOaNVrBalok/rs:fit:1000:0:1/q:100/plain/images/products/1/5109/1014182901/LR3515-A1325-P171-C98-3.jpg@webp", category_id=1),
            Product(name="Kiky", description="Материал: пластик", price=6999.0, photo_url="https://static.insales-cdn.com/r/JkLpAziS-jU/rs:fit:1000:0:1/q:100/plain/images/products/1/5242/1014183034/LR3522-10-P55-C32-3.jpg@webp", category_id=1),
            Product(name="Amor", description="Материал: металл", price=15990.0, photo_url="https://static.insales-cdn.com/r/0x81hzN5QBE/rs:fit:1000:0:1/q:100/plain/images/products/1/4828/1014182620/1024-C1-1.jpg@webp", category_id=2),
            Product(name="Tiffany", description="Материал: металл", price=1599.0, photo_url="https://static.insales-cdn.com/r/tHf8yOy65SY/rs:fit:1000:0:1/q:100/plain/images/products/1/5105/1014182897/1031-C6-1.jpg_@webp", category_id=2),
            Product(name="Coco", description="Материал: пластик", price=999.0, photo_url="https://static.insales-cdn.com/r/mMPo7-M3hDw/rs:fit:1000:0:1/q:100/plain/images/products/1/5073/1014182865/6-118-C2-2.jpg@webp", category_id=2),
            Product(name="Kourt", description="Материал: металл", price=6999.0, photo_url="https://static.insales-cdn.com/r/GpDfntRjRWg/rs:fit:1000:0:1/q:100/plain/images/products/1/5029/1014182821/LR1104-C97-P93-362-2.jpg@webp", category_id=3),
            Product(name="Seoul", description="Материал: пластик", price=6999.0, photo_url="https://static.insales-cdn.com/r/9mBD9tQCxZU/rs:fit:1000:0:1/q:100/plain/images/products/1/5198/1014182990/R5047-C5-1.jpg@webp", category_id=3),
            Product(name="Montreal", description="Материал: металл", price=3999.0, photo_url="https://static.insales-cdn.com/r/TzauUJX7_LQ/rs:fit:1000:0:1/q:100/plain/images/products/1/5424/1014183216/R5046-C3-1.jpg@webp", category_id=3)

        ]
        db.add_all(products)
        db.commit()

    db.close()

if __name__ == "__main__":
    init_db()        # Создаёт таблицы
    add_demo_data()  # Добавляет демо-данные
    print("✅ База данных инициализирована. Демо-данные добавлены.")