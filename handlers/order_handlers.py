from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.crud import add_to_cart, get_cart_items
from database.db_helper import get_db
from keyboards.inline_keyboards import get_cart_kb, get_product_view_kb, get_back_to_menu_kb
from database.models import CartItem, Product
from aiogram.types import InputMediaPhoto

router = Router()

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart_handler(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)

    # Добавляем товар в корзину (если есть — увеличиваем количество)
    add_to_cart(db, user_id, product_id, quantity=1)

    await callback.answer("✅ Товар добавлен в корзину!", show_alert=False)
    # Обновляем клавиатуру под товаром — можно добавить счётчик
    # Пока просто закрываем уведомление


@router.callback_query(F.data == "open_cart")
async def show_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    db_gen = get_db()
    db = next(db_gen)
    items = get_cart_items(db, user_id)

    if not items:
        text = "🛒 Ваша корзина пуста."
        await callback.message.edit_media(
            media=InputMediaPhoto(media="https://static.insales-cdn.com/files/1/5466/40031578/original/Logo_Only_Black__1___1_.png", caption=text),
            reply_markup=get_back_to_menu_kb()
        )
        return

    text = "🛒 <b>Ваша корзина:</b>\n\n"
    # total = 0.0
    # for item in items:
    #     subtotal = item.product.price * item.quantity
    #     total += subtotal
    #     text += f"▪️ {item.product.name}\n"
    #     text += f"   {item.quantity} × {item.product.price:.0f}₽ = <b>{subtotal:.0f}₽</b>\n\n"
    # text += f"💳 <b>Итого: {total:.0f}₽</b>"

    await callback.message.edit_media(
        media=InputMediaPhoto(media="https://static.insales-cdn.com/files/1/5466/40031578/original/Logo_Only_Black__1___1_.png", caption=text),
        reply_markup=get_cart_kb(items)
    )

@router.callback_query(F.data == "open_cart_from_product")
async def open_cart_from_product(callback: CallbackQuery):
    await callback.answer()  # Закрываем "часики"
    await show_cart(callback)  # Открываем корзину

@router.callback_query(F.data.startswith("incr_"))
async def increase_quantity(callback: CallbackQuery):
    cart_item_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)

    # Увеличиваем количество на 1
    item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == user_id).first()
    if item:
        item.quantity += 1
        db.commit()
        await callback.answer("➕ Товар добавлен")

    # Обновляем корзину
    await show_cart(callback)

@router.callback_query(F.data.startswith("decr_"))
async def decrease_quantity(callback: CallbackQuery):
    cart_item_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)

    item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == user_id).first()
    if item:
        if item.quantity > 1:
            item.quantity -= 1
            db.commit()
            await callback.answer("➖ Товар убран")
        else:
            db.delete(item)
            db.commit()
            await callback.answer("❌ Товар удалён")

    # Обновляем корзину
    await show_cart(callback)

@router.callback_query(F.data.startswith("remove_"))
async def remove_item(callback: CallbackQuery):
    cart_item_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    db_gen = get_db()
    db = next(db_gen)

    item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == user_id).first()
    if item:
        db.delete(item)
        db.commit()
        await callback.answer("❌ Товар удалён")

    # Обновляем корзину
    await show_cart(callback)

@router.callback_query(F.data.startswith("view_product_"))
async def view_product_in_cart(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[-1])
    db_gen = get_db()
    db = next(db_gen)
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        await callback.answer("Товар не найден.")
        return

    text = f"📦 {product.name}\n\n"
    text += f"💰 {product.price}₽\n"
    text += f"📝 {product.description or 'Описание отсутствует'}"

    # Редактируем текущее сообщение — заменяем текст и клавиатуру
    if product.photo_url:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=product.photo_url, caption=text),
            reply_markup=get_product_view_kb(product_id)
        )
    else:
        await callback.message.edit_text(text, reply_markup=get_product_view_kb(product_id))

@router.callback_query(F.data == "back_to_cart")
async def back_to_cart(callback: CallbackQuery):
    await show_cart(callback)  # Переключаемся обратно в корзину