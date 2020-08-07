import httplib2
import os

from apiclient import discovery
from google.oauth2 import service_account

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('bHi/8szU2mkZAaIMLGDKqTE8CnG4TjilHVVJsqDse2XD39ZUGdxiHRedvOGSC5Q7zJfFYZoOAIoMxeKAR5mQqbz0DomlYKjU7gMEK/zQ0QJFFVJLpDhwB8DRrJ8SAoqK+sEAMuD2PL0h0wdsZxncRwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2ee6a86bd730b810a7d614777f07cecb')


scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
secret_file = os.path.join(os.getcwd(),'client_secret.json')

credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
service = discovery.build('sheets','v4',credentials=credentials)


SPREADSHEET_ID = '1a7Rz4BUy6krsQzbj82NS1Z9hFDlkQZLfXi-0ZVMrRXA'
RANGE_NAME = 'A1:B2'


values = [
        ['aaa','gitkraken works'],
        ['a2','b2'],
        ]

 data = {
    'values' : values
    }

service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, body=data, range=RANGE_NAME, valueInputOption='USER_ENTERED').execute()




#def db_call():
    #return test_output


@app.route("/")
def home():
    return 'home OK'

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
        
    input_text = event.message.text
    if (eval(input_text)>0) and (eval(input_text)<=100):
        output_text= input_text
    elif  input_text =="0":
        output_text = "早安"
   # elif input_text == "111":
       # output_text = db_call()
    else:
        output_text="我是可愛的貓咪"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(str(output_text)))





if __name__ == "__main__":
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        secret_file = os.path.join(os.getcwd(),'client_secret.json')

        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets','v4',credentials=credentials)

        spreadsheet_id = '1a7Rz4BUy6krsQzbj82NS1Z9hFDlkQZLfXi-0ZVMrRXA'
        range_name = 'A1:B2'

        values = [
            ['omcoolg','this works'],
            ['a2','b2'],
            ]

        data = {
            'values' : values
            }

        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, body=data, range=range_name, valueInputOption='USER_ENTERED').execute()



    except OSError as e:
        print(e)

        app.run()
    
