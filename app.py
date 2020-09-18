from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    SourceUser,SourceGroup,SourceRoom,LeaveEvent,JoinEvent,
    TemplateSendMessage,ButtonsTemplate,CarouselTemplate,CarouselColumn,
    MessageTemplateAction,URITemplateAction,PostbackEvent,AudioMessage,LocationMessage,
    MessageEvent, TextMessage, TextSendMessage ,FollowEvent, UnfollowEvent
)

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

import requests
from bs4 import BeautifulSoup
from dbModel import *
from datetime import datetime
import json
from sqlalchemy import desc
import numpy as np
import sys
import re
import time

app = Flask(__name__)

line_bot_api = LineBotApi('bHi/8szU2mkZAaIMLGDKqTE8CnG4TjilHVVJsqDse2XD39ZUGdxiHRedvOGSC5Q7zJfFYZoOAIoMxeKAR5mQqbz0DomlYKjU7gMEK/zQ0QJFFVJLpDhwB8DRrJ8SAoqK+sEAMuD2PL0h0wdsZxncRwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2ee6a86bd730b810a7d614777f07cecb')


@app.route("/")
def home():
    return 'home OK'


def get_TodayRate(mode):
    numb= []
    cate=[]
    data=[]
    url_1= "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    resp_1 = requests.get(url_1)
    ms = BeautifulSoup(resp_1.text,"html.parser")

    t1=ms.find_all("td","rate-content-cash text-right print_hide")
    for child in t1:
        numb.append(child.text.strip())

    buy=numb[0:37:2]
    sell=numb[1:38:2]

    t2=ms.find_all("div","hidden-phone print_show")
    for child in t2:
        cate.append(child.text.strip())
    for i in range(19):
        data.append([cate[i] +'買入：'+buy[i]+ '賣出：'+sell[i]])

    if mode==1:
        USD = data[0][0]
        regex = re.compile(r'賣出：(\d+.*\d*)')
        match = regex.search(USD)
        return eval(match.group(1))
    elif mode==2:
        JPY = data[7][0]
        regex = re.compile(r'賣出：(\d+.*\d*)')
        match = regex.search(JPY)
        return eval(match.group(1))
    elif mode==3:
        EUR = data[14][0]
        regex = re.compile(r'賣出：(\d+.*\d*)')
        match = regex.search(EUR)
        return eval(match.group(1))
    else:
        return 1

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    bodyjson=json.loads(body)
    app.logger.error("Request body: " + body)
    if bodyjson['events'][0]['type'] != 'join' : 
        Group_id='None'
        if bodyjson['events'][0]['source']['type'] == 'group':
            Group_id =  bodyjson['events'][0]['source']['groupId']
        add_data = usermessage(
        id = bodyjson['events'][0]['message']['id'],
        group_num = '0',
        nickname = 'None',
        group_id = Group_id,
        type = bodyjson['events'][0]['source']['type'],
        status = 'None',
        account = '0',
        user_id = bodyjson['events'][0]['source']['userId'],
        message = bodyjson['events'][0]['message']['text'],
        birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
        )

        if bodyjson['events'][0]['source']['type'] == 'group':
            receivedmsg = bodyjson['events'][0]['message']['text']
            if '分帳設定' in receivedmsg: 
                userName = receivedmsg.strip(' 分帳設定 ')
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
            elif ('分帳' in receivedmsg)  and (len(re.findall(r" ",receivedmsg)) >= 3):           
                chargeName=receivedmsg.split(' ',3)[1]
                chargeNumber=receivedmsg.split(' ',3)[2]
                chargePeople=receivedmsg.split(' ',3)[3]            
                if re.search(r"\D",chargeNumber) is None:
                    add_data = usermessage(
                        id = bodyjson['events'][0]['message']['id'],
                        group_num = chargePeople.strip(' ') ,
                        nickname = 'None',
                        group_id = bodyjson['events'][0]['source']['groupId'],
                        type = bodyjson['events'][0]['source']['type'],
                        status = 'save',
                        account = chargeNumber,
                        user_id = bodyjson['events'][0]['source']['userId'],
                        message = chargeName,
                        birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                    )
            elif ('美金設定' in receivedmsg):           
                add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num =  '0' ,
                    nickname = 'None',
                    group_id = bodyjson['events'][0]['source']['groupId'],
                    type = bodyjson['events'][0]['source']['type'],
                    status = 'USD',
                    account = '0', 
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = get_TodayRate(1),
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
            elif ('日圓設定' in receivedmsg):           
                add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num =  '0' ,
                    nickname = 'None',
                    group_id = bodyjson['events'][0]['source']['groupId'],
                    type = bodyjson['events'][0]['source']['type'],
                    status = 'JPY',
                    account = '0', 
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = get_TodayRate(2),
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
            elif ('歐元設定' in receivedmsg):           
                add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'],
                    group_num =  '0' ,
                    nickname = 'None',
                    group_id = bodyjson['events'][0]['source']['groupId'],
                    type = bodyjson['events'][0]['source']['type'],
                    status = 'EUR',
                    account = '0', 
                    user_id = bodyjson['events'][0]['source']['userId'],
                    message = get_TodayRate(3),
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                )
                
        else:
            receivedmsg = bodyjson['events'][0]['message']['text']
            receivedmsg = receivedmsg.strip(' ')
            if ('記帳' in receivedmsg) and (len(re.findall(r" ",receivedmsg)) == 2):
                chargeName=receivedmsg.split(' ')[1]
                chargeNumber=receivedmsg.split(' ')[2]
                if re.search(r"\D",chargeNumber) is None:
                    add_data = usermessage(
                            id = bodyjson['events'][0]['message']['id'],
                            group_num = '0',
                            nickname = 'None',
                            group_id = 'None',
                            type = bodyjson['events'][0]['source']['type'],
                            status = 'save',
                            account = chargeNumber,
                            user_id = bodyjson['events'][0]['source']['userId'],
                            message = chargeName ,
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


def get_movie():   #電影討論度
    movies = []
    url_1= "https://movies.yahoo.com.tw/chart.html"
    resp_1 = requests.get(url_1)
    ms = BeautifulSoup(resp_1.text,"html.parser")

    ms.find_all("div","rank_txt")
    movies.append(ms.find('h2').text)

    for rank_txt in ms.find_all("div","rank_txt"):
        movies.append(rank_txt.text.strip())

    return movies


def get_exchangeRate(mode):
    if mode==1:
        data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).filter(usermessage.status=='USD' ).limit(1).all()
        history_dic = {}
        history_list = []
        for _data in data_UserData:
            history_dic['Mesaage'] = _data.message
            history_list.append(history_dic)
        USDrate=eval(history_dic['Mesaage'])
        return USDrate
    if mode==2:
        data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).filter(usermessage.status=='JPY' ).limit(1).all()
        history_dic = {}
        history_list = []
        for _data in data_UserData:
            history_dic['Mesaage'] = _data.message
            history_list.append(history_dic)
        JPYrate=eval(history_dic['Mesaage'])
        return JPYrate
    if mode==3:
        data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).filter(usermessage.status=='EUR' ).limit(1).all()
        history_dic = {}
        history_list = []
        for _data in data_UserData:
            history_dic['Mesaage'] = _data.message
            history_list.append(history_dic)
        EURrate=eval(history_dic['Mesaage'])
        return EURrate

def get_history_list():   #取得最新資料
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
    return history_list

#記帳查帳
def get_accountList(selfId):
    time.sleep(0.2)
    data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.user_id==selfId).filter(usermessage.status=='save').filter(usermessage.type=='user')
    history_dic = {}
    history_list = []
    count=0
    for _data in data_UserData:
        count+=1
        history_dic['birth_date'] = _data.birth_date
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
        msgTime = str(history_list[i]['birth_date'])
        final_list.append(msgTime[:10]+' '+str(history_list[i]['Mesaage'])+' '+str(history_list[i]['Account']))
        add += money

    perfect_list=''
    for j in range(count):
        perfect_list=perfect_list+str(j+1)+'.'+str(final_list[j])+'\n'
    perfect_list = perfect_list+'\n'+'累計花費:'+str(add)
    return perfect_list

#分帳查帳
def get_settleList():
    history_list = get_history_list()
    selfGroupId = history_list[0]['group_id']
    dataSettle_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group')
    historySettle_list = []
    for _data in dataSettle_UserData:
        historySettle_dic = {}
        historySettle_dic['Mesaage'] = _data.message
        historySettle_dic['Account'] = _data.account
        historySettle_dic['GroupPeople'] =_data.group_num
        historySettle_dic['Time'] =_data.birth_date
        historySettle_list.append(historySettle_dic)
    final_list =[]
    for i in range(len(historySettle_list)):
        settleTime = str(historySettle_list[i]['Time'])
        final_list.append(settleTime[:10]+' '+str(historySettle_list[i]['Mesaage'])+' '+str(historySettle_list[i]['Account'])+' '+str(historySettle_list[i]['GroupPeople']))
    perfect_list=''
    for j in range(len(final_list)):
        perfect_list += str(j+1)+'.'+str(final_list[j])+'\n'
    return perfect_list

#群組人數/名單
def get_groupPeople(history_list,mode):
    selfGroupId = history_list[0]['group_id']
    data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='set')
    GroupPeopleString=''
    for _data in data_UserData:
        GroupPeopleString += _data.nickname.strip(' ') +' '
    new_list = GroupPeopleString.strip(' ').split(' ')
    new_list=list(set(new_list)) #刪除重複

    if mode ==1:
        return len(new_list)
    elif mode ==2:
        return new_list
    else:
        return 0

#處理加入群組

@handler.add(JoinEvent)
def handle_join(event):
    
    message = ImagemapSendMessage(
                            base_url="https://i.imgur.com/pABJnFu.png",
                            alt_text='選擇',
                            base_size=BaseSize(height=1040, width=1040),
                            actions=[
            URIImagemapAction(
                #分帳者設定
                link_uri="https://liff.line.me/1654876504-QNXjnrl2",
                area=ImagemapArea(
                    x=100, y=555, width=420, height=235
                )
            ),
            URIImagemapAction(
                #記錄分帳
                link_uri="https://liff.line.me/1654876504-9wWzOva7",
                area=ImagemapArea(
                    x=100, y=315, width=420, height=235
                )
            ),
            MessageImagemapAction(
                #使用說明
                text="@help",
                area=ImagemapArea(
                    x=530, y=555, width=420, height=235
                )
            ),
            URIImagemapAction(
                #查帳結算
                link_uri="https://liff.line.me/1654876504-rK3v07Pk",
                area=ImagemapArea(
                    x=530, y=315, width=420, height=235
                )
            )
        ]
                       
                            )
    line_bot_api.reply_message(event.reply_token,message)


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text.lower()
    history_list = get_history_list()
    if history_list[0]['type'] == 'user':      #個人部分
        if (history_list[0]['Status'] == 'save') and ('記帳' in input_text):
            output_text='記帳成功'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
                
        elif input_text =='查帳':
            selfId = history_list[0]['user_id']
            for i in range(10):
                output_text = get_accountList(selfId)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        
        elif input_text =='@help':
            help_text='1.記帳--輸入：記帳 項目 金額'+'\n'+'ex：記帳 麥當勞 200'+'\n'+'2.查帳--輸入：查帳'+'\n'+'3.理財小幫手--輸入：理財'+'\n'+'4.刪除--輸入：刪除' +'\n'+'5.刪除單筆資料--輸入：delete 編號'+'\n'+'6.使用說明--輸入：help'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(help_text)))

        elif input_text =='理財':            
            line_bot_api.reply_message(  
            event.reply_token,
            TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='理財小幫手',
                    text='請選擇功能',
                    actions=[
                        URITemplateAction(
                            label='股市',
                            uri='https://tw.stock.yahoo.com/'
                        ),
                        URITemplateAction(
                            label='匯率',
                            uri='https://rate.bot.com.tw/xrt?Lang=zh-TW'
                        ),
                        URITemplateAction(
                            label='財經新聞',
                            uri='https://www.msn.com/zh-tw/money'
                        )
                        ]
                    )
                )
            )

        elif input_text =='刪除':
            selfId = history_list[0]['user_id']
            for i in range(3):
                data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='save').delete(synchronize_session='fetch')
            output_text='刪除成功'
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        elif 'delete' in input_text:
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
            deleteNum=re.findall(r"\d+\.?\d*",input_text)

            targetNum = int(deleteNum[0])
            if targetNum > count:
                output_text='刪除失敗'
            else:
                data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.user_id==selfId).filter(usermessage.status=='save').filter(usermessage.type=='user')[targetNum-1:targetNum]
                history_dic = {}
                history_list = []
                count=0
                for _data in data_UserData:
                    count+=1
                    history_dic['Mesaage'] = _data.message
                    history_dic['Account'] = _data.account
                    history_dic['id'] = _data.id
                    history_list.append(history_dic)
                personID=history_dic['id']
                data_UserData = usermessage.query.filter(usermessage.id==personID).delete(synchronize_session='fetch')
                output_text='刪除成功'+'\n\n'+'記帳清單：'+'\n'+get_accountList(selfId)
                db.session.commit()

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        

        else:
            output_text='記帳失敗，請再檢查記帳格式'+'\n'+'輸入：記帳 項目 金額'+'\n'+'ex：記帳 麥當勞 200'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        
    else:  #群組部分
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
            output_text="分帳名單:"
            for i in range(get_groupPeople(history_list,1)):
                output_text+='\n'+groupMember[i]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str( output_text )))

        elif '美金設定' in input_text:
            NowRate=get_TodayRate(1)
            output_text="今日匯率："+str(NowRate)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str( output_text )))

        elif '日圓設定' in input_text:
            NowRate=get_TodayRate(2)
            output_text="今日匯率："+str(NowRate)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str( output_text )))
        
        elif '歐元設定' in input_text:
            NowRate=get_TodayRate(3)
            output_text="今日匯率："+str(NowRate)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str( output_text )))

        elif input_text == '刪除':
            selfId = history_list[0]['user_id']
            selfGroupId = history_list[0]['group_id']
            for i in range(3):
                data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='save').delete(synchronize_session='fetch')
            output_text='刪除成功'
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))

        elif input_text == '設定刪除':
            selfGroupId = history_list[0]['group_id']
            data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='set').delete(synchronize_session='fetch')
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= '設定刪除成功'))

        elif 'delete' in input_text:
            selfGroupId = history_list[0]['group_id']
            data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='save')
            history_dic = {}
            history_list = []
            count=0
            for _data in data_UserData:
                count+=1
                history_dic['Mesaage'] = _data.message
                history_dic['Account'] = _data.account
                history_list.append(history_dic)
                history_dic = {}
            deleteNum=re.findall(r"\d+\.?\d*",input_text)

            targetNum = int(deleteNum[0])
            if targetNum > count:
                output_text='刪除失敗'
            else:
                data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='save')[targetNum-1:targetNum]
                history_dic = {}
                history_list = []
                count=0
                for _data in data_UserData:
                    count+=1
                    history_dic['Mesaage'] = _data.message
                    history_dic['Account'] = _data.account
                    history_dic['id'] = _data.id
                    history_list.append(history_dic)

                targetID=history_dic['id']
                data_UserData = usermessage.query.filter(usermessage.id==targetID).delete(synchronize_session='fetch')
                output_text='刪除成功'+'\n\n'+'分帳清單：'+'\n'+get_settleList()
                db.session.commit()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= str(output_text)))

        elif input_text == '查帳':
            output_text = get_settleList()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))

        elif input_text =='理財':            
            line_bot_api.reply_message(  
            event.reply_token,
            TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='理財小幫手',
                    text='請選擇功能',
                    actions=[
                        URITemplateAction(
                            label='股市',
                            uri='https://tw.stock.yahoo.com/'
                        ),
                        URITemplateAction(
                            label='匯率',
                            uri='https://rate.bot.com.tw/xrt?Lang=zh-TW'
                        ),
                        URITemplateAction(
                            label='財經新聞',
                            uri='https://www.msn.com/zh-tw/money'
                        )
                        ]
                    )
                )
            )

        elif input_text =='結算':            
            selfGroupId = history_list[0]['group_id']
            dataSettle_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group')
            historySettle_list = []
            person_list  = get_groupPeople(history_list,2)
            person_num = get_groupPeople(history_list,1)
            for _data in dataSettle_UserData:
                historySettle_dic = {}
                historySettle_dic['Account'] = _data.account
                historySettle_dic['GroupPeople'] =_data.group_num
                historySettle_dic['message'] = _data.message
                historySettle_list.append(historySettle_dic)
            
            dataNumber=len(historySettle_list)
            account = np.zeros(person_num)
            exchange_rate_USD = 0
            exchange_rate_JPY = 0
            exchange_rate_EUR = 0
            for i in range(dataNumber):
                b=dict(historySettle_list[i])
                GroupPeopleString=b['GroupPeople'].strip(' ').split(' ')  #刪除代墊者
                del GroupPeopleString[0]
                
                if 'USD' in b['message']:   #匯率轉換
                    if exchange_rate_USD:
                        exchange_rate = exchange_rate_USD
                    else:
                        exchange_rate_USD = get_exchangeRate(1)
                        exchange_rate = exchange_rate_USD
                elif 'JPY' in b['message']:
                    if exchange_rate_JPY:
                        exchange_rate = exchange_rate_JPY
                    else:
                        exchange_rate_JPY = get_exchangeRate(2)
                        exchange_rate = exchange_rate_JPY
                elif 'EUR' in b['message']:
                    if exchange_rate_EUR:
                        exchange_rate = exchange_rate_EUR
                    else:
                        exchange_rate_EUR = get_exchangeRate(1)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1

                payAmount = exchange_rate*int(b['Account']) / len(GroupPeopleString)
                a1=set(person_list)      #分帳設定有的人
                a2=set(GroupPeopleString)
                duplicate = list(a1.intersection(a2))       #a1和a2重複的人名
                for j in range(len(duplicate)):      #分帳金額
                    place=person_list.index(duplicate[j])
                    account[place] -= payAmount
                    
            for j in range(dataNumber):
                b=dict(historySettle_list[j])
                GroupPeopleString=b['GroupPeople'].strip(' ').split(' ')
                if 'USD' in b['message']:   #匯率轉換
                    if exchange_rate_USD:
                        exchange_rate = exchange_rate_USD
                    else:
                        exchange_rate_USD = get_exchangeRate(1)
                        exchange_rate = exchange_rate_USD
                elif 'JPY' in b['message']:
                    if exchange_rate_JPY:
                        exchange_rate = exchange_rate_JPY
                    else:
                        exchange_rate_JPY = get_exchangeRate(2)
                        exchange_rate = exchange_rate_JPY
                elif 'EUR' in b['message']:
                    if exchange_rate_EUR:
                        exchange_rate = exchange_rate_EUR
                    else:
                        exchange_rate_EUR = get_exchangeRate(1)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1

                for i in range(person_num):  #代墊金額
                    if GroupPeopleString[0] ==  person_list[i]:
                        account[i] += exchange_rate * int(b['Account'])

            #將人和錢結合成tuple，存到一個空串列
            person_account=[]
            for i in range(person_num):
                zip_tuple=(person_list[i],account[i])
                person_account.append(zip_tuple)

            #重複執行交換動作
            result=""
            for i in range(person_num-1):  #排序
                person_account=sorted(person_account, key = lambda s:s[1])

                #找到最大、最小值
                min_tuple=person_account[0]
                max_tuple=person_account[-1]
                min=float(min_tuple[1])
                max=float(max_tuple[1])

                #交換，印出該付的錢
                if min==0 or max==0:
                    pass
                elif (min+max)>0:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+str(abs(round(min,2)))+'元'+'\n'
                    max_tuple=(max_tuple[0],min+max)
                    min_tuple=(min_tuple[0],0)
                elif (min+max)<0:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+str(abs(round(max,2)))+'元'+'\n'
                    min_tuple=(min_tuple[0],min+max)
                    max_tuple=(max_tuple[0],0)
                else:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+str(abs(round(max,2)))+'元'+'\n'
                    min_tuple=(min_tuple[0],0)
                    max_tuple=(max_tuple[0],0)
                
                person_account[0]=min_tuple
                person_account[-1]=max_tuple
            # result=result+'\n'+'下次不要再讓'+str(max_tuple[0])+'付錢啦! TA幫你們付很多了!'

            output_text = result
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))


        elif input_text =='不簡化':        
            selfGroupId = history_list[0]['group_id']
            dataSettle_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group')
            historySettle_list = []
            for _data in dataSettle_UserData:
                historySettle_dic = {}
                historySettle_dic['Account'] = _data.account
                historySettle_dic['GroupPeople'] =_data.group_num
                historySettle_list.append(historySettle_dic)
                
            result=""
            dataNumber=len(historySettle_list)
            for i in range(dataNumber):
                b=dict(historySettle_list[i])
                GroupPeopleString=b['GroupPeople'].split(' ')  #分帳者設定 
                payer=GroupPeopleString[0] #抓出代墊者
                del GroupPeopleString[0]
                payAmount=round( int(b['Account']) / len(GroupPeopleString) ,2)
                a1=set(get_groupPeople(history_list,2))      #分帳設定有的人
                a2=set(GroupPeopleString)
                duplicate = list(a1.intersection(a2))      #a1和a2重複的人名
                for j in range(len(duplicate)):          #分帳金額
                    if str(duplicate[j]) != payer:
                        result += str(duplicate[j])+'付給'+payer+str(payAmount)+'元'+'\n'

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= result))

        elif input_text =='稍微':             
            selfGroupId = history_list[0]['group_id'] 
            dataSettle_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group') 
            historySettle_list = [] 
            person_list  = get_groupPeople(history_list,2)  #分帳設定人名
            person_num = get_groupPeople(history_list,1)  #分帳設定人數
            for _data in dataSettle_UserData: 
                historySettle_dic = {} 
                historySettle_dic['Account'] = _data.account 
                historySettle_dic['GroupPeople'] =_data.group_num 
                historySettle_list.append(historySettle_dic) 
                
            dataNumber=len(historySettle_list) 
            account= np.zeros((person_num,person_num)) 
            for i in range(dataNumber): 
                b=dict(historySettle_list[i]) 
                GroupPeopleString=b['GroupPeople'].split(' ')
                payAmount = round( int(b['Account']) / (len(GroupPeopleString)-1),2)  #不包含代墊者
                a1=set(person_list)      #分帳設定有的人 
                a2=set(GroupPeopleString) 
                duplicate = list(a1.intersection(a2))         #a1和a2重複的人名 
                for j in range(len(duplicate)):      #誰付誰錢矩陣 2給1 
                    place1=person_list.index(GroupPeopleString[0]) 
                    place2=person_list.index(duplicate[j]) 
                    account[place1][place2]+=payAmount 
            result=""
            for i in range ( person_num ): #誰付誰錢輸出 
                for j in range ( person_num ): 
                    if i!=j and account[i][j] != 0 : 
                        result += person_list[j]+'付給'+person_list[i] + str(account[i][j]) +'元'+'\n' 

            line_bot_api.reply_message( 
                event.reply_token, 
                TextSendMessage(text= result )) 
     
        elif input_text == '清空資料庫':
            data_UserData = usermessage.query.filter(usermessage.status=='None').delete(synchronize_session='fetch')
            db.session.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= '爽啦沒資料囉\n請重新設定匯率'))

        elif input_text =='@help' :
            Carousel_template = TemplateSendMessage(
                            alt_text='使用說明',
                            template=ImageCarouselTemplate(
                            columns=[
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/m4fkFQJ.jpg",
                    action=URITemplateAction(
                        uri="https://i.imgur.com/m4fkFQJ.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://imgur.com/Y1BoSsp.jpg",
                    action=URITemplateAction(
                        uri="https://imgur.com/Y1BoSsp.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://imgur.com/ZuV1blU.jpg",
                    action=URITemplateAction(
                        uri="https://imgur.com/Y1BoSsp.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://imgur.com/uJKYIsg.jpg",
                    action=URITemplateAction(
                        uri="https://imgur.com/Y1BoSsp.jpg"
                    )

                )
            ]     
                            )
                        )
            line_bot_api.reply_message(event.reply_token,Carousel_template)
        elif input_text =='@選單'  :
            message = ImagemapSendMessage(
                            base_url="https://i.imgur.com/CzIxqa1.png",
                            alt_text='功能總覽',
                            base_size=BaseSize(height=1040, width=1240),
                            actions=[
            URIImagemapAction(
                #分帳者設定
                link_uri="https://liff.line.me/1654876504-QNXjnrl2",
                area=ImagemapArea(
                    x=60, y=659, width=479, height=274
                )
            ),
            URIImagemapAction(
                #記錄分帳
                link_uri="https://liff.line.me/1654876504-9wWzOva7",
                area=ImagemapArea(
                    x=60, y=381, width=479, height=274
                )
            ),
            MessageImagemapAction(
                #使用說明
                text="@help",
                area=ImagemapArea(
                    x=543, y=653, width=462, height=273
                )
            ),
            URIImagemapAction(
                #查帳結算
                link_uri="https://liff.line.me/1654876504-rK3v07Pk",
                area=ImagemapArea(
                    x=543, y=373, width=445, height=282
                )
            )
        ]
                       
                            )
                        
            line_bot_api.reply_message(event.reply_token,message)
        elif (eval(input_text)>0) and (eval(input_text)<=100000):
            output_text= input_text
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text))) 
        else:
            hot_movie=get_movie()
            output_text=hot_movie
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= str(output_text)))
        
            line_bot_api.reply_message(event.reply_token,message)




if __name__ == "__main__":
    app.run()
