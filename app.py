from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    SourceUser,SourceGroup,SourceRoom,LeaveEvent,JoinEvent,
    TemplateSendMessage,PostbackEvent,AudioMessage,LocationMessage,
    MessageEvent, TextMessage, TextSendMessage
)
import requests
from bs4 import BeautifulSoup
from dbModel import *
from datetime import datetime
import json


app = Flask(__name__)

line_bot_api = LineBotApi('bHi/8szU2mkZAaIMLGDKqTE8CnG4TjilHVVJsqDse2XD39ZUGdxiHRedvOGSC5Q7zJfFYZoOAIoMxeKAR5mQqbz0DomlYKjU7gMEK/zQ0QJFFVJLpDhwB8DRrJ8SAoqK+sEAMuD2PL0h0wdsZxncRwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2ee6a86bd730b810a7d614777f07cecb')


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
    bodyjson=json.loads(body)
    app.logger.error("Request body: " + body)
    
    #insertdata
    #print('-----in----------')
    add_data = usermessage(
            id = bodyjson['events'][0]['message']['id'],
            user_id = bodyjson['events'][0]['source']['userId'],
            message = bodyjson['events'][0]['message']['text'],
            birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
            #CreateDate = datetime.now.strftime(int(bodyjson['events'][0]['%Y/%m/%d %H:%M:%S']['CreateDate']))
        )
    db.session.add(add_data)
    db.session.commit()

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


def get_movie():
    movies = []
    url_1= "https://movies.yahoo.com.tw/chart.html"
    resp_1 = requests.get(url_1)
    ms = BeautifulSoup(resp_1.text,"html.parser")

    ms.find_all("div","rank_txt")
    movies.append(ms.find('h2').text)

    for rank_txt in ms.find_all("div","rank_txt"):
        movies.append(rank_txt.text.strip())

    return movies

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text.lower()

    if input_text == '-1':
        print('-----------in')
        data_UserData = usermessage.query.all()
        history_dic = {}
        history_list = []
        for _data in data_UserData:
            history_dic['id'] = _data.id
            history_dic['User_Id'] = _data.user_id
            history_dic['Mesaage'] = _data.message
            history_dic['Date'] = _data.birth_date
            #history_dic['CreateDate'] = _data.CreateDate
            history_list.append(history_dic)
            history_dic = {}
        print(history_list)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= str(history_list))) 
        

    elif (eval(input_text)>0) and (eval(input_text)<=100000):
        output_text= input_text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= str(output_text))) 
    elif input_text =="0":
        hot_movie=get_movie()
        output_text=hot_movie
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= str(output_text))) 
    else:
        output_text="我是可愛的柴柴"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= str(output_text))) 


if __name__ == "__main__":
    app.run()
