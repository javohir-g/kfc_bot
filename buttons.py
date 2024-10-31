from telebot import types

def phone_number_bt():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Поделиться номером", request_contact=True)
    kb.add(button)
    return kb
def location_bt():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Поделиться локацией", request_location=True)
    kb.add(button)
    return kb
def main_menu_bt():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu = types.KeyboardButton(text="🍴Меню")
    cart = types.KeyboardButton(text="🛒Корзина")
    feedback = types.KeyboardButton(text="❗️Отзыв")
    kb.add(menu, cart, feedback)
    return kb
def products_in(all_products):
    kb = types.InlineKeyboardMarkup(row_width=2)
    # статичные кнопки
    cart = types.InlineKeyboardButton(text="Корзина", callback_data="cart")
    back = types.InlineKeyboardButton(text="Назад", callback_data="main_menu")
    # динамичные кнопки
    all_buttons = [types.InlineKeyboardButton(text=product[1], callback_data=f"prod_{product[0]}")
                   for product in all_products]
    kb.add(*all_buttons)
    kb.row(cart)
    kb.row(back)
    return kb
def exact_product_in(plus_or_minus="", current_amount=1):
    kb = types.InlineKeyboardMarkup(row_width=3)
    # статичные или постоянные кнопки
    add_to_cart = types.InlineKeyboardButton(text="Добавить в корзину", callback_data="to_cart")
    back = types.InlineKeyboardButton(text="Назад", callback_data="back")
    minus = types.InlineKeyboardButton(text="➖", callback_data="minus")
    plus = types.InlineKeyboardButton(text="➕", callback_data="plus")
    count = types.InlineKeyboardButton(text=f"{current_amount}", callback_data="none")
    # логика изменения кнопок
    if plus_or_minus == "plus":
        new_amount = current_amount + 1
        count = types.InlineKeyboardButton(text=f"{new_amount}", callback_data="none")
    elif plus_or_minus == "minus":
        if current_amount > 1:
            new_amount = current_amount - 1
            count = types.InlineKeyboardButton(text=f"{new_amount}", callback_data="none")
    kb.add(minus, count, plus)
    kb.row(add_to_cart)
    kb.row(back)
    return kb

def get_cart_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    clear = types.InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart")
    back = types.InlineKeyboardButton(text="Назад", callback_data="main_menu")
    order = types.InlineKeyboardButton(text="Оформить заказ", callback_data="order")
    kb.add(clear, order, back)
    return kb



