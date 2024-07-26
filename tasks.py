import datetime

import schedule
from telebot import types

from config import tz, bot
from couriers import Courier
from lunch_break import LunchBreak
from workday import Workday


def task_send_reminder_start():
    couriers = Courier().get_all_couriers()

    for courier in couriers:
        row_workday = Workday().get_row_courier_workday(courier["name"])

        if not row_workday:
            try:
                bot.send_message(courier['telegram_id'], f'Привіт {courier["name"].title()}👋 Якщо ти сьогодні працюєш, не забудь відмітитися коли прийдеш на роботу. Гарного та Продуктивного дня🤙')
            except Exception as e:
                print(courier)
                print(e)


def task_send_reminder_end_lunch(telegram_id, time):
    courier = Courier(user_id=telegram_id).get_courier()
    date = datetime.datetime.now(tz).date()
    is_lunch_brake = LunchBreak().is_courier_finished_lunch(courier['name'], date, time)

    if is_lunch_brake:
        try:
            bot.send_message(telegram_id, 'Ти вже годину на обіді. Не забудь натиснути кнопку "Завершити обід"')  #  f'Лягай спати, відпочивай! Я знаю ти втомлюєшся капец.Так що лягай спати це я тобі сказав Полтавський палій! Ти зрозумів мене Дракон?'
        except Exception as e:
            print(telegram_id)
            print(e)

    return schedule.CancelJob


def task_filling_blanks():
    all_workdays = Workday().workdays
    all_lunch_brake = LunchBreak().lunch_brake
    name_couriers = []

    for lunch_brake in all_lunch_brake:
        if len(lunch_brake) == 3:
            LunchBreak().end_lunch_break(lunch_brake[1], '23:50:00')

    for idw, workday in enumerate(all_workdays):
        if len(workday) == 4:
            Workday().end_workday(workday[1], datetime.datetime.now(tz), 'Відсутнє', idw + 1)
            if workday[1] not in name_couriers:
                name_couriers.append(workday[1])

    for name_courier in name_couriers:
        courier = Courier(name=name_courier).get_courier()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_start_work = types.KeyboardButton(text='Я вже нa poботі💼', request_location=True)
        markup.add(btn_start_work)
        try:
            bot.send_message(courier['telegram_id'],
                             f'Оце ти попав! Схоже що ти не натиснув кнопку завершити роботу. Більше так не роби.',
                             reply_markup=markup)
        except Exception as e:
            print(courier)
            print(e)


