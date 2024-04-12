import datetime

import pygsheets

from config import tz
from lunch_break import LunchBreak


class Workday:
    sheet_name = 'testcourier'
    client = pygsheets.authorize()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet_by_title('testWorkday')

    def __init__(self):
        self.date = datetime.datetime.now(tz).date()

    def start_workday(self, courier_name, time, location):
        self.worksheet.append_table([str(self.date), courier_name, str(time), location])

    def end_workday(self, courier_name, time, location, row):
        workday_time = self.count_workday_time(row, time)
        lunch_break_time = LunchBreak().count_lunch_break(courier_name)

        self.worksheet.update_value(f'E{row}', str(time))
        self.worksheet.update_value(f'F{row}', location)
        self.worksheet.update_value(f'G{row}', workday_time)
        self.worksheet.update_value(f'H{row}', lunch_break_time)

    def count_workday_time(self, row, time):
        all_workdays = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
        workday = all_workdays[row - 1]
        hours = int(time.hour) - int(datetime.datetime.strptime(workday[2], '%H:%M:%S').hour)
        minutes = int(time.minute) - int(datetime.datetime.strptime(workday[2], '%H:%M:%S').minute)
        seconds = int(time.second) - int(datetime.datetime.strptime(workday[2], '%H:%M:%S').second)
        return f'{hours}:{minutes}:{seconds}'

    def get_row_courier_workday(self, courier_name):
        all_couriers = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)

        for idc, courier in enumerate(all_couriers):
            if courier_name == courier[1] and str(self.date) == courier[0]:
                return idc + 1

    def get_courier_workday(self, courier_name):
        all_workdays = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)

        for workday in all_workdays:
            if courier_name == workday[1] and str(self.date) == workday[0]:
                return workday

        return []

    def get_couriers_workday(self):
        all_workdays = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)

        return [workday for workday in all_workdays if str(self.date) == workday[0]]
