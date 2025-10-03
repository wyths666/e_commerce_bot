from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="✏️ Редактировать товары", callback_data="admin_products")],
        [InlineKeyboardButton(text="📋 Список заказов", callback_data="admin_orders")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu")]
    ])


def get_orders_kb(orders):
    buttons = []
    for order in orders:
        buttons.append([
            InlineKeyboardButton(
                text=f"📄 {order.order_number} - {order.total_amount}₽",
                callback_data=f"admin_order_{order.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_order_status_kb(order_id, current_status):
    statuses = {"new": "В обработке", "confirmed": "Подтвержден", "delivered": "Отправлен", "cancelled": "Отменен"}
    buttons = []
    for status in statuses:
        if status == current_status:
            text = f"✅ {statuses[status]}"
        else:
            text = statuses[status]
        callback_data = f"status_{status}_{order_id}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_orders")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_products_list_kb(products):
    buttons = []
    for product in products:
        buttons.append([
            InlineKeyboardButton(
                text=f"✏️ {product.name}",
                callback_data=f"edit_product_{product.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_product_edit_kb(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Название", callback_data=f"edit_name_{product_id}")],
        [InlineKeyboardButton(text="📝 Описание", callback_data=f"edit_desc_{product_id}")],
        [InlineKeyboardButton(text="💰 Цена", callback_data=f"edit_price_{product_id}")],
        [InlineKeyboardButton(text="🖼 Фото", callback_data=f"edit_photo_{product_id}")],
        [InlineKeyboardButton(text="📂 Категория", callback_data=f"edit_category_{product_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_product_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_products")]
    ])

