import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import apiclient

import os

from config import google_json, spreadsheet_id


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + f"/{google_json}"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return apiclient.discovery.build('sheets', 'v4', http=creds_service)


def create_worksheet(title: str):
    body = {
        "requests": {
            "addSheet": {
                "properties": {
                    "title": title
                }
            }
        }
    }

    get_service_sacc().spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body=body).execute()
