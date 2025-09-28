from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import re
from states.user_states import UserProfile
from database import models
from database.crud import get_user_profile, get_orders_by_user, user_cancel_order
from database.db_helper import get_db

from keyboards.lk_keyboards import get_profile_edit_kb, return_profile_edit_kb, share_contact, get_user_orders_kb, \
    order_details_kb, kb_with_cancel

router = Router()


def normalize_phone(phone: str) -> str | None:
    """Приводит телефон к формату +7.........., возвращает None если формат неверный"""
    # Убираем все символы, кроме цифр
    digits = re.sub(r'\D', '', phone)

    # Проверяем длину
    if len(digits) == 11 and digits.startswith('8'):
        # Заменяем 8 на +7
        return f"+7{digits[1:]}"
    elif len(digits) == 11 and digits.startswith('7'):
        # Добавляем +
        return f"+{digits}"
    elif len(digits) == 10:
        # Добавляем +7
        return f"+7{digits}"
    elif len(digits) == 12 and digits.startswith('7'):
        # Уже +7
        return f"+{digits[1:]}"
    else:
        # Если формат непонятный — возвращаем None
        return None


async def show_profile_card(message, user_id=None):
    if user_id is None:
        user_id = message.from_user.id

    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    if not profile:
        await message.answer("❌ Профиль не найден.")
        return

    text = f'📋 Ваши данные:\n'
    text += f'👤 ФИО: {profile.user_name or "Не указано"}\n'
    text += f'📱 Телефон: {profile.user_phone or "Не указано"}\n'
    text += f'🏠 Адрес: {profile.user_address or "Не указано"}'


    try:
        await message.edit_text(text, reply_markup=get_profile_edit_kb(user_id))
    except:
        await message.answer(text, reply_markup=get_profile_edit_kb(user_id))

@router.callback_query(F.data == "user_profile")
async def user_profile(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    if not profile:
        # Создаём пустой профиль
        new_profile = models.Profile(
            user_id=user_id,
            user_name=None,
            user_phone=None,
            user_address=None
        )
        db.add(new_profile)
        db.commit()
        profile = new_profile

    text = f'📋 Ваши данные:\n'
    text += f'👤 ФИО: {profile.user_name or "Не указано"}\n'
    text += f'📱 Телефон: {profile.user_phone or "Не указано"}\n'
    text += f'🏠 Адрес: {profile.user_address or "Не указано"}'

    await callback.message.edit_text(text, reply_markup=get_profile_edit_kb(user_id))

#=============== Редактирование ФИО ==========================

@router.callback_query(F.data.startswith("edit_username_"))
async def start_edit_username(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(editing_user_id=user_id, field="name")
    await callback.message.edit_text("✏️ Введите ваше имя:", reply_markup=return_profile_edit_kb())
    await state.set_state(UserProfile.name)

@router.message(UserProfile.name)
async def process_edit_username(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['editing_user_id']

    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    if profile:
        profile.user_name = message.text
        db.commit()
        await message.answer("✅ ФИО Изменено!", show_alert=True)
        await show_profile_card(message, user_id)
    else:
        await message.answer("❌ Профиль не найден.")

    await state.clear()

#=============== Редактирование Адреса ==========================

@router.callback_query(F.data.startswith("edit_user_address_"))
async def start_edit_user_address(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(editing_user_id=user_id, field="address")
    await callback.message.edit_text("✏️ Введите адрес доставки:", reply_markup=return_profile_edit_kb())
    await state.set_state(UserProfile.address)

@router.message(UserProfile.address)
async def process_edit_user_address(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['editing_user_id']

    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    if profile:
        profile.user_address = message.text
        db.commit()
        await message.answer("✅ Адрес доставки изменен!", show_alert=True)
        await show_profile_card(message, user_id)
    else:
        await message.answer("❌ Профиль не найден.")

    await state.clear()

#=============== Редактирование Телефона =========================
@router.callback_query(F.data.startswith("edit_user_phone_"))
async def start_edit_user_phone(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])
    await state.update_data(editing_user_id=user_id, field="phone")

    await callback.message.answer(
        "📱 Введите номер телефона или нажмите на кнопку 'Отправить номер':",
        reply_markup=share_contact()
    )
    await state.set_state(UserProfile.phone)

@router.message(UserProfile.phone, F.contact)
async def process_edit_user_phone_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['editing_user_id']

    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)

    raw_phone = message.contact.phone_number
    normalized_phone = normalize_phone(raw_phone)

    if normalized_phone is None:
        await message.answer(
            f"❌ Неверный формат номера: {raw_phone}\n"
            f"📱 Пожалуйста, отправьте номер ещё раз."
        )
        return

    if profile:
        profile.user_phone = normalized_phone
        db.commit()

        await message.answer(f"✅ Телефон обновлён: {normalized_phone}", reply_markup=ReplyKeyboardRemove())
        await show_profile_card(message, user_id)
    else:
        await message.answer("❌ Профиль не найден.", reply_markup=ReplyKeyboardRemove())

    await state.clear()

@router.message(UserProfile.phone)
async def process_edit_user_phone_text(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['editing_user_id']

    db_gen = get_db()
    db = next(db_gen)
    profile = get_user_profile(db, user_id)
    raw_phone = message.text
    normalized_phone = normalize_phone(raw_phone)

    if normalized_phone is None:
        await message.answer(
            f"❌ Неверный формат номера: {raw_phone}\n"
            f"📱 Пожалуйста, отправьте номер ещё раз."
        )
        return

    if profile:
        profile.user_phone = normalized_phone
        db.commit()

        await message.answer(f"✅ Телефон обновлён: {normalized_phone}", reply_markup=ReplyKeyboardRemove())
        await show_profile_card(message, user_id)
    else:
        await message.answer("❌ Профиль не найден.", reply_markup=ReplyKeyboardRemove())

    await state.clear()

@router.message(F.contact)
async def handle_unexpected_contact(message: Message):
    await message.answer(
        "📞 В данный момент приём контактов не активен.\n"
        "Перезапустите бота командой /start"
    )

@router.callback_query(F.data.startswith("orders_"))
async def show_user_orders(callback: CallbackQuery):
    db_gen = get_db()
    db = next(db_gen)
    user_id = int(callback.data.split("_")[-1])
    orders = get_orders_by_user(db, user_id)

    if not orders:
        await callback.message.edit_text("📭 Нет заказов.", reply_markup=return_profile_edit_kb())
        return

    text = "📋 <b>Список заказов:</b>\n\n"


    await callback.message.edit_text(text, reply_markup=get_user_orders_kb(orders, user_id), parse_mode="HTML")




@router.callback_query(F.data.startswith("user_order_"))
async def show_user_order_details(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[-1])

    db_gen = get_db()
    db = next(db_gen)
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    user_id = order.user_id

    if not order:
        await callback.answer("❌ Заказ не найден.")
        return

    text = f"📄 <b>Заказ № {order.order_number}</b>\n\n"
    text += f"👤 ФИО: {order.customer_name}\n"
    text += f"📱 Телефон: {order.customer_phone}\n"
    text += f"📍 Адрес доставки: {order.customer_address}\n"
    text += f"💰 Сумма: {order.total_amount}₽\n"
    text += f"🚚 Доставка: {order.delivery_method}\n"
    text += f"📊 Статус: {order.status}\n"
    text += f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    # Показываем товары
    if order.items:
        text += f"📦 Товары в заказе:\n"
        for item in order.items:
            # Показываем название товара и количество
            text += f"• {item.product.name} - {item.quantity}x{item.price} = {item.quantity * item.price}\n"
    else:
        text += f"📦 Товары в заказе: не указаны\n"

    if order.status == "new":
        await callback.message.edit_text(text, reply_markup=kb_with_cancel(order_id, user_id), parse_mode="HTML")
    else:
        await callback.message.edit_text(text, reply_markup=order_details_kb(order_id, user_id), parse_mode="HTML")


@router.callback_query(F.data.startswith("cancelling_"))
async def cancelling_order(callback: CallbackQuery):
    data = callback.data.split("_")
    order_id = int(data[-1])

    db_gen = get_db()
    db = next(db_gen)
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        await callback.answer("❌ Заказ не найден.")
        return

    status = order.status
    user_id = order.user_id
    updated_order = user_cancel_order(db, order_id, status)

    if updated_order:
        await callback.answer(f"✅ Заказ отменен")

        try:
            await callback.message.delete()
        except:
            pass  # Игнорируем ошибку, если сообщение уже удалено

        # ✅ ОТПРАВЛЯЕМ НОВОЕ СООБЩЕНИЕ
        text = f"📄 <b>Заказ № {updated_order.order_number}</b>\n\n"
        text += f"👤 ФИО: {updated_order.customer_name}\n"
        text += f"📱 Телефон: {updated_order.customer_phone}\n"
        text += f"📍 Адрес доставки: {updated_order.customer_address}\n"
        text += f"💰 Сумма заказ: {updated_order.total_amount}₽\n"
        text += f"🚚 Доставка: {updated_order.delivery_method}\n"
        text += f"📊 Статус: {updated_order.status}\n"
        text += f"📅 Дата: {updated_order.created_at.strftime('%d.%m.%Y %H:%M')}\n"

        # Показываем товары
        if updated_order.items:
            text += f"📦 Товары в заказе:\n"
            for item in updated_order.items:
                text += f"• {item.product.name} - {item.quantity}x{item.price} = {item.quantity * item.price}\n"
        else:
            text += f"📦 Товары в заказе: не указаны\n"

        await callback.message.answer(text, reply_markup=order_details_kb(order_id, user_id), parse_mode="HTML")
    else:
        await callback.answer("❌ Ошибка при изменении статуса")