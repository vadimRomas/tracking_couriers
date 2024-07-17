import datetime

from config import tz
from lunch_break import LunchBreak
from google_connect import get_service_sacc, create_worksheet


class Workday:

    def __init__(self):
        self.date = datetime.datetime.now(tz).date()
        self.worksheet_name = f'testWorkday{str(self.date.month)}'
        try:
            self.workdays = get_service_sacc().spreadsheets().values().batchGet(
                spreadsheetId='1yiHgHortpplm1kD6yIkyCh1-bt1iwsOg_qMqGBc4rGA', ranges=["A1:H999", self.worksheet_name]).execute()['valueRanges'][1]['values']
        except:
            create_worksheet(self.worksheet_name)
            body = {
                'values': [
                    ["Дата", "Ім'я курєра", "Початок робочого дня", "Початкова адреса", "Кінець робочого дня", "Кінцева адреса", "Робочий час", "Перерва"]
                ]
            }

            get_service_sacc().spreadsheets().values().append(
                spreadsheetId='1yiHgHortpplm1kD6yIkyCh1-bt1iwsOg_qMqGBc4rGA',
                range=f"{self.worksheet_name}!A1",
                valueInputOption="RAW",
                body=body).execute()

            self.workdays = get_service_sacc().spreadsheets().values().batchGet(
                spreadsheetId='1yiHgHortpplm1kD6yIkyCh1-bt1iwsOg_qMqGBc4rGA',
                ranges=["A1:H999", self.worksheet_name]).execute()['valueRanges'][1]['values']

    def start_workday(self, courier_name, time, location):
        body = {
            'values': [
                [str(self.date), courier_name, str(time.time().replace(microsecond=0)), location],
            ]
        }

        get_service_sacc().spreadsheets().values().append(
            spreadsheetId='1yiHgHortpplm1kD6yIkyCh1-bt1iwsOg_qMqGBc4rGA',
            range=f"{self.worksheet_name}!A{len(self.workdays)+1}",
            valueInputOption="RAW",
            body=body).execute()

    def end_workday(self, courier_name, time, location, row):
        workday_time = self.count_workday_time(row, time)
        lunch_break_time = LunchBreak().count_lunch_break(courier_name)

        body = {
            'values': [
                [str(time.time().replace(microsecond=0)), location, workday_time, lunch_break_time],
            ]
        }

        get_service_sacc().spreadsheets().values().update(
            spreadsheetId='1yiHgHortpplm1kD6yIkyCh1-bt1iwsOg_qMqGBc4rGA',
            range=f"{self.worksheet_name}!E{row}",
            valueInputOption="RAW",
            body=body).execute()

    def count_workday_time(self, row, time):
        workday = self.workdays[row - 1]

        hour = datetime.datetime.strptime(workday[2], '%H:%M:%S').hour
        minute = datetime.datetime.strptime(workday[2], '%H:%M:%S').minute
        second = datetime.datetime.strptime(workday[2], '%H:%M:%S').second

        result = time - datetime.timedelta(hours=hour, minutes=minute, seconds=second)
        return f'{result.hour}:{result.minute}:{result.second}'

    def get_row_courier_workday(self, courier_name):
        for idc, courier in enumerate(self.workdays):
            if courier_name == courier[1] and str(self.date) == courier[0]:
                return idc + 1

    def get_courier_workday(self, courier_name):
        for workday in self.workdays:
            if courier_name == workday[1] and str(self.date) == workday[0]:
                return workday

        return []

    def get_couriers_workday(self):
        return [workday for workday in self.workdays if str(self.date) == workday[0]]
