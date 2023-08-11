import httplib2
import asyncio
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from data_base import db

CREDENTIALS_FILE = 'EXAMPLE-CREDENTIALS_FILE.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http = httpAuth)

spreadsheetId = '1aaaAAAAA-EXAMPLE-spreadsheetId'


async def update_table():
    values = [['End date of the trial period','Payment date','Name','ID', 'Server']]
    users=db.get_users()
    for u in users:
        date_of_arrival = u[2]
        date_sub = u[4]
        user_id = u[0]
        full_name = u[1]
        server = u[-1]
        values.append([date_of_arrival, date_sub, full_name, f'#ID{user_id}', server])
    results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "List1",
            "majorDimension": "ROWS",
            "values": values}
        ]
    }).execute()