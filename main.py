import datetime
from threading import Thread
from time import sleep

import schedule
from telebot import types, apihelper
from telebot.apihelper import ApiTelegramException

from config import tz, proxy_url, bot
from couriers import Courier
from geo import get_country
from lunch_break import LunchBreak
from tasks import task_send_reminder_start, task_send_reminder_end_lunch, task_filling_blanks
from workday import Workday


@bot.message_handler(commands=["start"])
def start(message):
    courier = Courier(message.from_user.id).get_courier()

    if not courier:
        msg = bot.send_message(message.chat.id, f"Привіт незнайомець🥷 Введи своє ім'я та прізвище")
        bot.register_next_step_handler(msg, process_create_courier_step)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_geo = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
    markup.add(button_geo)

    try:
        bot.send_message(message.chat.id, f'Привіт! {courier["name"]}', reply_markup=markup)
    except Exception as e:
        print('message.chat.id: ', message.chat.id)
        print(e)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Піти на обід🍔":
        courier = Courier(message.from_user.id).get_courier()
        start_datetime = datetime.datetime.now(tz)
        row_lunch_brake = LunchBreak().get_row_courier_lunch_break(courier['name'], start_datetime.date())

        if row_lunch_brake:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_end_lunch = types.KeyboardButton('Завершити обід')
            markup.add(btn_end_lunch)

            bot.send_message(message.from_user.id, "Ти вже на обіді.", reply_markup=markup)
            return

        LunchBreak().start_lunch_break(courier['name'], start_datetime.time().replace(microsecond=0))

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_end_lunch = types.KeyboardButton('Завершити обід')
        markup.add(btn_end_lunch)

        schedule.every(1).hour.do(task_send_reminder_end_lunch, message.from_user.id)

        try:
            bot.send_message(message.from_user.id, "Смачного!", reply_markup=markup)
        except Exception as e:
            print('message.chat.id: ', message.chat.id)
            print(e)
    elif message.text == 'Завершити обід':
        courier = Courier(message.from_user.id).get_courier()
        end_time = datetime.datetime.now(tz).time().replace(microsecond=0)
        LunchBreak().end_lunch_break(courier['name'], end_time)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_lunch_brake = types.KeyboardButton(text='Піти на обід🍔')
        btn_go_home = types.KeyboardButton(text='Завершити роботу', request_location=True)
        markup.add(btn_lunch_brake, btn_go_home)

        try:
            bot.send_message(message.from_user.id, 'Поїли тепер можна і попрацювати', reply_markup=markup)
        except Exception as e:
            print('message.chat.id: ', message.chat.id)
            print(e)


def process_create_courier_step(message):
    courier_name = message.text.lower()

    create_courier = Courier(message.from_user.id, courier_name).create_courier()

    if create_courier:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_geo = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
        markup.add(button_geo)

        try:
            bot.send_message(message.chat.id, f"Радий знайомству {create_courier['name'].title()}", reply_markup=markup)
        except Exception as e:
            print('message.chat.id: ', message.chat.id)
            print(e)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        courier = Courier(message.from_user.id).get_courier()
        message_time = datetime.datetime.now(tz).time().replace(microsecond=0)
        address = get_country(message.location.latitude, message.location.longitude)

        row_courier_work = Workday().get_row_courier_workday(courier['name'])
        courier_work = Workday().get_courier_workday(courier['name'])

        if len(courier_work) == 8:
            try:
                bot.send_message(message.chat.id, "Ви вже завершили сьогодні працювати! Якщо ви випадково завершили роботу, будь ласка, повідомте вашого керівника")
            except Exception as e:
                print('message.chat.id: ', message.chat.id)
                print(e)
            return

        if not row_courier_work:
            Workday().start_workday(courier['name'], message_time, address)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_lunch_brake = types.KeyboardButton(text='Піти на обід🍔')
            btn_go_home = types.KeyboardButton(text='Завершити роботу', request_location=True)
            markup.add(btn_lunch_brake, btn_go_home)

            try:
                bot.send_message(message.chat.id, address, reply_markup=markup)
            except Exception as e:
                print('message.chat.id: ', message.chat.id)
                print(courier)
                print(e)
        else:
            Workday().end_workday(courier['name'], message_time, address, row=row_courier_work)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_start_work = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
            markup.add(btn_start_work)

            try:
                bot.send_message(message.chat.id, address, reply_markup=markup)
            except Exception as e:
                print('message.chat.id: ', message.chat.id)
                print(courier)
                print(e)


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def start_bot():
    try:
        bot.infinity_polling(none_stop=True, interval=0)  # обязательная для работы бота часть
    except ApiTelegramException as e:
        print(dir(e))
        print(e)
        sleep(10)
        start_bot()


if __name__ == "__main__":
    apihelper.proxy = {'http': proxy_url}

    schedule.every().day.at("09:50", "Europe/Kyiv").do(task_send_reminder_start)
    schedule.every().day.at("23:50", "Europe/Kyiv").do(task_filling_blanks)

    Thread(target=schedule_checker).start()

    start_bot()
