import telebot
from telebot import types
import sqlite3


TOKEN = "8111206814:AAH161P_-hRREUD-hOn-CRDQdyOOz8K3dzE"
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("rent_bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    rooms INTEGER,
    price INTEGER,
    address TEXT,
    photo BLOB,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
"""
)
conn.commit()

user_data = {}


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("➕ Додати оголошення"))
    markup.add(types.KeyboardButton("🏠 Пошук житла"))
    markup.add(types.KeyboardButton("📋 Мої оголошення"))
    markup.add(types.KeyboardButton("📞 Контакти"))
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Вітаю! Обирайте дію:", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "➕ Додати оголошення")
def add_property(message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Квартира"), types.KeyboardButton("Будинок"))
    bot.send_message(
        message.chat.id, "🏠 Виберіть тип нерухомості:", reply_markup=markup
    )
    bot.register_next_step_handler(message, process_type)


def process_type(message):
    if message.text not in ["Квартира", "Будинок"]:
        bot.send_message(
            message.chat.id, "⚠ Будь ласка, оберіть із запропонованих варіантів."
        )
        return add_property(message)

    user_data[message.chat.id]["type"] = message.text
    bot.send_message(message.chat.id, "🛏 Введіть кількість кімнат (число):")
    bot.register_next_step_handler(message, process_rooms)


def process_rooms(message):
    try:
        rooms = int(message.text)
        if rooms <= 0:
            raise ValueError
        user_data[message.chat.id]["rooms"] = rooms
        bot.send_message(message.chat.id, "💵 Введіть ціну у $ (число):")
        bot.register_next_step_handler(message, process_price)
    except ValueError:
        bot.send_message(
            message.chat.id, "⚠ Будь ласка, введіть коректне число кімнат!"
        )
        bot.register_next_step_handler(message, process_rooms)


def process_price(message):
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError
        user_data[message.chat.id]["price"] = price
        bot.send_message(message.chat.id, "📍 Введіть адресу:")
        bot.register_next_step_handler(message, process_address)
    except ValueError:
        bot.send_message(message.chat.id, "⚠ Будь ласка, введіть коректну ціну!")
        bot.register_next_step_handler(message, process_price)


def process_address(message):
    if not message.text.strip():
        bot.send_message(message.chat.id, "⚠ Будь ласка, введіть адресу!")
        bot.register_next_step_handler(message, process_address)
        return

    user_data[message.chat.id]["address"] = message.text.strip()
    bot.send_message(message.chat.id, "📸 Надішліть фото об'єкта:")
    bot.register_next_step_handler(message, process_photo)


def process_photo(message):
    try:
        if not message.photo:
            bot.send_message(message.chat.id, "⚠ Будь ласка, надішліть фото.")
            bot.register_next_step_handler(message, process_photo)
            return

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        cursor.execute(
            """
        INSERT INTO properties (user_id, type, rooms, price, address, photo) 
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                message.chat.id,
                user_data[message.chat.id]["type"],
                user_data[message.chat.id]["rooms"],
                user_data[message.chat.id]["price"],
                user_data[message.chat.id]["address"],
                downloaded_file,
            ),
        )
        conn.commit()

        # Очищаємо тимчасові дані
        del user_data[message.chat.id]

        bot.send_message(
            message.chat.id, "✅ Оголошення додано!", reply_markup=main_menu()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            "⚠ Сталася помилка при додаванні оголошення. Спробуйте ще раз.",
            reply_markup=main_menu(),
        )


@bot.message_handler(func=lambda message: message.text == "🏠 Пошук житла")
def search_property(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Квартири", callback_data="type_Квартира"))
    markup.add(types.InlineKeyboardButton("Будинки", callback_data="type_Будинок"))
    bot.send_message(message.chat.id, "Оберіть тип житла:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("type_"))
def callback_query(call):
    try:
        property_type = call.data.split("_")[1]
        cursor.execute("SELECT * FROM properties WHERE type=?", (property_type,))
        properties = cursor.fetchall()
        if not properties:
            bot.send_message(call.message.chat.id, "Немає доступних варіантів.")
            return
        for prop in properties:
            text = f"📍 Адреса: {prop[5]}\n🏘 Кімнат: {prop[3]}\n💵 Ціна: {prop[4]} $"
            if prop[6]:  # Якщо є фото
                try:
                    bot.send_photo(call.message.chat.id, photo=prop[6], caption=text)
                except Exception as e:
                    bot.send_message(call.message.chat.id, text)
            else:
                bot.send_message(call.message.chat.id, text)
    except Exception as e:
        bot.send_message(call.message.chat.id, "⚠ Сталася помилка при пошуку.")


@bot.message_handler(func=lambda message: message.text == "📋 Мої оголошення")
def my_properties(message):
    try:
        cursor.execute("SELECT * FROM properties WHERE user_id=?", (message.chat.id,))
        properties = cursor.fetchall()

        if not properties:
            bot.send_message(message.chat.id, "❌ У вас немає доданих оголошень.")
            return

        for prop in properties:
            text = f"📍 Адреса: {prop[5]}\n🏘 Кімнат: {prop[3]}\n💵 Ціна: {prop[4]} $"
            if prop[6]:
                try:
                    bot.send_photo(message.chat.id, photo=prop[6], caption=text)
                except Exception as e:
                    bot.send_message(message.chat.id, text)
            else:
                bot.send_message(message.chat.id, text)
    except Exception as e:
        bot.send_message(message.chat.id, "⚠ Сталася помилка. Спробуйте пізніше.")


@bot.message_handler(func=lambda message: message.text == "📞 Контакти")
def ask_phone(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 Надати номер", request_contact=True))
    bot.send_message(
        message.chat.id,
        "Будь ласка, поділіться своїм номером телефону:",
        reply_markup=markup,
    )


@bot.message_handler(content_types=["contact"])
def save_contact(message):
    try:
        cursor.execute(
            """
        INSERT OR REPLACE INTO users (id, username, first_name, last_name, phone) 
        VALUES (?, ?, ?, ?, ?)
        """,
            (
                message.chat.id,
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.last_name,
                message.contact.phone_number,
            ),
        )
        conn.commit()
        bot.send_message(
            message.chat.id, "✅ Ваш номер збережено!", reply_markup=main_menu()
        )
    except Exception as e:
        bot.send_message(message.chat.id, "⚠ Виникла помилка. Спробуйте ще раз.")


if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        conn.close()
