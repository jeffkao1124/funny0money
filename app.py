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
    MessageEvent, TextMessage, TextSendMessage ,FollowEvent, UnfollowEvent
)
import requests
from bs4 import BeautifulSoup
from dbModel import *
from datetime import datetime
import json
from sqlalchemy import desc


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

    if bodyjson['events'][0]['source']['type'] == 'group':
        receivedmsg = bodyjson['events'][0]['message']['text']
        if '分帳設定' in receivedmsg:
            userName=receivedmsg.split(' ')[1]
            add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num = '0',
                    nickname = userName,
                    group_id = bodyjson['events'][0]['source']['groupId'],
                    type = bodyjson['events'][0]['source']['type'],
                    status = 'None',
                    account = '0',
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = bodyjson['events'][0]['message']['text'],
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
        elif '分帳' in receivedmsg:
            chargeName=receivedmsg.split(' ')[1]
            chargeNumber=receivedmsg.split(' ')[2]
            add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num = '0',
                    nickname = 'None',
                    group_id = bodyjson['events'][0]['source']['groupId'],
                    type = bodyjson['events'][0]['source']['type'],
                    status = 'None',
                    account = chargeNumber,
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = chargeName,
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
        else:
            add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num = '0',
                    nickname = 'None',
                    group_id = bodyjson['events'][0]['source']['groupId'],
                    type = bodyjson['events'][0]['source']['type'],
                    status = 'None',
                    account = '0',
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = bodyjson['events'][0]['message']['text'],
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
            
    else:
        receivedmsg = bodyjson['events'][0]['message']['text']
        if '記帳' in receivedmsg:
            chargeName=receivedmsg.split(' ')[1]
            chargeNumber=receivedmsg.split(' ')[2]
            add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num = '0',
                    nickname = 'None',
                    group_id = 'None',
                    type = 'user',
                    status = 'save',
                    account = chargeNumber,
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = chargeName ,
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
        else:
            add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num = '0',
                    nickname = 'None',
                    group_id = 'None',
                    account = '0',
                    type = 'user',
                    status = 'None',
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = bodyjson['events'][0]['message']['text'],
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
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
    #line_bot_api.push_message(
   #             event.reply_token,
    #            TextSendMessage(text= str(perfect_list)))
    input_text = event.message.text.lower()
    data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).limit(1).all()
    history_dic = {}
    history_list = []    
    for _data in data_UserData:
        history_dic['Status'] = _data.status
        history_dic['type'] = _data.type
        history_dic['user_id'] = _data.user_id
        history_list.append(history_dic)
        history_dic = {}
    if history_list[0]['type'] == 'user':   
        if (history_list[0]['Status'] == 'save') and ('記帳' in input_text):

            output_text='記帳成功'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        elif input_text =='查帳':
            selfId = history_list[0]['user_id']
            data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='save')
            history_dic = {}
            history_list = []
            count=0
            for _data in data_UserData:
                count+=1
                history_dic['Mesaage'] = _data.message
                history_dic['Account'] = _data.account
                history_list.append(history_dic)
                history_dic = {}
            final_list =[]
            #add=0
            for i in range(count):
                final_list.append(str(history_list[i]['Mesaage'])+' '+str(history_list[i]['Account']))
                #add += eval(history_list[i]['Account'])

            perfect_list=''
            for j in range(count):
                perfect_list=perfect_list+str(j+1)+'.'+str(final_list[j])+'\n'
            #perfect_list = perfect_list+'累計花費:'+str(add)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(perfect_list)))
        elif input_text =='刪除':
            selfId = history_list[0]['user_id']
            data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='save').delete()
            output_text='刪除成功'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))

        #elif '更改' in input_text':
            
        #    changeNumber=input_text.split(' ')[1]
        #    changeMessage=input_text.split(' ')[2]
        #    changeAccount=input_text.split(' ')[3]
        #    selfId = history_list[0]['user_id']
        #    data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='save').first().update({'message':str(changeMessage),'account':str(changeAccount)})
        #    output_text='更改成功'
        #    line_bot_api.reply_message(
        #        event.reply_token,
        #        TextSendMessage(text= str(output_text)))
            
        else:
            output_text='記帳失敗'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        

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
    elif ('笨' in input_text):
        output_text='你才笨!'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= str(output_text)))            
    elif ('擊敗' in input_text):
        output_text='他真的很擊敗'
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
