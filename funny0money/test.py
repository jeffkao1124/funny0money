import httplib2
import os

from apiclient import discovery
from google.oauth2 import service_account

if __name__ == "__main__":
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        secret_file = os.path.join(os.getcwd(),'client_secret.json')

        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets','v4',credentials=credentials)

        spreadsheet_id = '1a7Rz4BUy6krsQzbj82NS1Z9hFDlkQZLfXi-0ZVMrRXA'
        range_name = 'A1:B2'

        values = [
            ['this its test text','this works'],
            ['a2','b2'],
            ]

        data = {
            'values' : values
            }

        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, body=data, range=range_name, valueInputOption='USER_ENTERED').execute()



    except OSError as e:
        print(e)
