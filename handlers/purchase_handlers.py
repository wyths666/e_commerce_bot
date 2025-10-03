from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from handlers.lk_handlers import show_profile_card
from keyboards.lk_keyboards import get_profile_edit_kb, get_confirm_order_kb, get_confirm_data_kb
from states.order_states import OrderForm, NewOrderForm
from database.crud import get_cart_items, create_order, clear_cart, get_user_profile
from database.db_helper import get_db
from handlers.order_handlers import show_cart
from keyboards.inline_keyboards import get_delivery_kb, get_confirm_kb, get_back_to_menu_kb, get_confirm_address_kb
import re
import logging

logger = logging.getLogger(__name__)

router = Router()


# async def confirm_new_order(message, state: FSMContext):
#     data = await state.get_data()
#     user_id = message.from_user.id
#
#     db_gen = get_db()
#     db = next(db_gen)
#     items = get_cart_items(db, user_id)
#
#     if not items:
#         await message.answer("🛒 Корзина пуста.", reply_markup=get_back_to_menu_kb())
#         await state.clear()
#         return
#
#     text = "📦 <b>Подтверждение заказа:</b>\n\n"
#     text += f"👤 ФИО: {data['name']}\n"
#     text += f"📱 Телефон: {data['phone']}\n"
#     if data.get('address'):
#         text += f"📍 Адрес: {data['address']}\n"
#     text += f"🚚 Доставка: {data['delivery']}\n\n"
#     text += "🛒 <b>Товары:</b>\n"
#
#     total = 0.0
#     for item in items:
#         subtotal = item.product.price * item.quantity
#         total += subtotal
#         text += f"▪️ {item.product.name} × {item.quantity} = {subtotal:.0f}₽\n"
#
#     text += f"\n💳 <b>Итого: {total:.0f}₽</b>"
#
#     await message.edit_text(text, reply_markup=get_confirm_kb(), parse_mode="HTML")
#     await state.update_data(total=total)
#     await state.set_state(NewOrderForm.confirm)
#
# @router.callback_query(F.data == "start_new_order")
# async def start_new_order(callback: CallbackQuery, state: FSMContext):
#     user_id = callback.from_user.id
#
#     db_gen = get_db()
#     db = next(db_gen)
#
#     # Проверяем, есть ли профиль
#     profile = get_user_profile(db, user_id)
#
#     if profile:
#         # Есть профиль → используем данные
#         await state.update_data(
#             name=profile.user_name,
#             phone=profile.user_phone,
#             address=profile.user_address
#         )
#
#         # Показываем способы доставки
#         await callback.message.delete()
#         await callback.message.answer("🚚 Выберите способ доставки:", reply_markup=get_delivery_kb())
#         await state.set_state(NewOrderForm.delivery)
#     else:
#         # Нет профиля → спрашиваем всё
#         await callback.message.edit_text("👤 Введите ваше имя:")
#         await state.set_state(OrderForm.name)  # Старая схема
#
# @router.callback_query(F.data == "start_order")
# async def start_order(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#
#     try:
#         await callback.message.delete()
#     except:
#         pass
#
#     await callback.message.answer("👤 Введите ваше ФИО:")
#     await state.set_state(OrderForm.name)
#
# @router.message(OrderForm.name)
# async def process_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await message.answer("📱 Введите ваш телефон в формате +7...:")
#     await state.set_state(OrderForm.phone)
#
# @router.message(OrderForm.phone)
# async def process_phone(message: Message, state: FSMContext):
#     phone = message.text.strip()
#     if phone[0] == "8" and len(phone) == 11:
#         phone = "+7" + phone[1:]
#
#     if phone[:2] == "+7":
#
#         if re.match(r'^\d{10}$', phone[2:]):
#             await state.update_data(phone=phone)
#             await message.answer("📍 Введите ваш адрес доставки:")
#             await state.set_state(OrderForm.address)
#     else:
#         await message.answer("❌ Неверный формат телефона.\n📱 Введите ваш телефон в формате:\n+7XXXXXXXXXX или 8XXXXXXXXXX")
#
# @router.message(OrderForm.address)
# async def process_address(message: Message, state: FSMContext):
#     await state.update_data(address=message.text)
#     await message.answer("🚚 Выберите способ доставки:", reply_markup=get_delivery_kb())
#     await state.set_state(OrderForm.delivery)
#
#
# @router.callback_query(NewOrderForm.delivery)
# async def process_delivery_new(callback: CallbackQuery, state: FSMContext):
#     delivery_map = {
#         "delivery_courier": "Курьером",
#         "delivery_pickup": "Самовывоз",
#         "delivery_sdek": "СДЭК"
#     }
#     delivery_method = delivery_map.get(callback.data, "Не указан")
#     await state.update_data(delivery=delivery_method)
#
#     data = await state.get_data()
#
#     if delivery_method == "Курьером":
#         # Требуется адрес
#         if data.get('address'):
#             # Адрес есть в профиле → подтверждаем
#             await callback.message.edit_text(
#                 f"📍 Ваш адрес: {data['address']}\n"
#                 f"Использовать этот адрес?",
#                 reply_markup=get_confirm_address_kb()
#             )
#         else:
#             # Адреса нет → спрашиваем
#             await callback.message.edit_text("📍 Введите адрес доставки:")
#             await state.set_state(NewOrderForm.address)
#     else:
#         # Не требует адреса → подтверждаем заказ
#         await confirm_new_order(callback, state)
#
# @router.callback_query(F.data == "change_address")
# async def change_address(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text("📍 Введите новый адрес доставки:")
#     await state.set_state(NewOrderForm.address)
#
#
# @router.callback_query(F.data == "use_address")
# async def confirm_address(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#
#     # Подтверждаем заказ
#     await confirm_new_order(callback, state)
#
#
#
# @router.message(NewOrderForm.address)
# async def process_address_new(message: Message, state: FSMContext):
#     await state.update_data(address=message.text)
#
#     # Сохраняем адрес в профиль
#     data = await state.get_data()
#     user_id = message.from_user.id
#
#     db_gen = get_db()
#     db = next(db_gen)
#     profile = get_user_profile(db, user_id)
#
#     if profile:
#         profile.user_address = message.text
#         db.commit()
#
#     await confirm_new_order(message, state)
#
# @router.callback_query(OrderForm.delivery)
# async def process_delivery(callback: CallbackQuery, state: FSMContext):
#     delivery_map = {
#         "delivery_courier": "Курьером",
#         "delivery_pickup": "Самовывоз",
#         "delivery_sdek": "СДЭК"
#     }
#     delivery_method = delivery_map.get(callback.data, "Не указан")
#     await state.update_data(delivery=delivery_method)
#
#     # Подготовка подтверждения
#     data = await state.get_data()
#     user_id = callback.from_user.id
#
#     db_gen = get_db()
#     db = next(db_gen)
#     items = get_cart_items(db, user_id)
#
#     if not items:
#         await callback.message.edit_text("🛒 Корзина пуста.", reply_markup=get_back_to_menu_kb())
#         await state.clear()
#         return
#
#     text = "📦 <b>Подтверждение заказа:</b>\n\n"
#     text += f"👤 ФИО: {data['name']}\n"
#     text += f"📱 Телефон: {data['phone']}\n"
#     text += f"📍 Адрес: {data['address']}\n"
#     text += f"🚚 Доставка: {delivery_method}\n\n"
#     text += "🛒 <b>Товары:</b>\n"
#
#     total = 0.0
#     for item in items:
#         subtotal = item.product.price * item.quantity
#         total += subtotal
#         text += f"▪️ {item.product.name} × {item.quantity} = {subtotal:.0f}₽\n"
#
#     text += f"\n💳 <b>Итого: {total:.0f}₽</b>"
#
#     # ✅ СОХРАНЯЕМ ДАННЫЕ ТОВАРОВ, А НЕ ТОЛЬКО ID
#     items_data = [
#         {
#             'product_id': item.product.id,
#             'quantity': item.quantity,
#             'price': item.product.price
#         }
#         for item in items
#     ]
#
#     await state.update_data(total=total, items=items_data)
#     await callback.message.edit_text(text, reply_markup=get_confirm_kb(), parse_mode="HTML")
#     await state.set_state(OrderForm.confirm)
#
#
# @router.callback_query(OrderForm.confirm, F.data == "confirm_order")
# async def confirm_order(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     user_id = callback.from_user.id
#
#     db_gen = get_db()
#     db = next(db_gen)
#     items_data = data.get('items', [])
#     # Создаём заказ
#     order = create_order(
#         db=db,
#         user_id=user_id,
#         total_amount=data['total'],
#         customer_name=data['name'],
#         customer_phone=data['phone'],
#         customer_address=data['address'],
#         delivery_method=data['delivery'],
#         items_data=items_data
#     )
#     logger.info(f"Пользователь {user_id} оформил заказ № {order.order_number}")
#     # Очищаем корзину
#     clear_cart(db, user_id)
#
#     await callback.message.edit_text(
#         f"✅ Заказ оформлен!\n\n"
#         f"📄 Номер заказа: <b>{order.order_number}</b>\n"
#         f"💳 Сумма: {data['total']:.0f}₽\n"
#         f"🚚 Доставка: {data['delivery']}\n\n"
#         f"Спасибо за покупку!",
#         reply_markup=get_back_to_menu_kb(),
#         parse_mode="HTML"
#     )
#
#     await state.clear()
#
#
# @router.callback_query(OrderForm.confirm, F.data == "cancel_order")
# async def cancel_order(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await callback.message.edit_text("❌ Оформление заказа отменено.", reply_markup=get_back_to_menu_kb())
#
# @router.callback_query(F.data == "back_to_cart")
# async def back_to_cart(callback: CallbackQuery):
#     await show_cart(callback)

@router.callback_query(F.data == "start_new_order")
async def start_new_order(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)

    # Проверяем, есть ли профиль
    profile = get_user_profile(db, user_id)

    if profile:
        # Есть профиль → запрашиваем подтверждение данных
        text = f"👤 Ваши данные:\n"
        text += f"ФИО: {profile.user_name}\n"
        text += f"Телефон: {profile.user_phone}\n"
        text += f"Адрес: {profile.user_address or 'Не указан'}\n"
        text += f"\n✅ Подтвердите данные или измените их."

        if callback.message.text:
            await callback.message.edit_text(text, reply_markup=get_confirm_data_kb(), parse_mode="HTML")
        else:
            # Если сообщение не содержит текста → отправляем новое
            await callback.message.answer(text, reply_markup=get_confirm_data_kb(), parse_mode="HTML")
    else:
        # Нет профиля → предлагаем зарегистрироваться
        await callback.message.edit_text(
            "❌ Вы ещё не зарегистрированы.\n"
            "Перейдите в личный кабинет, чтобы заполнить данные.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➡️ Перейти в личный кабинет", callback_data="user_profile")]
            ])
        )





@router.callback_query(F.data == "confirm_data")
async def confirm_data(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    # Запрашиваем метод доставки
    await callback.message.edit_text("🚚 Выберите способ доставки:", reply_markup=get_delivery_kb())
    await state.set_state(NewOrderForm.delivery)


@router.callback_query(F.data == "edit_data")
async def edit_data(callback: CallbackQuery, state: FSMContext):
    # Переходим в личный кабинет
    await callback.message.edit_text("📝 Редактирование данных:",
                                     reply_markup=get_profile_edit_kb(callback.from_user.id))


@router.callback_query(NewOrderForm.delivery)
async def process_delivery_new(callback: CallbackQuery, state: FSMContext):
    delivery_map = {
        "delivery_courier": "Курьером",
        "delivery_pickup": "Самовывоз",
        "delivery_sdek": "СДЭК"
    }
    delivery_method = delivery_map.get(callback.data, "Не указан")
    await state.update_data(delivery=delivery_method)

    user_id = callback.from_user.id
    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    if delivery_method == "Курьером":
        # Требуется адрес
        if profile.user_address:
            # Адрес есть → подтверждаем
            await callback.message.edit_text(
                f"📍 Ваш адрес: {profile.user_address}\n"
                f"Использовать этот адрес?",
                reply_markup=get_confirm_address_kb()
            )
            await state.set_state(NewOrderForm.confirm_address)
        else:
            # Адреса нет → просим заполнить в профиле
            await callback.message.edit_text("📍 Заполните адрес в личном кабинете:")
            await show_profile_card(callback.message, user_id)
    else:
        # Не требует адреса → подтверждаем заказ
        await confirm_order_summary(callback, state)

@router.callback_query(F.data == "use_address")
async def confirm_address(callback: CallbackQuery, state: FSMContext):
    await confirm_order_summary(callback, state)

@router.callback_query(F.data == "change_address")
async def change_address(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📍 Заполните адрес в личном кабинете:")
    await show_profile_card(callback.message, callback.from_user.id)


async def confirm_order_summary(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)
    items = get_cart_items(db, user_id)

    if not items:
        await callback.message.edit_text("🛒 Корзина пуста.", reply_markup=get_back_to_menu_kb())
        await state.clear()
        return

    text = "📦 <b>Подтверждение заказа:</b>\n\n"
    text += f"👤 ФИО: {profile.user_name}\n"
    text += f"📱 Телефон: {profile.user_phone}\n"
    if profile.user_address:
        text += f"📍 Адрес: {profile.user_address}\n"
    text += f"🚚 Доставка: {data['delivery']}\n\n"
    text += "🛒 <b>Товары:</b>\n"

    total = 0.0
    for item in items:
        subtotal = item.product.price * item.quantity
        total += subtotal
        text += f"▪️ {item.product.name} × {item.quantity} = {subtotal:.0f}₽\n"

    text += f"\n💳 <b>Итого: {total:.0f}₽</b>"

    await callback.message.edit_text(text, reply_markup=get_confirm_order_kb(), parse_mode="HTML")
    await state.update_data(total=total)
    await state.set_state(NewOrderForm.confirm_order)


@router.callback_query(NewOrderForm.confirm_order, F.data == "confirm_new_order")
async def confirm_new_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)
    items = get_cart_items(db, user_id)

    # Подготовка данных для заказа
    items_data = [
        {
            'product_id': item.product.id,
            'quantity': item.quantity,
            'price': item.product.price
        }
        for item in items
    ]

    # Создаём заказ
    order = create_order(
        db=db,
        user_id=user_id,
        total_amount=data['total'],
        customer_name=profile.user_name,
        customer_phone=profile.user_phone,
        customer_address=profile.user_address,
        delivery_method=data['delivery'],
        items_data=items_data
    )

    logger.info(f"Пользователь {user_id} оформил заказ № {order.order_number}")

    # Очищаем корзину
    clear_cart(db, user_id)

    # Отправляем сообщение админу
    admin_message = f"🆕 Новый заказ №{order.order_number}\n"

    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(admin_id, admin_message)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения админу {admin_id}: {e}")

    await callback.message.edit_text(
        f"✅ Заказ оформлен!\n\n"
        f"📄 Номер заказа: <b>{order.order_number}</b>\n"
        f"💳 Сумма: {data['total']:.0f}₽\n"
        f"🚚 Доставка: {data['delivery']}\n\n"
        f"Спасибо за покупку!",
        reply_markup=get_back_to_menu_kb(),
        parse_mode="HTML"
    )

    await state.clear()