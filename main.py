import datetime
from threading import Thread
from time import sleep

import schedule
from telebot import TeleBot, types, apihelper

from config import telegram_token, tz, proxy_url
from couriers import Courier
from geo import get_country
from lunch_break import LunchBreak
from workday import Workday


bot = TeleBot(telegram_token)


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

        start_time = datetime.datetime.now(tz).time().replace(microsecond=0)
        LunchBreak().start_lunch_break(courier['name'], start_time)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_end_lunch = types.KeyboardButton('Завершити обід')
        markup.add(btn_end_lunch)
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


def task_send_reminder_start():
    couriers = Courier().get_all_couriers()

    for courier in couriers:
        if courier['telegram_id'] != 'телеграм id':
            try:
                bot.send_message(courier['telegram_id'], f'Привіт {courier["name"].title()}👋 Якщо ти сьогодні працюєш, не забудь відмітитися коли прийдеш на роботу. Гарного та Продуктивного дня🤙')
            except Exception as e:
                print(courier)
                print(e)


def task_filling_blanks():
    all_workdays = Workday().worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
    all_lunch_brake = LunchBreak().worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
    name_couriers = []

    for lunch_brake in all_lunch_brake:
        if len(lunch_brake) == 3:
            LunchBreak().end_lunch_break(lunch_brake[1], '23:50:00')

    for idw, workday in enumerate(all_workdays):
        if len(workday) == 4:
            Workday().end_workday(workday[1], datetime.datetime.now().time().replace(microsecond=0), 'Відсутнє', idw + 1)
            if workday[1] not in name_couriers:
                name_couriers.append(workday[1])

    for name_courier in name_couriers:
        courier = Courier(name=name_courier).get_courier()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_start_work = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
        markup.add(btn_start_work)

        bot.send_message(courier['telegram_id'],
                         f'Оце ти попав! Схоже що ти не натиснув кнопку завершити роботу. Більше так не роби.',
                         reply_markup=markup)


if __name__ == "__main__":
    apihelper.proxy = {'http': proxy_url}

    schedule.every().day.at("09:50", "Europe/Kyiv").do(task_send_reminder_start)
    schedule.every().day.at("23:50", "Europe/Kyiv").do(task_filling_blanks)

    Thread(target=schedule_checker).start()

    bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть