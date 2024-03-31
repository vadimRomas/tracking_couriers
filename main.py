import datetime
import os
from threading import Thread
from time import sleep

import schedule
from dotenv import load_dotenv
from telebot import TeleBot, types

from couriers import Courier
from geo import get_country
from lunch_break import LunchBreak
from workday import Workday


load_dotenv()

bot = TeleBot(os.getenv('telegram_token'))


@bot.message_handler(commands=["start"])
def start(message):
    courier = Courier(message.from_user.id).get_courier_by_user_id()

    if not courier:
        msg = bot.send_message(message.chat.id, f"Привіт незнайомець🥷 Введи своє ім'я та прізвище")
        bot.register_next_step_handler(msg, process_create_courier_step)
        return

    markup = types.ReplyKeyboardMarkup()
    button_geo = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
    markup.add(button_geo)

    bot.send_message(message.chat.id, f'Привіт! {courier["name"]}', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Піти на обід🍔":
        courier = Courier(message.from_user.id).get_courier_by_user_id()
        start_time = datetime.datetime.fromtimestamp(message.date).time()
        LunchBreak().start_lunch_break(courier['name'], start_time)

        markup = types.ReplyKeyboardMarkup()
        btn_end_lunch = types.KeyboardButton('Завершити обід')
        markup.add(btn_end_lunch)

        bot.send_message(message.from_user.id, "Смачного!", reply_markup=markup)
    elif message.text == 'Завершити обід':
        courier = Courier(message.from_user.id).get_courier_by_user_id()
        end_time = datetime.datetime.fromtimestamp(message.date).time()
        LunchBreak().end_lunch_break(courier['name'], end_time)

        markup = types.ReplyKeyboardMarkup()
        btn_lunch_brake = types.KeyboardButton(text='Піти на обід🍔')
        btn_go_home = types.KeyboardButton(text='Завершити роботу', request_location=True)
        markup.add(btn_lunch_brake, btn_go_home)

        bot.send_message(message.from_user.id, 'Поїли тепер можна і попрацювати', reply_markup=markup)


def process_create_courier_step(message):
    courier_name = message.text.lower()

    create_courier = Courier(message.from_user.id, courier_name).create_courier()

    if create_courier:
        markup = types.ReplyKeyboardMarkup()
        button_geo = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
        markup.add(button_geo)

        bot.send_message(message.chat.id, f"Радий знайомству {create_courier['name'].title()}", reply_markup=markup)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        courier = Courier(message.from_user.id).get_courier_by_user_id()
        time = datetime.datetime.fromtimestamp(message.date).time()
        address = get_country(message.location.latitude, message.location.longitude)

        is_courier_work = Workday().get_row_courier_workday(courier['name'])

        if not is_courier_work:
            Workday().start_workday(courier['name'], time, address)

            markup = types.ReplyKeyboardMarkup()
            btn_lunch_brake = types.KeyboardButton(text='Піти на обід🍔')
            btn_go_home = types.KeyboardButton(text='Завершити роботу', request_location=True)
            markup.add(btn_lunch_brake, btn_go_home)

            bot.send_message(message.chat.id, address, reply_markup=markup)
            # print(message.location)
            print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
        else:
            Workday().end_workday(courier['name'], time, address, row=is_courier_work)

            markup = types.ReplyKeyboardMarkup()
            btn_start_work = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
            markup.add(btn_start_work)

            bot.send_message(message.chat.id, address, reply_markup=markup)


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def task_send_reminder():
    couriers = Courier().get_all_couriers()

    for courier in couriers:
        if courier['telegram_id'] != 'телеграм id':
            bot.send_message(courier['telegram_id'], f'Привіт {courier['name'].title()}👋 Якщо ти сьогодні працюєш, не забудь відмітитися коли прийдеш на роботу. Гарного та Продуктивного дня🤙')


if __name__ == "__main__":
    schedule.every().day.at("09:50").do(task_send_reminder)

    Thread(target=schedule_checker).start()

    bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть