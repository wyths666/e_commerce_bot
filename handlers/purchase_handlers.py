from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from database.models import Order
from handlers.lk_handlers import show_profile_card
from keyboards.lk_keyboards import get_profile_edit_kb, get_confirm_order_kb, get_confirm_data_kb
from states.order_states import NewOrderForm
from database.crud import get_cart_items, create_order, clear_cart, get_user_profile
from database.db_helper import get_db
from keyboards.inline_keyboards import get_delivery_kb, get_back_to_menu_kb, get_confirm_address_kb
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "start_new_order")
async def start_new_order(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)

    # Проверяем, есть ли профиль
    profile = get_user_profile(db, user_id)

    if len(profile.user_name) >1 and len(profile.user_phone) >1:
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
        await callback.message.answer(
            "❌ Вы ещё не зарегистрированы.\n"
            "Необходимо указать ФИО и телефон.",
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
        "delivery_sdek": "Транспортной компанией"
    }
    delivery_method = delivery_map.get(callback.data, "Не указан")
    await state.update_data(delivery=delivery_method)

    user_id = callback.from_user.id
    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    if delivery_method == "Курьером":
        # Требуется адрес
        if len(profile.user_address) > 1:
            # Адрес есть → подтверждаем
            await callback.message.edit_text(
                f"🏠 Ваш адрес: {profile.user_address}\n"
                f"Использовать этот адрес?",
                reply_markup=get_confirm_address_kb()
            )
            await state.set_state(NewOrderForm.confirm_address)
        else:
            # Адреса нет → просим заполнить в профиле
            await state.clear()
            await callback.message.edit_text(
                "❌ Адрес не указан.\n"
                "Необходимо указать адрес доставки.",
                reply_markup=get_profile_edit_kb(callback.from_user.id))
            #await show_profile_card(callback.message, user_id)
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
    if data['delivery'] == "Курьером":
        text += f"🏠 Адрес: {profile.user_address}\n"
    text += f"🚚 Доставка: {data['delivery']}\n\n"
    text += "🛒 <b>Список товаров:</b>\n"

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
    order = db.query(Order).filter(Order.order_number == order.order_number).first()
    order_id = order.id
    # Очищаем корзину
    clear_cart(db, user_id)

    # Отправляем сообщение админу
    admin_message = f"🆕 Новый заказ №{order.order_number}\n"

    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Посмотреть заказ", callback_data=f"admin_order_{order_id}")]
                ])
            )
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