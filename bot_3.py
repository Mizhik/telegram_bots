import telebot
import requests
import re

TOKEN = "7787503861:AAFUh4ob-A-_Ys_67xcOPySeGcCub3VsxV8"
API_KEY = "2bf5650f913d63f7b35ad78e"
BASE_URL = "https://open.er-api.com/v6/latest/"

bot = telebot.TeleBot(TOKEN)

CURRENCIES = {
    "USD": "Долар США",
    "EUR": "Євро",
    "UAH": "Гривня",
    "GBP": "Фунт стерлінгів",
    "JPY": "Єна",
    "CAD": "Канадський долар",
    "PLN": "Злотий",
}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    help_text = (
        "💱 *Бот для конвертації валют*\n\n"
        "Напишіть у форматі:\n"
        "`<сума> <валюта1> в <валюта2>`\n\n"
        "*Приклад:*\n"
        "`100 USD в UAH`\n\n"
        "Доступні валюти:\n"
    )

    currencies_list = "\n".join(
        [f"- {code}: {name}" for code, name in CURRENCIES.items()]
    )

    bot.send_message(
        message.chat.id, help_text + currencies_list, parse_mode="Markdown"
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    send_welcome(message)  


def get_exchange_rates(base_currency):
    try:
        response = requests.get(f"{BASE_URL}{base_currency}?apikey={API_KEY}")
        data = response.json()
        if data["result"] == "success":
            return data["rates"]
        return None
    except:
        return None


def convert_currency(amount, from_currency, to_currency):
    rates = get_exchange_rates(from_currency)
    if not rates:
        return None

    if to_currency not in rates:
        return None

    converted_amount = float(amount) * rates[to_currency]
    return round(converted_amount, 2)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        match = re.match(
            r"(\d+\.?\d*)\s+([A-Za-z]{3})\s+(в|to)\s+([A-Za-z]{3})",
            message.text,
            re.IGNORECASE,
        )
        if not match:
            bot.reply_to(
                message,
                "Невірний формат. Спробуйте:\n`100 USD в EUR`",
                parse_mode="Markdown",
            )
            return

        amount, from_curr, _, to_curr = match.groups()
        from_curr = from_curr.upper()
        to_curr = to_curr.upper()

        if from_curr not in CURRENCIES or to_curr not in CURRENCIES:
            unsupported = []
            if from_curr not in CURRENCIES:
                unsupported.append(from_curr)
            if to_curr not in CURRENCIES:
                unsupported.append(to_curr)
            bot.reply_to(message, f"Валюта не підтримується: {', '.join(unsupported)}")
            return

        result = convert_currency(amount, from_curr, to_curr)
        if result is None:
            bot.reply_to(message, "Не вдалося отримати курси валют. Спробуйте пізніше.")
            return

        response = (
            f"💱 *Результат конвертації:*\n\n"
            f"{amount} {from_curr} = *{result} {to_curr}*\n\n"
            f"1 {from_curr} = {round(result/float(amount), 4)} {to_curr}\n"
            f"1 {to_curr} = {round(float(amount)/result, 4)} {from_curr}"
        )

        bot.reply_to(message, response, parse_mode="Markdown")

    except ValueError:
        bot.reply_to(message, "Будь ласка, введіть коректну суму для конвертації.")
    except Exception as e:
        bot.reply_to(message, "Сталася помилка. Спробуйте ще раз.")


bot.polling(none_stop=True)
