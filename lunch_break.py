import datetime

from config import tz, spreadsheet_id
from google_connect import get_service_sacc, create_worksheet


class LunchBreak:

    def __init__(self):
        self.date = datetime.datetime.now(tz).date()

        self.worksheet_name = f'testlunchBreak{str(self.date.month)}'
        try:
            self.lunch_brake = get_service_sacc().spreadsheets().values().batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=["A1:D999", self.worksheet_name]).execute()['valueRanges'][1]['values']
        except:
            create_worksheet(self.worksheet_name)
            body = {
                'values': [
                    ["Дата", "Імя курєра", "Початок перерви", "Кінець перерви"]
                ]
            }
            get_service_sacc().spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{self.worksheet_name}!A1",
                valueInputOption="RAW",
                body=body).execute()

            self.lunch_brake = get_service_sacc().spreadsheets().values().batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=["A1:D999", self.worksheet_name]).execute()['valueRanges'][1]['values']

    def start_lunch_break(self, courier_name, start_time):
        body = {
            'values': [
                [str(self.date), courier_name, str(start_time)]
            ]
        }

        get_service_sacc().spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{self.worksheet_name}!A{len(self.lunch_brake)+1}",
            valueInputOption="RAW",
            body=body).execute()

    def end_lunch_break(self, courier_name, end_time):
        row = self.get_row_courier_lunch_break(courier_name, self.date)

        if row:
            body = {
                'values': [
                    [str(end_time)],
                ]
            }

            get_service_sacc().spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{self.worksheet_name}!D{row}",
                valueInputOption="RAW",
                body=body).execute()

    def count_lunch_break(self, courier_name):
        list_lunch_time = [[lunch_brake[2], lunch_brake[3]] for lunch_brake in self.lunch_brake if courier_name == lunch_brake[1] and str(self.date) == lunch_brake[0]]
        result = datetime.datetime(2020,8, 29)

        for lunch_time in list_lunch_time:
            start_lunch = lunch_time[0].split(':')
            end_lunch = lunch_time[1].split(':')

            result += (datetime.datetime(2020, 8, 29, int(end_lunch[0]), int(end_lunch[1]), int(end_lunch[2])) -
                       datetime.datetime(2020, 8, 29, int(start_lunch[0]), int(start_lunch[1]), int(start_lunch[2])))

        return f'{result.hour}:{result.minute}:{result.second}'

    def get_row_courier_lunch_break(self, courier_name, date):
        for idl, lunch_brake in enumerate(self.lunch_brake):
            if courier_name == lunch_brake[1] and str(date) == lunch_brake[0] and len(lunch_brake) == 3:
                return idl + 1

    def is_courier_finished_lunch(self, courier_name, date, time):
        for lunch_brake in self.lunch_brake:
            if courier_name == lunch_brake[1] and str(date) == lunch_brake[0] and len(lunch_brake) == 3 and str(time) == lunch_brake[2]:
                return True

        return False
