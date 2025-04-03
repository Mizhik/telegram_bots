import telebot
import requests
from datetime import datetime

TOKEN = "7724406657:AAHXM9LLQRWKy5qttmefyBtJX-4g4cLXT2U"
API_URL = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"  

bot = telebot.TeleBot(TOKEN)

ZODIAC_SIGNS = {
    "овен": "aries",
    "телець": "taurus",
    "близнюки": "gemini",
    "рак": "cancer",
    "лев": "leo",
    "діва": "virgo",
    "ваги": "libra",
    "скорпіон": "scorpio",
    "стрілець": "sagittarius",
    "козеріг": "capricorn",
    "водолій": "aquarius",
    "риби": "pisces",
}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)

    buttons = []
    for sign in ZODIAC_SIGNS.keys():
        buttons.append(telebot.types.KeyboardButton(sign.capitalize()))

    markup.add(*buttons)

    welcome_text = (
        "🔮 *Гороскоп на сьогодні*\n\n"
        "Оберіть свій знак зодіаку з клавіатури або напишіть його назву.\n\n"
        "Також доступні команди:\n"
        "/help - Довідка\n"
        "/today - Отримати гороскоп для вашого знаку\n"
        "/signs - Список усіх знаків зодіаку"
    )

    bot.send_message(
        message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown"
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = (
        "🌟 *Як користуватися ботом:*\n\n"
        "1. Оберіть свій знак зодіаку з клавіатури\n"
        "2. Або введіть назву знаку (наприклад, 'Овен')\n"
        "3. Бот надішле вам гороскоп на сьогодні\n\n"
        "Доступні команди:\n"
        "/start - Почати роботу з ботом\n"
        "/today - Отримати гороскоп\n"
        "/signs - Список знаків зодіаку\n"
        "/help - Ця довідка"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")


@bot.message_handler(commands=["signs"])
def list_signs(message):
    signs_list = "📜 *Список знаків зодіаку:*\n\n" + "\n".join(
        [f"- {sign.capitalize()}" for sign in ZODIAC_SIGNS.keys()]
    )
    bot.send_message(message.chat.id, signs_list, parse_mode="Markdown")


def get_horoscope(sign):
    try:
        response = requests.get(f"{API_URL}?sign={sign}&day=today")
        if response.status_code == 200:
            data = response.json()
            return data["data"]["horoscope_data"]
        return None
    except:
        return None


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_input = message.text.lower()

    if user_input == "/today":
        bot.send_message(
            message.chat.id, "Будь ласка, спочатку оберіть свій знак зодіаку."
        )
        return

    if user_input in ZODIAC_SIGNS:
        sign_key = ZODIAC_SIGNS[user_input]
        horoscope = get_horoscope(sign_key)

        if horoscope:
            today = datetime.now().strftime("%d.%m.%Y")
            response = (
                f"✨ *Гороскоп для {user_input.capitalize()} на {today}*\n\n"
                f"{horoscope}\n\n"
                f"Щасливого дня! 🌟"
            )
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        else:
            bot.send_message(
                message.chat.id,
                "На жаль, не вдалося отримати гороскоп. Спробуйте пізніше.",
            )
    else:
        bot.send_message(
            message.chat.id,
            "Не розпізнано знак зодіаку. Спробуйте ще раз або виберіть зі списку /signs",
        )

bot.polling(none_stop=True)
