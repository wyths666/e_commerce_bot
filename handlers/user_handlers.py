from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.crud import get_categories, get_products_by_category
from database.db_helper import get_db
from keyboards.inline_keyboards import get_categories_kb, get_main_menu_kb,  get_product_navigation_kb
from aiogram.types import InputMediaPhoto

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в наш магазин!\nВыберите действие:",
        reply_markup=get_main_menu_kb()
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer("👋 Добро пожаловать в наш магазин!\nВыберите действие:",
        reply_markup=get_main_menu_kb())
    await callback.message.delete()


@router.callback_query(F.data == "open_catalog")
async def show_categories(callback: CallbackQuery):
    await callback.answer()  # Закрываем "часики" на кнопке
    db_gen = get_db()
    db = next(db_gen)
    categories = get_categories(db)
    if not categories:
        await callback.message.answer("К сожалению, каталог пуст.")
        return
    kb = get_categories_kb(categories)
    await callback.message.answer("📂 Выберите категорию:", reply_markup=kb)
    # Опционально: удалить предыдущее сообщение
    await callback.message.delete()

@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    db_gen = get_db()
    db = next(db_gen)
    products = get_products_by_category(db, category_id)

    if not products:
        await callback.message.edit_text("В этой категории пока нет товаров.")
        return

    # Показываем первый товар (индекс 0)
    await show_product_by_index(callback, category_id, 0, products)

async def show_product_by_index(callback: CallbackQuery, category_id: int, index: int, products: list):
    product = products[index]
    total = len(products)

    text = f"📦 {product.name}\n\n"
    text += f"💰 {product.price}₽\n"
    text += f"📝 {product.description or 'Описание отсутствует'}\n"
    text += f"\n📋 Товар {index + 1} из {total}"

    # Клавиатура: предыдущий / следующий / добавить / назад
    kb = get_product_navigation_kb(category_id, index, total, product.id)

    if product.photo_url:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=product.photo_url, caption=text),
            reply_markup=kb
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=kb)(product.id)

@router.callback_query(F.data.startswith("nav_"))
async def navigate_products(callback: CallbackQuery):
    data = callback.data.split("_")
    category_id = int(data[1])
    index = int(data[2])

    db_gen = get_db()
    db = next(db_gen)
    products = get_products_by_category(db, category_id)

    if not products or index < 0 or index >= len(products):
        await callback.answer("Ошибка навигации", show_alert=True)
        return

    await show_product_by_index(callback, category_id, index, products)

