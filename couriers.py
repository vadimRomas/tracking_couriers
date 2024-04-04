import pygsheets


class Courier:
    sheet_name = 'CouriersTracking'
    client = pygsheets.authorize()
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet_by_title('Couriers')

    def __init__(self, user_id=None, name=None):
        self.user_id = user_id
        self.name = name

    def get_courier(self):
        all_couriers = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)

        if self.user_id:
            courier_name = {"name": courier[0] for courier in all_couriers if courier[1] == str(self.user_id)}
            return courier_name if courier_name is not None else None
        elif self.name:
            telegram_id = {"telegram_id": courier[1] for courier in all_couriers if courier[0] == str(self.name)}
            return telegram_id if telegram_id else None

    def create_courier(self):
        self.worksheet.append_table([self.name, self.user_id])
        return {"name": self.name, "user_id": self.user_id}

    def get_all_couriers(self):
        all_couriers = self.worksheet.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False)
        return [{"name": courier[0], "telegram_id": courier[1]} for courier in all_couriers]
