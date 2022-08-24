import requests
from telebot import TeleBot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from configs import TOKEN
import sqlite3

bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'about', 'help', "view_history"])
def command_handler(message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    commands(message)

    if message.text == "/start":
        chat_id = message.chat.id
        user_msg = bot.send_message(chat_id, f"Hello {full_name}! This is a weather bot☁️🙂🌡️",
                                    reply_markup=weather_data())
        bot.register_next_step_handler(user_msg, enter_city_name)

    elif message.text == "/about":
        bot.send_message(chat_id, "You can be aware of everyday weather of every country and city in this bot!\n")
    elif message.text == "/help":
        bot.send_message(chat_id, "You can ask for help by this command https://t.me/User65031", )
    elif message.text == "/view_history":
        viewHistory(message)


def enter_city_name(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Enter the city name 🌆🏙️")
    bot.register_next_step_handler(msg, show_user)


def enter_again(message):
    text = message.text
    if text == "Yes":
        enter_city_name(message)
    else:
        commands(message)


def show_user(message):
    chat_id = message.chat.id
    text = message.text
    full_name = message.from_user.full_name

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=7a29ec7fe1ccf3e341f6f55de1e74ae3'
    response = requests.get(url.format(text)).json()

    if response['cod'] == 200:
        city_name = response['name']
        description = response['weather'][0]['description']
        weather = response['main']['temp']
        wind_speed = response['wind']['speed']
        bot.send_message(chat_id,
                         f"City Name - {city_name}\nStatus - {description}\nWind - {wind_speed} km/h\nTemperature - {weather} °C")
        msg = bot.send_message(chat_id, "Do you want to enter again ? Yes/No", reply_markup=user_answer())
        bot.register_next_step_handler(msg, enter_again)

        conn = sqlite3.connect("weather.db")
        cur = conn.cursor()

        cur.execute("INSERT INTO history(telegram_id, fullname, city_name, status, wind, temperature)VALUES("
                    "?,?,?,?,?,?)", (chat_id, full_name, city_name, description, wind_speed, weather))
        conn.commit()
        conn.close()

    else:
        bot.send_message(chat_id, "Invalid City")
        enter_city_name(message)


def viewHistory(message):
    chat_id = message.chat.id
    conn = sqlite3.connect("weather.db")
    cur = conn.cursor()

    cur.execute("SELECT telegram_id, fullname, city_name, status, wind, temperature FROM history WHERE telegram_id = ?",
                (chat_id,))
    msg = bot.send_message(chat_id, "Your history activity⬇️", reply_markup=back())
    for item in cur:
        bot.send_message(chat_id,
                         f"Telegram ID = {item[0]}\n"
                         f"Fullname = {item[1]}\n"
                         f"City Name = {item[2]}\n"
                         f"Status = {item[3]}\n"
                         f"Wind Speed = {item[4]}\n"
                         f"Temperature = {item[5]}", )
    bot.register_next_step_handler(msg, back_function)
    conn.close()


def weather_data():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton(text="Weather")
    markup.add(btn)
    return markup


answers = ['Yes', "No"]


def user_answer():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    for ans in answers:
        btn = KeyboardButton(text=ans)
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def back():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton(text="🔙 back")
    markup.add(btn)
    return markup


def back_function(message):
    text = message.text
    if text == "🔙 back":
        commands(message)


def commands(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "/start\n"
                              "/about\n"
                              "/help\n"
                              "/view_history")


bot.polling(none_stop=True)
