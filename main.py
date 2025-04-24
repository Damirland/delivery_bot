import telebot
from telebot import types
import json

TOKEN = "7811520905:AAEQ7OEK88ddKPDge48yRRhu2Bv0HRZJV2c"
bot = telebot.TeleBot(TOKEN)

carts = {}

ITEMS_PER_PAGE = 4

menu_items = [
    {"name": "Грибной суп", "price": "450 руб.", "photo": "mushroom_soup.png"},
    {"name": "Салат Цезарь", "price": "550 руб.", "photo": "caesar.png"},
    {"name": "Утка с апельсинами", "price": "700 руб.", "photo": "duck_orange.png"},
    {"name": "Бефстроганов", "price": "650 руб.", "photo": "stroganoff.png"},
    {"name": "Ризотто", "price": "500 руб.", "photo": "risotto.png"},
    {"name": "Тирамису", "price": "400 руб.", "photo": "tiramisu.png"},
    {"name": "Блины", "price": "300 руб.", "photo": "pancakes.png"},
    {"name": "Паста Карбонара", "price": "550 руб.", "photo": "carbonara.png"},
    {"name": "Гаспачо", "price": "350 руб.", "photo": "gazpacho.png"},
    {"name": "Фалафель", "price": "400 руб.", "photo": "falafel.png"}]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, text=message.chat.id)
    bot.send_message(message.chat.id, "Основное меню:", reply_markup=selection())


def selection():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton("Меню🍜")
    btn2 = types.KeyboardButton("Корзина🧺")
    btn3 = types.KeyboardButton("Заказать✅")

    markup.add(btn1, btn2, btn3)
    return markup


def generate_markup(page=0):
    markup = types.InlineKeyboardMarkup()
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    for food in menu_items[start_index:end_index]:
        button = types.InlineKeyboardButton(f"{food["name"]}: {food["price"]}",
                                            callback_data=f"item_{menu_items.index(food)}")
        markup.add(button)

    if page > 0:
        markup.add(types.InlineKeyboardButton(text="<<", callback_data=f"page_{page - 1}"))
    if end_index < len(menu_items):
        markup.add(types.InlineKeyboardButton(text=">>", callback_data=f"page_{page + 1}"))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(call.id)
    if call.data.startswith('page_'):
        _, page = call.data.split('_')
        markup = generate_markup(int(page))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Выберите элемент:", reply_markup=markup)
    elif call.data.startswith('item_'):
        _, item_index = call.data.split('_')
        add_to_cart(call.message.chat.id, menu_items[int(item_index)])
        bot.send_message(call.message.chat.id, f'{menu_items[int(item_index)]["name"]} добавлено в заказ')


def add_to_cart(client_id, item):
    with open("data.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            for cart_item in client["id"]:
                if cart_item[0] == item:
                    cart_item[1] += 1
            else:
                client["cart"].append([item, 1])

    with open("data.json", 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def delete_from_cart(client_id, item):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            for cart_item in client["id"]:
                if cart_item[1] != 1:
                    if cart_item[0] == item:
                        cart_item[1] -= 1
                else:
                    client["cart"].remove([item, 1])
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def button_basket(message):
    items_in_cart = get_cart(message.chat.id)

    markup = types.InlineKeyboardMarkup()
    if items_in_cart:
        for item in items_in_cart:
            minus_button = types.InlineKeyboardButton("-", callback_data=f"minus_{item}")
            name_button = types.InlineKeyboardButton(f"{item[0]} x{item[1]}", callback_data=f"name_{item}")
            plus_button = types.InlineKeyboardButton("+", callback_data=f"plus_{item}")

            markup.add(minus_button, name_button, plus_button)
        return markup


def get_cart(client_id):
    with open("data.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            return client.get("cart", [])

    return None


# def get_username(message):
#     chat_id = message.chat.id
#     user_info[chat_id]['name'] = message.text
#     msg = bot.send_message(chat_id, "Введите ваш номер телефона:")
#     bot.register_next_step_handler(msg, get_phone_number)
#
#
# def get_phone_number(message):
#     chat_id = message.chat.id
#     user_info[chat_id]['phone'] = message.text
#     bot.send_message(chat_id,
#                      f"Ваше имя: {user_info[chat_id]['name']}\nВаш номер телефона: {user_info[chat_id]['phone']}")


# @bot.message_handler(commands=["add_info"])
# def add_info(message):
#     user_info[message.chat.id] = {}
#     msg = bot.send_message(message.chat.id, "Введите ваше имя:")
#     bot.register_next_step_handler(msg, get_username)
#
#
# def user_save(message, client_id, item):
#     with open('data.json', 'r', encoding='utf-8') as file:
#         data = json.load(file)
#
#     # Сохраняем имя пользователя
#     clients = data.get("clients", [])
#     for client in clients:
#         if client.get("id") == str(client_id):
#             for cart_item in client["id"]:
#                 if cart_item[0] == item:
#                     cart_item[1] += 1
#             else:
#                 client["cart"].append([item, 1])
#
#     # Запись обновленных данных в файл
#     with open('data.json', 'w', encoding='utf-8') as file:
#         json.dump(data, file, ensure_ascii=False)
#
#     bot.send_message(message.chat.id, "Ваше имя сохранено")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "Меню🍜":
        bot.send_message(message.chat.id, "Выберите блюдо:", reply_markup=generate_markup())

    elif message.text == "Корзина🧺":
        items_in_cart = get_cart(message.chat.id)

        markup = types.InlineKeyboardMarkup()
        for item in items_in_cart:
            minus_button = types.InlineKeyboardButton("-", callback_data=f"minus_{item}")
            name_button = types.InlineKeyboardButton(f"{item[0]} x{item[1]}", callback_data=f"name_{item}")
            plus_button = types.InlineKeyboardButton("+", callback_data=f"plus_{item}")

            markup.add(minus_button, name_button, plus_button)

        bot.send_message(message.chat.id, "Корзина:", reply_markup=markup)
    elif message.text == "Заказать✅":
        items = get_cart(message.chat.id)
        text = "Ваша корзина:\n"
        for item in items:
            text += "✨ " + str(items[0]["name"]) + " x" + str(items[1]["price"]) + "\n"
        bot.send_message(message.chat.id, text)
        bot.send_message(message.chat.id, "Подтвердите правильность заказа.")


bot.polling(none_stop=True)
