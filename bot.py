import telebot
import buttons as bt
from geopy.geocoders import Photon
import database as db
#db.add_product("Бургер", 30000, "лучший бургер", 20, "https://menunedeli.ru/wp-content/uploads/2023/07/4523862E-973D-49D0-BE99-2609DDAA5CF4-933x700.jpeg")
#db.add_product("Чизбургер", 35000, "лучший чизбургер", 20, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR7lfdGQENwsxIWcpk80o43dRz2V8jN9pBK_w&s")
#db.add_product("Хот-дог", 15000, "лучший хотдог", 0, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSsfW388zWeoTBoYVtL5yJi85sJmFoVB3isLw&s")

bot = telebot.TeleBot(token="7927478236:AAEaWaz1v2rNK9W5Oc2cZ7PPRjDhaZZMUHk")
geolocator = Photon(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
users = {}
admin_id = -4578355993
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    checker = db.check_user(user_id)
    if checker == True:
        bot.send_message(user_id, "Главное меню", reply_markup=bt.main_menu_bt())
    elif checker == False:
        bot.send_message(user_id, "Добро пожаловать в наш бот доставки!\n"
                                  "Напишите своё имя")
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(user_id, "Поделитесь своими контактами",
                     reply_markup=bt.phone_number_bt())
    bot.register_next_step_handler(message, get_number, name)

def get_number(message, name):
    user_id = message.from_user.id
    if message.contact:
        phone_number = message.contact.phone_number
        bot.send_message(user_id, f"{name}, вы успешно зарегистрированы!\n"
                                  "Выберите действие из меню", reply_markup=bt.main_menu_bt())
        db.add_user(name, phone_number, user_id)
    else:
        bot.send_message(user_id, "Отправьте свой номер через кнопку в меню",
                         reply_markup=bt.phone_number_bt())
        bot.register_next_step_handler(message, get_number, name)
def get_location(message):
    user_id = message.from_user.id
    if message.location:
        longitude = message.location.longitude
        latitude = message.location.latitude
        address = geolocator.reverse((latitude, longitude)).address
        print(address)
@bot.callback_query_handler(lambda call: call.data in ["back", "main_menu", "cart", "plus", "minus",
                                                       "to_cart", "clear_cart", "order"])
def all_calls(call):
    user_id = call.message.chat.id
    if call.data == "main_menu":
        bot.delete_message(user_id, call.message.id)
        bot.send_message(user_id, "Главное меню", reply_markup=bt.main_menu_bt())
    elif call.data == "back" or call.data == "main_menu":
        bot.delete_message(user_id, call.message.id)
        bot.send_message(user_id, "Главное меню", reply_markup=bt.main_menu_bt())
    elif call.data == "plus":
        current_amount = users[user_id]["pr_count"]
        users[user_id]["pr_count"] += 1
        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                      reply_markup=bt.exact_product_in(current_amount=current_amount,
                                                                       plus_or_minus="plus"))
    elif call.data == "minus":
        current_amount = users[user_id]["pr_count"]
        if current_amount > 1:
            users[user_id]["pr_count"] -= 1
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                          reply_markup=bt.exact_product_in(current_amount=current_amount,
                                                                           plus_or_minus="minus"))
    elif call.data == "to_cart":
        db.add_to_cart(user_id=user_id, pr_id=users[user_id]["pr_id"], pr_name=users[user_id]["pr_name"],
                       pr_count=users[user_id]["pr_count"], pr_price=users[user_id]["pr_price"])
        users.pop(user_id)
        bot.delete_message(user_id, call.message.id)
        all_product = db.get_pr_id_name()
        bot.send_message(user_id, "Продукт добавлен в корзину. "
                                  "Желаете заказать что-нибудь еще?", reply_markup=bt.products_in(all_product))
    elif call.data == "clear_cart":
        db.delete_user_cart(user_id)
        bot.delete_message(user_id, call.message.id)
        all_product = db.get_pr_id_name()
        bot.send_message(user_id, "Корзина очищена. Выберите новые продукты",
                         reply_markup=bt.products_in(all_product))
    elif call.data == "order":
        bot.delete_message(user_id, call.message.id)
        user_cart = db.get_user_cart(user_id)
        full_text = f"Новый заказ от пользователя {user_id}: \n\n"
        total_amount = 0
        for i in user_cart:
            full_text += f"{i[0]} x {i[1]} = {i[2]}\n"
            total_amount += i[2]
        full_text += f"\n\n Итоговая сумма заказа: {total_amount} сум"
        bot.send_message(admin_id, full_text)
        bot.send_message(user_id, "Ваш заказ принят. Ожидайте подтверждения")
        db.delete_user_cart(user_id)




@bot.callback_query_handler(lambda call: "prod_" in call.data)
def product_call(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    product_id = int(call.data.replace("prod_", ""))
    product_info = db.get_exact_product(product_id)
    users[user_id] = {"pr_id": product_id, "pr_name": product_info[0],
                      "pr_count": 1, "pr_price": product_info[1]}
    text = (f"{product_info[0]}\n\n"
            f"Описание: {product_info[2]}\n"
            f"Цена: {product_info[1]} сум")
    bot.send_photo(user_id, photo=product_info[3], caption=text,
                   reply_markup=bt.exact_product_in())


@bot.message_handler(content_types=["text"])
def main_menu(message):
    user_id = message.from_user.id
    if message.text == "🍴Меню":
        all_product = db.get_pr_id_name()
        bot.send_message(user_id, "Меню", reply_markup=bt.products_in(all_product))
    elif message.text == "🛒Корзина":
        user_cart = db.get_user_cart(user_id)
        full_text = f"Ваша корзина: \n\n"
        total_amount = 0
        for i in user_cart:
            full_text += f"{i[0]} x {i[1]} = {i[2]}\n"
            total_amount += i[2]
        full_text += f"\n\n Итоговая сумма заказа: {total_amount} сум"
        bot.send_message(user_id, full_text, reply_markup=bt.get_cart_kb())
    elif message.text == "❗️Отзыв":
        bot.send_message(user_id, "Напишите текст вашего отзыва")


bot.infinity_polling()