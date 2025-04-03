import telebot
import requests

bot = telebot.TeleBot("7689377518:AAGrQChz9oUsA1DDrYNcnYNRaC8fhndgfjI")
WEATHER_API_KEY = "aab1fb0cd6f961b2d87c23ae2c01ab64"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привіт! Я бот погоди. ✨\n"
        "Напиши назву міста (наприклад, 'Київ' або 'Львів'), "
        "і я надішлю поточний прогноз погоди.\n\n"
        "Також можна використати /help для довідки.",
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(
        message,
        "Доступні команди:\n"
        "/start - Почати роботу з ботом\n"
        "/help - Отримати довідку\n\n"
        "Просто напиши назву міста, щоб дізнатися погоду!",
    )


def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    response = requests.get(url)
    data = response.json()
    return data


def format_weather(data):
    if data["cod"] != 200:
        return "Не вдалося знайти погоду для цього міста. Спробуйте ще раз!"

    city = data["name"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    return (
        f"Погода в {city}:\n\n"
        f"🌡 Температура: {temp}°C (відчувається як {feels_like}°C)\n"
        f"☁️ Стан: {description.capitalize()}\n"
        f"💧 Вологість: {humidity}%\n"
        f"🌬 Вітер: {wind} м/с"
    )


@bot.message_handler(content_types=["text"])
def send_weather(message):
    try:
        city = message.text
        weather_data = get_weather(city)
        reply = format_weather(weather_data)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Вибачте, сталася помилка. Спробуйте пізніше.")


bot.polling(none_stop=True)
