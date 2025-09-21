from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states.order_states import OrderForm
from database.crud import get_cart_items, create_order, clear_cart
from database.db_helper import get_db
from handlers.order_handlers import show_cart
from keyboards.inline_keyboards import get_delivery_kb, get_confirm_kb, get_back_to_menu_kb
import re
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "start_order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("👤 Введите ваше ФИО:")
    await state.set_state(OrderForm.name)

@router.message(OrderForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Введите ваш телефон в формате +7...:")
    await state.set_state(OrderForm.phone)

@router.message(OrderForm.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if phone[0] == "8" and len(phone) == 11:
        phone = "+7" + phone[1:]

    if phone[:2] == "+7":

        if re.match(r'^\d{10}$', phone[2:]):
            await state.update_data(phone=phone)
            await message.answer("📍 Введите ваш адрес доставки:")
            await state.set_state(OrderForm.address)
    else:
        await message.answer("❌ Неверный формат телефона.\n📱 Введите ваш телефон в формате:\n+7XXXXXXXXXX или 8XXXXXXXXXX")

@router.message(OrderForm.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("🚚 Выберите способ доставки:", reply_markup=get_delivery_kb())
    await state.set_state(OrderForm.delivery)


@router.callback_query(OrderForm.delivery)
async def process_delivery(callback: CallbackQuery, state: FSMContext):
    delivery_map = {
        "delivery_courier": "Курьером",
        "delivery_pickup": "Самовывоз",
        "delivery_sdek": "СДЭК"
    }
    delivery_method = delivery_map.get(callback.data, "Не указан")
    await state.update_data(delivery=delivery_method)

    # Подготовка подтверждения
    data = await state.get_data()
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)
    items = get_cart_items(db, user_id)

    if not items:
        await callback.message.edit_text("🛒 Корзина пуста.", reply_markup=get_back_to_menu_kb())
        await state.clear()
        return

    text = "📦 <b>Подтверждение заказа:</b>\n\n"
    text += f"👤 ФИО: {data['name']}\n"
    text += f"📱 Телефон: {data['phone']}\n"
    text += f"📍 Адрес: {data['address']}\n"
    text += f"🚚 Доставка: {delivery_method}\n\n"
    text += "🛒 <b>Товары:</b>\n"

    total = 0.0
    for item in items:
        subtotal = item.product.price * item.quantity
        total += subtotal
        text += f"▪️ {item.product.name} × {item.quantity} = {subtotal:.0f}₽\n"

    text += f"\n💳 <b>Итого: {total:.0f}₽</b>"

    await callback.message.edit_text(text, reply_markup=get_confirm_kb(), parse_mode="HTML")
    await state.update_data(total=total)
    await state.set_state(OrderForm.confirm)


@router.callback_query(OrderForm.confirm, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)

    # Создаём заказ
    order = create_order(
        db=db,
        user_id=user_id,
        total_amount=data['total'],
        customer_name=data['name'],
        customer_phone=data['phone'],
        customer_address=data['address'],
        delivery_method=data['delivery']
    )
    logger.info(f"Пользователь {user_id} оформил заказ № {order.order_number}")
    # Очищаем корзину
    clear_cart(db, user_id)

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


@router.callback_query(OrderForm.confirm, F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Оформление заказа отменено.", reply_markup=get_back_to_menu_kb())

@router.callback_query(F.data == "back_to_cart")
async def back_to_cart(callback: CallbackQuery):
    await show_cart(callback)