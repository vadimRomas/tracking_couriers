from config import spreadsheet_id
from google_connect import get_service_sacc


class Courier:

    def __init__(self, user_id=None, name=None):
        self.user_id = user_id
        self.name = name
        self.worksheet_name = 'Couriers'
        self.couriers = get_service_sacc().spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id, ranges=["A1:B999", self.worksheet_name]).execute()[
            'valueRanges'][0]['values']

    def get_courier(self):

        if self.user_id:
            courier_name = {"name": courier[0] for courier in self.couriers if courier[1] == str(self.user_id)}
            return courier_name if courier_name is not None else None
        elif self.name:
            telegram_id = {"telegram_id": courier[1] for courier in self.couriers if courier[0] == str(self.name)}
            return telegram_id if telegram_id else None

    def create_courier(self):
        body = {
            'values': [
                [self.name, self.user_id],
            ]
        }

        get_service_sacc().spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{self.worksheet_name}!A{len(self.couriers)+1}",
            valueInputOption="RAW",
            body=body).execute()
        return {"name": self.name, "user_id": self.user_id}

    def get_all_couriers(self):
        return [{"name": courier[0], "telegram_id": courier[1]} for courier in self.couriers]
