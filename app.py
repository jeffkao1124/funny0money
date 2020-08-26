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
import numpy as np
import sys

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
                    status = 'set',
                    account = '0',
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = bodyjson['events'][0]['message']['text'],
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
        elif '分帳' in receivedmsg:
            chargeName=receivedmsg.split(' ',3)[1]
            chargeNumber=receivedmsg.split(' ',3)[2]
            chargePeople=receivedmsg.split(' ',3)[3]
            add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num =chargePeople ,
                    nickname = 'None',
                    group_id = bodyjson['events'][0]['source']['groupId'],
                    type = bodyjson['events'][0]['source']['type'],
                    status = 'save',
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


def get_groupPeople(history_list,mode):
    selfId = history_list[0]['user_id']
    selfGroupId = history_list[0]['group_id']
    SetMsgNumber = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='set').count()
    data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='set')
    history_dic = {}
    history_list = []
    for _data in data_UserData:
        history_dic['nickname'] = _data.nickname
        history_list.append(history_dic)
        history_dic = {}
    final_list =[]
    for i in range(SetMsgNumber):
        final_list.append(str(history_list[i]['nickname']))
    count=0
    new_list = []
    for i in final_list:
        if not i in new_list:
            new_list.append(i)
            count+=1

    if mode ==1:
        return count
    elif mode ==2:
        return new_list
    else:
        return 1



# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text.lower()
    data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).limit(1).all()
    history_dic = {}
    history_list = []    
    for _data in data_UserData:
        history_dic['Status'] = _data.status
        history_dic['type'] = _data.type
        history_dic['user_id'] = _data.user_id
        history_dic['group_id'] = _data.group_id
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
            data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='save').filter(usermessage.type=='user')
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
            add=0
            for i in range(count):
                try:
                    money = int(history_list[i]['Account'])
                except:
                    money = 0
                final_list.append(str(history_list[i]['Mesaage'])+' '+str(history_list[i]['Account']))
                add += money

            perfect_list=''
            for j in range(count):
                perfect_list=perfect_list+str(j+1)+'.'+str(final_list[j])+'\n'
            perfect_list = perfect_list+'\n'+'累計花費:'+str(add)
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
        elif input_text =='help':
            help_text='1.記帳--輸入：記帳 項目 金額'+'\n'+'ex：記帳 麥當勞 200'+'\n'+'2.查帳--輸入：查帳'+'\n'+'3.刪除--輸入：刪除'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(help_text)))

        else:
            output_text='記帳失敗'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        
    else:
        if (history_list[0]['Status'] == 'set') and ('分帳設定' in input_text):
            groupNumber=get_groupPeople(history_list,1)
            output_text='分帳設定成功:共有'+str(groupNumber)+'人分帳'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str( output_text )))
        elif (history_list[0]['Status'] == 'save') and ('分帳' in input_text):
            output_text='分帳紀錄成功'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))

        elif input_text == '設定查詢':
            groupMember=get_groupPeople(history_list,2)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str( groupMember )))

        elif ('結算' in input_text):
            selfGroupId = history_list[0]['group_id']
            dataSettle_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group')
            historySettle_dic = {}
            historySettle_list = []
            person_list = get_groupPeople(history_list,2)
            count=0
            for _data in dataSettle_UserData:
                count+=1
                historySettle_dic['Mesaage'] = _data.message
                historySettle_dic['Account'] = _data.account
                historySettle_dic['GroupPeople'] =_data.group_num
                historySettle_list.append(historySettle_dic)
                historySettle_dic = {}
            
            dataNumber=len(historySettle_list)
            Zero= np.zeros((dataNumber,get_groupPeople(history_list,1)))
            for i in range(dataNumber):
                b=dict(historySettle_list[i])
                GroupPeopleString=b['GroupPeople'].split(' ')
                payAmount=int(b['Account'])/len(GroupPeopleString)
                a1=set(get_groupPeople(history_list,2))
                a2=set(GroupPeopleString)
                duplicate = list(a1.intersection(a2))
                count=0
                for j in range(len(duplicate)):
                    place=get_groupPeople(history_list,2).index(duplicate[count])
                    Zero[i][place]=payAmount
                    count+=1

            replaceZero=Zero
            totalPayment=replaceZero.sum(axis=0)

            paid= np.zeros((1,len(get_groupPeople(history_list,2))))
            for i in range(len(get_groupPeople(history_list,2))):
                for j in range(len(historySettle_list)):
                    b=dict(historySettle_list[j])
                    GroupPeopleString=b['GroupPeople'].split(' ')
                    if GroupPeopleString[0] == get_groupPeople(history_list,2)[i]:
                        paidAmount=int(b['Account'])
                        paid[0][i]=paid[0][i]+paidAmount
                    else:
                        continue
            account=paid-totalPayment

            #將人和錢結合成tuple，存到一個空串列
            person_account=[]
            for i in range(len(person_list)):
                zip_tuple=(person_list[i],account[0][i])
                person_account.append(zip_tuple)

            #重複執行交換動作
            for i in range(len(person_list)-1):
                #排序
                person_account=sorted(person_account, key = lambda s:s[1])

                #找到最大、最小值
                min_tuple=person_account[0]
                max_tuple=person_account[-1]
                min=float(min_tuple[1])
                max=float(max_tuple[1])

                #交換，印出該付的錢
                result=[]
                if min==0 or max==0:
                    pass
                elif (min+max)>0:
                    result=result+(str(min_tuple[0])+'付給'+str(max_tuple[0])+str(abs(min))+'\n')
                    max_tuple=(max_tuple[0],min+max)
                    min_tuple=(min_tuple[0],0)
                elif (min+max)<0:
                    result=result+(str(min_tuple[0])+'付給'+str(max_tuple[0])+str(abs(max))+'\n')
                    min_tuple=(min_tuple[0],min+max)
                    max_tuple=(max_tuple[0],0)
                else:
                    result=result+(str(min_tuple[0])+'付給'+str(max_tuple[0])+str(abs(max))+'\n')
                    min_tuple=(min_tuple[0],0)
                    max_tuple=(max_tuple[0],0)
                person_account[0]=min_tuple
                person_account[-1]=max_tuple
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(result)))
                

        
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
