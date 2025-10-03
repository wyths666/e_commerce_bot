from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from database.crud import get_all_orders, update_order_status, get_categories
from database.db_helper import get_db
from keyboards.admin_keyboards import get_admin_menu_kb, get_orders_kb, get_order_status_kb, get_product_edit_kb, get_products_list_kb
from states.admin_states import AddProduct, EditProduct
from database.models import Order, Product
from config import ADMIN_IDS
router = Router()



@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ запрещён.")
        return

    await message.answer("🛡 Административная панель", reply_markup=get_admin_menu_kb())

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer("🛡 Административная панель", reply_markup=get_admin_menu_kb())
    await callback.message.delete()

@router.callback_query(F.data == "admin_orders")
async def show_orders(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    db_gen = get_db()
    db = next(db_gen)
    orders = get_all_orders(db)

    if not orders:
        await callback.message.edit_text("📭 Нет заказов.", reply_markup=get_admin_menu_kb())
        return

    text = "📋 <b>Список заказов:</b>\n\n"
    for order in orders:
        text += f"📄 {order.order_number}\n"
        text += f"💰 {order.total_amount}₽\n"
        text += f"🚚 {order.delivery_method}\n"
        text += f"📊 Статус: {order.status}\n"
        text += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += "─" * 20 + "\n"

    await callback.message.edit_text(text, reply_markup=get_orders_kb(orders), parse_mode="HTML")


@router.callback_query(F.data.startswith("admin_order_"))
async def show_order_details(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return
    statuses = {"new": "В обработке", "confirmed": "Подтвержден", "delivered": "Отправлен", "cancelled": "Отменен"}
    order_id = int(callback.data.split("_")[-1])

    db_gen = get_db()
    db = next(db_gen)
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        await callback.answer("❌ Заказ не найден.")
        return

    text = f"📄 <b>Заказ № {order.order_number}</b>\n\n"
    text += f"👤 Имя: {order.customer_name}\n"
    text += f"📱 Телефон: {order.customer_phone}\n"
    text += f"📍 Адрес: {order.customer_address}\n"
    text += f"💰 Сумма: {order.total_amount}₽\n"
    text += f"🚚 Доставка: {order.delivery_method}\n"
    text += f"📊 Статус: {statuses[order.status]}\n"
    text += f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"

    await callback.message.edit_text(text, reply_markup=get_order_status_kb(order_id, order.status), parse_mode="HTML")


@router.callback_query(F.data.startswith("status_"))
async def change_order_status(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    data = callback.data.split("_")
    if len(data) < 3 or not data[2].isdigit():
        await callback.answer("❌ Неверный формат данных.")
        return

    order_id = int(data[2])
    new_status = data[1]

    db_gen = get_db()
    db = next(db_gen)
    order = update_order_status(db, order_id, new_status)

    if order:
        await callback.answer(f"✅ Статус изменён на {new_status}")
        # Обновляем клавиатуру
        await show_order_details(callback)
    else:
        await callback.answer("❌ Ошибка при изменении статуса")


@router.callback_query(F.data == "admin_add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    await callback.message.edit_text("📦 Введите название товара:")
    await state.set_state(AddProduct.name)


@router.message(AddProduct.name)
async def process_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📝 Введите описание товара:")
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description)
async def process_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Введите цену товара:")
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("🖼 Отправьте фото товара:")
        await state.set_state(AddProduct.photo)
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")


@router.message(AddProduct.photo, F.photo)
async def process_product_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)

    # Получаем категории
    db_gen = get_db()
    db = next(db_gen)
    categories = get_categories(db)

    if not categories:
        await message.answer("❌ Нет категорий. Сначала создайте категории.")
        await state.clear()
        return

    text = "📂 Выберите категорию:"
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=cat.name, callback_data=f"cat_{cat.id}")])

    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(AddProduct.category)


@router.callback_query(AddProduct.category, F.data.startswith("cat_"))
async def process_product_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category=category_id)

    # Сохраняем товар
    data = await state.get_data()

    db_gen = get_db()
    db = next(db_gen)

    product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        photo_url=data['photo'],
        category_id=data['category']
    )

    db.add(product)
    db.commit()

    await callback.message.edit_text("✅ Товар успешно добавлен!", reply_markup=get_admin_menu_kb())
    await state.clear()


@router.callback_query(F.data == "admin_products")
async def show_products_list(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    db_gen = get_db()
    db = next(db_gen)
    products = db.query(Product).all()

    if not products:
        await callback.message.edit_text("📭 Нет товаров.", reply_markup=get_admin_menu_kb())
        return

    text = "📦 <b>Список товаров:</b>\n\n"
    # for product in products:
    #     text += f"🆔 {product.id} - {product.name}\n"
    #     text += f"💰 {product.price}₽\n"
    #     text += f"📂 {product.category.name if product.category else 'Без категории'}\n"
    #     text += "─" * 20 + "\n"

    #await callback.message.edit_text(text, reply_markup=get_products_list_kb(products), parse_mode="HTML")
    await callback.message.answer(text, reply_markup=get_products_list_kb(products), parse_mode="HTML")

# =========== Блок редактирования товаров =============
async def show_product_card(message, product, reply_markup=None):
    text = f"📦 <b>Редактирование товара:</b>\n\n"
    text += f"🆔 ID: {product.id}\n"
    text += f"🏷 Название: {product.name}\n"
    text += f"📝 Описание: {product.description or '—'}\n"
    text += f"💰 Цена: {product.price}₽\n"
    text += f"📂 Категория: {product.category.name if product.category else '—'}\n"

    # Если есть фото — отправляем фото с подписью
    if product.photo_url:
        await message.answer_photo(
            photo=product.photo_url,
            caption=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        # Если нет фото — отправляем обычный текст
        await message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("edit_product_"))
async def edit_product(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    product_id = int(callback.data.split("_")[2])

    db_gen = get_db()
    db = next(db_gen)
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        await callback.answer("❌ Товар не найден.")
        return
    await show_product_card(callback.message, product, get_product_edit_kb(product_id))



# =========== изменение наименования==============
@router.callback_query(F.data.startswith("edit_name_"))
async def start_edit_description(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    product_id = int(callback.data.split("_")[2])
    await state.update_data(editing_product_id=product_id)
    await callback.answer("✏️ Введите новое наименование в следующем сообщении:")
    await state.set_state(EditProduct.name)


@router.message(EditProduct.name)
async def process_edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['editing_product_id']

    db_gen = get_db()
    db = next(db_gen)
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        product.name = message.text
        db.commit()

        # Показываем alert
        await message.answer("✅ Описание обновлено!")

    await state.clear()

    # Возвращаемся к редактированию товара
    fake_callback = type('Callback', (), {
        'from_user': message.from_user,
        'message': message,
        'data': f'edit_product_{product_id}'
    })
    await edit_product(fake_callback)


# =========== изменение описания =============

@router.callback_query(F.data.startswith("edit_desc_"))
async def start_edit_description(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    product_id = int(callback.data.split("_")[2])
    await state.update_data(editing_product_id=product_id)
    await callback.answer("✏️ Введите новое описание в следующем сообщении:")
    await state.set_state(EditProduct.description)


@router.message(EditProduct.description)
async def process_edit_description(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['editing_product_id']

    db_gen = get_db()
    db = next(db_gen)
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        product.description = message.text
        db.commit()

        # Показываем alert
        await message.answer("✅ Описание обновлено!")

    await state.clear()

    # Возвращаемся к редактированию товара
    fake_callback = type('Callback', (), {
        'from_user': message.from_user,
        'message': message,
        'data': f'edit_product_{product_id}'
    })
    await edit_product(fake_callback)


# =========== изменение цены =============

@router.callback_query(F.data.startswith("edit_price_"))
async def start_edit_price(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    product_id = int(callback.data.split("_")[2])
    await state.update_data(editing_product_id=product_id)
    await callback.answer("💰 Введите новую цену товара:")
    await state.set_state(EditProduct.price)


@router.message(EditProduct.price)
async def process_edit_price(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['editing_product_id']

    try:
        price = float(message.text)

        db_gen = get_db()
        db = next(db_gen)
        product = db.query(Product).filter(Product.id == product_id).first()

        if product:
            product.price = price
            db.commit()
            await message.answer("✅ Цена обновлена!")

        await state.clear()
        fake_callback = type('Callback', (), {
            'from_user': message.from_user,
            'message': message,
            'data': f'edit_product_{product_id}'
        })
        await edit_product(fake_callback)
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")

# =========== изменение фото =============

@router.callback_query(F.data.startswith("edit_photo_"))
async def start_edit_photo(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    product_id = int(callback.data.split("_")[2])
    await state.update_data(editing_product_id=product_id)
    await callback.message.answer("🖼 Отправьте новое фото товара:")
    await state.set_state(EditProduct.photo)


@router.message(EditProduct.photo, F.photo)
async def process_edit_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['editing_product_id']

    photo_id = message.photo[-1].file_id

    db_gen = get_db()
    db = next(db_gen)
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        product.photo_url = photo_id
        db.commit()
        await message.answer("✅ Фото обновлено!")

        await show_product_card(message, product, get_product_edit_kb(product_id))
    else:
        await message.answer("❌ Товар не найден.")

    await state.clear()


# =========== изменение категории =============

@router.callback_query(F.data.startswith("edit_category_"))
async def start_edit_category(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    product_id = int(callback.data.split("_")[2])
    await state.update_data(editing_product_id=product_id)

    # Получаем категории
    db_gen = get_db()
    db = next(db_gen)
    categories = get_categories(db)

    if not categories:
        await callback.message.edit_text("❌ Нет категорий.")
        await state.clear()
        return

    text = "📂 Выберите новую категорию:"
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=cat.name, callback_data=f"newcat_{product_id}_{cat.id}")])

    #await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data.startswith("newcat_"))
async def process_edit_category(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    data = callback.data.split("_")
    product_id = int(data[1])
    category_id = int(data[2])

    db_gen = get_db()
    db = next(db_gen)
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        product.category_id = category_id
        db.commit()
        await callback.answer("✅ Категория обновлена!")

    # Возвращаемся к редактированию товара
    fake_callback = type('Callback', (), {
        'from_user': callback.from_user,
        'message': callback.message,
        'data': f'edit_product_{product_id}'
    })
    await edit_product(fake_callback)

# =========== удаление товара =============
@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещён.")
        return

    product_id = int(callback.data.split("_")[2])

    db_gen = get_db()
    db = next(db_gen)
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        db.delete(product)
        db.commit()
        await callback.answer("✅ Товар удалён!")
    else:
        await callback.answer("❌ Товар не найден.")
        return

    try:
        await callback.message.delete()
    except:
        pass


    db_gen = get_db()
    db = next(db_gen)
    products = db.query(Product).all()

    if not products:
        await callback.message.answer("📭 Нет товаров.", reply_markup=get_admin_menu_kb())
        return

    text = "📦 <b>Список товаров:</b>\n\n"
    # for product in products:
    #     text += f"🆔 {product.id} - {product.name}\n"
    #     text += f"💰 {product.price}₽\n"
    #     text += f"📂 {product.category.name if product.category else 'Без категории'}\n"
    #     text += "─" * 20 + "\n"

    await callback.message.answer(text, reply_markup=get_products_list_kb(products), parse_mode="HTML")