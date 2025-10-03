from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="open_catalog")],
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="user_profile")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="open_cart")],
        [InlineKeyboardButton(text="🏢 О магазине", callback_data="open_cart")]
    ])

def get_categories_kb(categories):
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_navigation_kb(category_id: int, current_index: int, total: int, product_id: int):
    buttons = []

    # Кнопка "Добавить в корзину"
    buttons.append([InlineKeyboardButton(text="✔️ Добавить в корзину", callback_data=f"add_to_cart_{product_id}")])

    # Кнопки навигации
    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущий", callback_data=f"nav_{category_id}_{current_index - 1}"))
    if current_index < total - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Следующий", callback_data=f"nav_{category_id}_{current_index + 1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    # Кнопка "Назад"
    buttons.append([InlineKeyboardButton(text="🛒 Корзина", callback_data="open_cart_from_product")])
    buttons.append([InlineKeyboardButton(text="⬅️ В каталог", callback_data="open_catalog")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cart_kb(items):
    buttons = []
    total = 0
    for item in items:
        # Кнопка с названием товара (кликабельная)
        buttons.append([
            InlineKeyboardButton(
                text=f"👓 {item.product.name} ({item.quantity} × {item.product.price:.0f}₽)",
                callback_data=f"view_product_{item.product_id}"
            )
        ])

        # Кнопки управления
        buttons.append([
            InlineKeyboardButton(text="➖", callback_data=f"decr_{item.id}"),
            InlineKeyboardButton(text=str(item.quantity), callback_data="ignore"),
            InlineKeyboardButton(text="➕", callback_data=f"incr_{item.id}"),
            InlineKeyboardButton(text="❌", callback_data=f"remove_{item.id}")
        ])
        total += item.quantity * item.product.price

    buttons.append([InlineKeyboardButton(text=f"💳 Итого: {total:.0f}₽",callback_data="ignore")])
    buttons.append([InlineKeyboardButton(text="📦 Оформить заказ", callback_data="start_new_order")])
    buttons.append([InlineKeyboardButton(text="⬅️ В каталог", callback_data="open_catalog")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в каталог", callback_data="open_catalog")],
        [InlineKeyboardButton(text="🏠 На главную", callback_data="back_to_menu")]
    ])

def get_product_view_kb(product_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к корзине", callback_data="back_to_cart")]
    ])

def get_delivery_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Курьером", callback_data="delivery_courier")],
        [InlineKeyboardButton(text="🏢 Самовывоз", callback_data="delivery_pickup")],
        [InlineKeyboardButton(text="🚚 Транспортной компанией", callback_data="delivery_sdek")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_cart")]
    ])

def get_confirm_address_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Использовать этот адрес", callback_data="use_address")],
        [InlineKeyboardButton(text="✏️ Изменить адрес", callback_data="change_address")]
    ])

def get_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ])

