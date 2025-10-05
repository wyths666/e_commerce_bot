# E-Commerce Bot

Telegram-бот для интернет-магазина с полным функционалом: каталог товаров, корзина, оформление заказов, REST API, панель администратора и тестирование.
---

## 🧰 Технологии

- Python 3.10+
- aiogram 3.x — асинхронный Telegram Bot API
- FastAPI — современное REST API
- SQLAlchemy — ORM для работы с БД
- SQLite — легковесная файловая БД
- Pydantic — валидация данных для API
- Uvicorn — ASGI сервер
- pytest — для тестирования

---

## 🧩 Функционал

- 🛒 Каталог товаров с навигацией по категориям
- 🛒 Корзина покупок (добавление, изменение, удаление)
- 💳 Оформление заказа через FSM (имя, телефон, адрес, доставка)
- 📊 Генерация уникального номера заказа
- 🎯 Административная панель:
  - Добавление/редактирование/удаление товаров
  - Просмотр и изменение статуса заказов
- 🌐 Веб-интерфейс управления заказами 
- 📝 Логирование всех заказов
- 🧪 Полное тестирование (unit-тесты)

---

## 📦 Структура проекта
```markdown
e_commerce_bot/
│
├── .env                    
├── .gitignore              
├── bot.py                  
├── config.py               
├── main.py                 
├── README.md               
├── requirements.txt        
├── bot.db                  
│
├── api/                    
│   ├── models/
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   └── routes/
│       └── orders.py
│
├── database/               
│   ├── crud.py            
│   ├── db_helper.py       
│   ├── init_db.py         
│   └── models.py          
│
├── handlers/               
│   ├── admin_handlers.py
│   ├── lk_handlers.py     
│   ├── order_handlers.py  
│   ├── purchase_handlers.py 
│   └── user_handlers.py   
│
├── keyboards/              
│   ├── admin_keyboards.py
│   ├── inline_keyboards.py
│   └── lk_keyboards.py
│
├── states/                 
│   ├── admin_states.py
│   ├── order_states.py
│   └── user_states.py
│
├── templates/              
│   └── orders.html
│
└── tests/                  
    ├── test_admin.py
    ├── test_cart.py
    └── test_orders.py
```
---

## 🔧 Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/wyths666/e_commerce_bot.git
cd e_commerce_bot
```

2. Установите зависимости:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```
3. Создайте файл .env
```bash
BOT_TOKEN="ваш_токен_бота"
ADMIN_IDS=123456789,234567891 # получить ID можно в @myidbot 
DATABASE_URL="sqlite:///./bot.db"
```
---

## ⚙ Запуск
```bash
python bot.py
```
---

## 🧪 Тесты
```markdown
pytest tests/ -v

-- test_add_product # Тест добавления товара
-- test_edit_product # Тест редактирования товара   
-- test_delete_product # Тест удаления товара
-- test_change_order_status # Тест изменения статусов заказа
-- test_get_all_orders # Тест получения списка заказов     
-- test_add_to_cart # Тест добавления товара в корзину       
-- test_update_quantity # Тест изменения количества в корзине    
-- test_remove_from_cart # Тест удаления из корзины  
-- test_create_order # Тест создания заказа        
-- test_order_number_unique # Тест присваивания уникального номера заказа 
-- test_get_orders_by_user # Тест получения заказов пользователя  
-- test_clear_cart_after_order # Тест очистки корзины после подтверждения заказа
```
---

## 🛠 Панель администратора

Админ-панель доступна только для авторизованных пользователей.
Используйте команду /admin для входа.
- Добавить новый товар
- Редактировать товар
 - Редактировать наименование
 - Редактировать описание
 - Редактировать цену
 - Редактировать фото
 - Редактировать категорию
 - Удалить товар
- Получить список заказов
 - Редактировать статус заказа

---

## 📄 Логи
Логи сохраняются в файле logs/bot.log.
Там можно посмотреть все заказы, ошибки и действия пользователей.

## 📂 База данных
База данных хранится в файле bot.db (SQLite).

🗃️ Структура базы данных:
```markdown
Таблица: categories — Категории товаров
- id # Уникальный ID (PK)
- name # Название категории
✅ Уникальность по name 

Таблица: products — Товары
- id # Уникальный ID 
- name # Название товара
- description # Описание товара
- price # Цена товара
- photo_url # URL фото товара
- category_id # Внешний ключ на categories.id  
🔗 Связь: category_id → categories.id 
✅ Индекс по category_id 

Таблица: cart_items — Содержимое корзины
- id # Уникальный ID (PK)
- user_id # ID пользователя (Telegram ID)
- product_id # Внешний ключ на products.id (FK)
- quantity # Количество товара в корзине
🔗 Связь: product_id → products.id
✅ Индекс по user_id и product_id 

Таблица: orders — Заказы
- id # Уникальный ID (PK)
- user_id # ID пользователя (Telegram ID)
- created_at # Дата и время создания заказа
- status # Статус заказа (new, confirmed, delivered, cancelled)
- total_amount # Общая сумма заказа 
- customer_name # Имя покупателя
- customer_phone # Телефон покупателя 
- customer_address # Адрес доставки
- delivery_method # Способ доставки (Курьером, Самовывоз, СДЭК) 
- order_number # Уникальный номер заказа (например,ORD-20250405-ABCD)
✅ Уникальность по order_number
✅ Индекс по user_id и status 
```
---

## 👨‍💻 Автор

[Власов Владиcлав] — [GitHub](https://github.com/wyths666) | [Telegram](https://t.me/wyths666)