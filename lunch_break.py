import datetime

import pygsheets

from config import tz


class LunchBreak:
    sheet_name = 'CouriersTracking'
    client = pygsheets.authorize()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet_by_title('lunchBreak')

    def __init__(self):
        self.date = datetime.datetime.now(tz).date()

    def start_lunch_break(self, courier_name, start_time):
        self.worksheet.append_table([str(self.date), courier_name, str(start_time)])

    def end_lunch_break(self, courier_name, end_time):
        row = self.get_row_courier_lunch_break(courier_name, self.date)

        if row:
            self.worksheet.update_value(f'D{row}', str(end_time))

    def count_lunch_break(self, courier_name):
        all_lunch_brake = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
        list_lunch_time = [[lunch_brake[2], lunch_brake[3]] for lunch_brake in all_lunch_brake if courier_name == lunch_brake[1] and str(self.date) == lunch_brake[0]]

        hours_lunch_time = 0
        minutes_lunch_time = 0
        seconds_lunch_time = 0

        for lunch_time in list_lunch_time:
            start_lunch = lunch_time[0].split(':')
            end_lunch = lunch_time[1].split(':')

            hours_lunch_time += int(end_lunch[0]) - int(start_lunch[0])
            minutes_lunch_time += int(end_lunch[1]) - int(start_lunch[1])
            seconds_lunch_time += int(end_lunch[2]) - int(start_lunch[2])

        return f'{hours_lunch_time}:{minutes_lunch_time}:{seconds_lunch_time}'

    def get_row_courier_lunch_break(self, courier_name, date):
        all_lunch_brake = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)

        for idl, lunch_brake in enumerate(all_lunch_brake):
            if courier_name == lunch_brake[1] and str(date) == lunch_brake[0] and len(lunch_brake) == 3:
                return idl + 1

    def is_courier_finished_lunch(self, courier_name, date, time):
        all_lunch_brake = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)

        for lunch_brake in all_lunch_brake:
            print(str(time), lunch_brake[2])
            if courier_name == lunch_brake[1] and str(date) == lunch_brake[0] and len(lunch_brake) == 3 and str(time) == lunch_brake[2]:
                return True

        return False
