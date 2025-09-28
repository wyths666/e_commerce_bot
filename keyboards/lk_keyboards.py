from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_profile_edit_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Редактировать ФИО", callback_data=f"edit_username_{user_id}")],
        [InlineKeyboardButton(text="🏠 Редактировать Адрес доставки", callback_data=f"edit_user_address_{user_id}")],
        [InlineKeyboardButton(text="📱 Редактировать Телефон", callback_data=f"edit_user_phone_{user_id}")],
        [InlineKeyboardButton(text="📦 Мои заказы", callback_data=f"orders_{user_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])





def return_profile_edit_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Вернуться в профиль", callback_data=f"user_profile")]
    ])

def share_contact():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_user_orders_kb(orders, user_id):
    buttons = []
    for order in orders:
        buttons.append([
            InlineKeyboardButton(
                text=f"📄 {order.order_number} - {order.total_amount}₽",
                callback_data=f"user_order_{order.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"user_profile")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def order_details_kb(order_id, user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↪️ Повторить заказ", callback_data=f"user_order_reply_{order_id}")],
        [InlineKeyboardButton(text="↩️ Вернуться к списку заказов", callback_data=f"orders_{user_id}")],
        [InlineKeyboardButton(text="⬅️ Вернуться в профиль", callback_data=f"user_profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=f"back_to_menu")]
    ])

def kb_with_cancel(order_id, user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить заказ", callback_data=f"cancelling_{order_id}")],
        [InlineKeyboardButton(text="↩️ Вернуться к списку заказов", callback_data=f"orders_{user_id}")],
        [InlineKeyboardButton(text="⬅️ Вернуться в профиль", callback_data=f"user_profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=f"back_to_menu")]
    ])

