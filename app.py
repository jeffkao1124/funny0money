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
    MessageEvent, TextMessage, TextSendMessage ,FollowEvent, UnfollowEvent,FlexSendMessage
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
import os


app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
#line_bot_api = LineBotApi('TZsCLYkAR8JisqPGq5PmXUFmSi9mPvRtS3nt9zyOJ6lBfeL7RYX5ZWrMOFv71lIqzJfFYZoOAIoMxeKAR5mQqbz0DomlYKjU7gMEK/zQ0QKRDe5W8HdSK9UgwJ1Nk+pLXA+i6Seo3UMAHdhVX1H6eQdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('39eb0abc9f8d96c8527cc94c3bdf9982')


@app.route("/")
def home():
    return 'home OK'

#爬蟲取得匯率
def get_TodayRate(mode):
    numb= []
    cate=[]
    data=[]
    url_1= "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    resp_1 = requests.get(url_1)
    ms =BeautifulSoup(resp_1.text,"html.parser")

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

def get_Boardgame():
    boardgame= []
    url_1= "https://boardgamegeek.com/browse/boardgame"
    resp_1 = requests.get(url_1)
    ms = BeautifulSoup(resp_1.text,"html.parser")

    for i in range(50):
        t1=ms.find_all("div",id="results_objectname"+str(i))
        for bgg in t1:
            boardgame.append(bgg.text.strip())

    return boardgame




# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    # signature = request.headers['X-Line-Signature']
    signature = request.headers['x-line-signature']

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
            if '@分帳設定' in receivedmsg: 
                userName = receivedmsg.strip(' @分帳設定 ').replace('  ',' ')
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
            elif ('@分帳' in receivedmsg)  and (len(re.findall(r" ",receivedmsg)) >= 3):           
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
            if ('@記帳' in receivedmsg) and (len(re.findall(r" ",receivedmsg)) == 2):
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
            elif '@欠款設定' in receivedmsg:
                debtName = receivedmsg.strip(' @欠款設定 ').replace('  ',' ')
                add_data = usermessage(
                    id = bodyjson['events'][0]['message']['id'], 
                    group_num = '0', 
                    nickname = debtName, 
                    group_id =  'None', 
                    type = bodyjson['events'][0]['source']['type'], 
                    status = 'debt_set', 
                    account = '0', 
                    user_id = bodyjson['events'][0]['source']['userId'], 
                    message = bodyjson['events'][0]['message']['text'], 
                    birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000) 
                )
            elif (('我欠' in receivedmsg)or('我借' in receivedmsg))  and (len(re.findall(r" ",receivedmsg)) == 3):           
                debtType=receivedmsg.split(' ')[0]
                debtPerson=receivedmsg.split(' ')[1]
                debtName=receivedmsg.split(' ')[2]
                debtAccount=receivedmsg.split(' ')[3]            
                if re.search(r"\D",debtAccount) is None:
                    if '欠' in debtType:
                        add_data = usermessage(
                            id = bodyjson['events'][0]['message']['id'],
                            group_num = debtPerson ,
                            nickname = 'None',
                            group_id = 'None',
                            type = bodyjson['events'][0]['source']['type'],
                            status = 'owe',
                            account = debtAccount,
                            user_id = bodyjson['events'][0]['source']['userId'],
                            message = debtName,
                            birth_date = datetime.fromtimestamp(int(bodyjson['events'][0]['timestamp'])/1000)
                        )
                    if '借' in debtType:
                        add_data = usermessage(
                            id = bodyjson['events'][0]['message']['id'],
                            group_num = debtPerson ,
                            nickname = 'None',
                            group_id = 'None',
                            type = bodyjson['events'][0]['source']['type'],
                            status = 'borrow',
                            account = debtAccount,
                            user_id = bodyjson['events'][0]['source']['userId'],
                            message = debtName,
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

#從資料庫取得匯率
def get_exchangeRate(mode):
    if mode==1:
        data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).filter(usermessage.status=='USD' ).limit(1).all()
        for _data in data_UserData:
            USDrate = eval(_data.message)
        return USDrate
    if mode==2:
        data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).filter(usermessage.status=='JPY' ).limit(1).all()
        for _data in data_UserData:
            JPYrate=eval(_data.message)
        return JPYrate
    if mode==3:
        data_UserData = usermessage.query.order_by(usermessage.birth_date.desc()).filter(usermessage.status=='EUR' ).limit(1).all()
        for _data in data_UserData:
            EURrate=eval(_data.message)
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
    return history_list

#記帳查帳
def get_accountList(selfId):
    time.sleep(0.2)
    data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.user_id==selfId).filter(usermessage.status=='save').filter(usermessage.type=='user')
    history_list = []
    for _data in data_UserData:
        history_dic = {}
        history_dic['birth_date'] = _data.birth_date
        history_dic['Mesaage'] = _data.message
        history_dic['Account'] = _data.account
        history_list.append(history_dic)
    
    total = 0
    final_list =[]
    for i in range(len(history_list)):
        total += int(history_list[i]['Account'])
        msgTime = str(history_list[i]['birth_date'])
        final_list.append(msgTime[:10]+' '+str(history_list[i]['Mesaage'])+' '+str(history_list[i]['Account']))

    perfect_list=''
    for j in range(len(final_list)):
        perfect_list=perfect_list+str(j+1)+'.'+str(final_list[j])+'\n'
    perfect_list = perfect_list+'\n'+'累計花費:'+str(total)
    return perfect_list

#欠款查詢
def get_debtList(selfId):
    time.sleep(0.2)
    data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.user_id==selfId).filter(usermessage.status==('owe')).filter(usermessage.type=='user')
    history_list = []
    for _data in data_UserData:
        history_dic = {}
        history_dic['birth_date'] = _data.birth_date
        history_dic['Mesaage'] = _data.message
        history_dic['Account'] = _data.account
        history_dic['debtPerson']=_data.group_num
        history_dic['debtStatus']=_data.status
        history_list.append(history_dic)

    data_userData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.user_id==selfId).filter(usermessage.status==('borrow')).filter(usermessage.type=='user')
    for _data in data_userData:
        history_dic = {}
        history_dic['birth_date'] = _data.birth_date
        history_dic['Mesaage'] = _data.message
        history_dic['Account'] = _data.account
        history_dic['debtPerson']=_data.group_num
        history_dic['debtStatus']=_data.status
        history_list.append(history_dic)

    total = 0
    final_list =[]
    for i in range(len(history_list)):
        msgStatus = str(history_list[i]['debtStatus'])
        if msgStatus == "owe":
            showStatus ="我欠"
        if msgStatus == "borrow":
            showStatus ="我借"            
        final_list.append(str(showStatus)+str(history_list[i]['debtPerson'])+str(history_list[i]['Mesaage'])+str(history_list[i]['Account'])+'元')

    debtPerson_list=get_debtPeople(selfId,2)
    person_total=''
    total = 0
    for i in range(get_debtPeople(selfId,1)):
        debtPerson = str(debtPerson_list[i])        
        for j in range(len(history_list)):
            historyPerson = str(history_list[j]['debtPerson'])
            msgStatus = str(history_list[j]['debtStatus'])
            if debtPerson == historyPerson:
                if msgStatus == "owe":
                    total -= int(history_list[j]['Account'])
                if msgStatus == "borrow":
                    total += int(history_list[j]['Account'])
        if total > 0:
            person_total += '我共借'+str(debtPerson)+str(total)+'元'+'\n'
        elif total < 0:
            total=abs(total)
            person_total += '我共欠'+str(debtPerson)+str(total)+'元'+'\n'
        else:
            person_total += '我不欠'+str(debtPerson)+','+str(debtPerson)+'不欠我'+'\n'
        total = 0

    perfect_list=''
    for j in range(len(final_list)):
        perfect_list=perfect_list+str(j+1)+'.'+str(final_list[j])+'\n'
    perfect_list = perfect_list+'\n'+person_total
    return perfect_list

#欠款設定
def get_debtPeople(selfId,mode):
    data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='debt_set')
    DebtPeopleString=''
    for _data in data_UserData:
        DebtPeopleString += _data.nickname.strip(' ') +' '
    new_list = DebtPeopleString.strip(' ').replace('  ',' ').split(' ')
    new_list=list(set(new_list)) #刪除重複

    if mode ==1:
        return len(new_list)
    elif mode ==2:
        return new_list
    else:
        return 0

#分帳查帳
def get_settleList(selfGroupId):
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
        final_list.append(settleTime[:10]+' '+str(historySettle_list[i]['Mesaage'])+' '+str(historySettle_list[i]['Account']))
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
    new_list = GroupPeopleString.strip(' ').replace('  ',' ').split(' ')
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
                            base_url="https://imgur.com/cODeL32.jpg",
                            alt_text='啾啾啾',
                            base_size=BaseSize(height=927, width=1040),
                            actions=[
            URIImagemapAction(
                #分帳者設定
                link_uri="https://liff.line.me/1654876504-QNXjnrl2",
                area=ImagemapArea(
                    x=0, y=464, width=522, height=459
                )
            ),
            URIImagemapAction(
                #記錄分帳
                link_uri="https://liff.line.me/1654876504-9wWzOva7",
                area=ImagemapArea(
                    x=0, y=0, width=521, height=463
                )
            ),
            MessageImagemapAction(
                #使用說明
                text="@help",
                area=ImagemapArea(
                    x=525, y=464, width=515, height=459
                )
            ),
            URIImagemapAction(
                #查帳結算
                link_uri="https://liff.line.me/1654876504-rK3v07Pk",
                area=ImagemapArea(
                    x=522, y=0, width=518, height=463
                )
            )
        ]
                       
                            )
    line_bot_api.reply_message(event.reply_token,message)


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text
    history_list = get_history_list()
    if history_list[0]['type'] == 'user':      #個人部分
        selfId = history_list[0]['user_id']
        if (history_list[0]['Status'] == 'save') and ('記帳' in input_text):
            output_text='記帳成功'
        elif input_text == '@官網':
            output_text = 'https://reurl.cc/4yjNyY'
        elif input_text =='@help':
            output_text='請直接把多多分帳邀請至群組以解鎖分帳功能唷~'

        elif '多多公布欄' in input_text:
            output_text='多多感謝您的體諒！我會在群組中繼續為大家服務。'
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

    elif history_list[0]['type'] == 'room':  #聊天室部分
        Carousel_template = TemplateSendMessage(
                            alt_text='請把我加入群組',
                            template=ImageCarouselTemplate(
                            columns=[
            ImageCarouselColumn(
                image_url="https://i.imgur.com/wUob12p.jpg",
                action=URITemplateAction(
                    uri="https://i.imgur.com/wUob12p.jpg"
                )
            ),
            ImageCarouselColumn(
                image_url="https://i.imgur.com/MRMWivy.jpg",
                action=URITemplateAction(
                    uri="https://i.imgur.com/MRMWivy.jpg"
                )
            )
        ]     
                        )
                    )
        line_bot_api.reply_message(event.reply_token,Carousel_template)    

    else:  #群組部分
        selfGroupId = history_list[0]['group_id']
        if (history_list[0]['Status'] == 'set') and ('@分帳設定' in input_text):
            groupNumber=get_groupPeople(history_list,1)
            output_text='分帳設定成功:共有'+str(groupNumber)+'人分帳'

        elif (history_list[0]['Status'] == 'save') and ('@分帳' in input_text):
            output_text='分帳記錄成功'

        elif (history_list[0]['Status'] == 'None') and ('@分帳' in input_text):
            output_text='分帳記錄失敗'

        elif input_text == '@設定查詢':
            groupMember=get_groupPeople(history_list,2)
            output_text="分帳名單："
            for i in range(get_groupPeople(history_list,1)):
                output_text+='\n'+groupMember[i]

        elif '@美金設定' in input_text:
            NowRate=get_TodayRate(1)
            output_text="今日匯率："+str(NowRate)

        elif '@日圓設定' in input_text:
            NowRate=get_TodayRate(2)
            output_text="今日匯率："+str(NowRate)
        
        elif '@歐元設定' in input_text:
            NowRate=get_TodayRate(3)
            output_text="今日匯率："+str(NowRate)

        elif input_text == '@刪除':
            for i in range(3):
                data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='save').delete(synchronize_session='fetch')
            output_text='刪除成功'
            db.session.commit()

        elif input_text == '@設定刪除':
            data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='set').delete(synchronize_session='fetch')
            db.session.commit()
            output_text='刪除成功'
        
        elif '@clear' in input_text:  #刪除單個分帳者
            data_UserData = usermessage.query.filter(usermessage.status=='set').filter(usermessage.group_id==selfGroupId)
            del_spiltperson = ' '+input_text.replace('@clear','').strip(' ') +' '
            for _data in data_UserData:
                old_nickname = ' '+_data.nickname+' '
                old_nickname = old_nickname
                if old_nickname.count(del_spiltperson):
                    new_nickname = old_nickname.replace(del_spiltperson,' ').replace('  ',' ').strip(' ')
                    add_data = usermessage( 
                    id = _data.id, 
                    group_num = '0', 
                    nickname = new_nickname,
                    group_id = _data.group_id, 
                    type = _data.type, 
                    status = 'set', 
                    account = '0', 
                    user_id = _data.user_id, 
                    message = _data.message, 
                    birth_date = _data.birth_date
                    )
                    personID = _data.id
                    data_UserData = usermessage.query.filter(usermessage.id==personID).delete(synchronize_session='fetch')
                    db.session.add(add_data)
                    db.session.commit()
                    output_text="刪除成功，若被刪除的人在帳目中，請記得把帳目也修改掉!\n\n分帳名單:"
            try:
                if output_text=='刪除成功，若被刪除的人在帳目中，請記得把帳目也修改掉!\n\n分帳名單:':
                    groupMember=get_groupPeople(history_list,2)
                    for i in range(get_groupPeople(history_list,1)):
                        output_text+='\n'+groupMember[i]
            except: 
                output_text = '刪除失敗'

        
        elif '@delete' in input_text: #刪除單筆分帳
            count = usermessage.query.filter(usermessage.status=='save').filter(usermessage.group_id==selfGroupId).count()
            try:
                del_number = int (input_text.strip('@delete '))
                if del_number <= count :
                    data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.status=='save').filter(usermessage.group_id==selfGroupId)[del_number-1:del_number]
                    for _data in data_UserData:
                        personID = _data.id
                    data_UserData = usermessage.query.filter(usermessage.id==personID).delete(synchronize_session='fetch')
                    output_text='刪除成功'+'\n\n'+'記帳清單：'+'\n'+get_settleList(selfGroupId)
                    db.session.commit()
                else:
                    output_text='刪除失敗'
            except:
                output_text='刪除失敗'

        

        elif input_text == '@查帳':
            output_text = get_settleList(selfGroupId)
            flexmsg ={
  "type": "flex",
  "altText": "Flex Message",
  "contents": {
    "type": "bubble",
    "hero": {
      "type": "image",
      "url": "https://imgur.com/KahFQi9.jpg",
      "size": "full",
      "aspectRatio": "20:13",
      "aspectMode": "cover",
      "action": {
        "type": "text",
        "text":"查查"
      }
    },
    "body": {
      "type": "box",
      "layout": "vertical",
      "contents": [
        {
          "type": "text",
          "text": "查帳",
          "size": "xl",
          "weight": "bold"
        },
        {
          "type": "box",
          "layout": "vertical",
          "spacing": "sm",
          "margin": "lg",
          "contents": [
            {
              "type": "box",
              "layout": "baseline",
              "spacing": "sm",
              "contents": [
                {
                  "type": "text",
                  "text": output_text+". . .",
                  "flex": 5,
                  "size": "sm",
                  "color": "#666666",
                  "wrap": True
                }
              ]
            },
          ]
        }
      ]
    },
    "footer": {
      "type": "box",
      "layout": "vertical",
      "flex": 0,
      "spacing": "sm",
      "contents": [
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": "查看更多",
            "uri": "https://liff.line.me/1654876504-rK3v07Pk"
          },
          "height": "sm",
          "style": "link"
        },
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": "記錄分帳",
            "uri": "https://liff.line.me/1654876504-9wWzOva7"
          },
          "height": "sm",
          "style": "link"
        },
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": "編輯分帳者",
            "uri": "https://liff.line.me/1654876504-QNXjnrl2"
          },
          "height": "sm",
          "style": "link"
        },
        {
          "type": "spacer",
          "size": "sm"
        }
      ]
    }
  }
}
            line_bot_api.reply_message(event.reply_token,messages=FlexSendMessage.new_from_json_dict(flexmsg))

        elif input_text =='@結算':            
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
            for i in range(dataNumber):   #分帳金額
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
                        exchange_rate_EUR = get_exchangeRate(3)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1

                payAmount = exchange_rate*int(b['Account']) / len(GroupPeopleString)
                a1=set(person_list)      #分帳設定有的人
                a2=set(GroupPeopleString)
                duplicate = list(a1.intersection(a2))       #a1和a2重複的人名
                for j in range(len(duplicate)):      #分帳金額
                    place=person_list.index(duplicate[j])
                    payAmount_place = GroupPeopleString.index(duplicate[j]) +1  #多種分帳金額 - 金額位置 
                    if ( payAmount_place < len(GroupPeopleString) and GroupPeopleString[payAmount_place].isdigit() ): 
                        payAmount = exchange_rate*int(GroupPeopleString[payAmount_place])                   
                    account[place] -= payAmount
                    
            for j in range(dataNumber):  #代墊金額
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
                        exchange_rate_EUR = get_exchangeRate(3)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1

                for i in range(person_num):  
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

                #找到目前代墊最多的人
                if i==0:
                    maxPerson=max_tuple[0]
                    minPerson=min_tuple[0]

                
                min=float(min_tuple[1])
                max=float(max_tuple[1])

                #交換，印出該付的錢
                if min==0 or max==0:
                    pass
                elif (min+max)>0:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+" "+str(abs(round(min,2)))+'元'+'\n'
                    max_tuple=(max_tuple[0],min+max)
                    min_tuple=(min_tuple[0],0)
                elif (min+max)<0:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+" "+str(abs(round(max,2)))+'元'+'\n'
                    min_tuple=(min_tuple[0],min+max)
                    max_tuple=(max_tuple[0],0)
                else:
                    result=result+str(min_tuple[0])+'付給'+str(max_tuple[0])+" "+str(abs(round(max,2)))+'元'+'\n'
                    min_tuple=(min_tuple[0],0)
                    max_tuple=(max_tuple[0],0)
                
                person_account[0]=min_tuple
                person_account[-1]=max_tuple
            # result=result+'\n'+'下次不要再讓'+str(max_tuple[0])+'付錢啦! TA幫你們付很多了!'

            output_text = result.strip('\n')
            
            flexmsg ={
                    "type": "flex",
                    "altText": "Flex Message",
                    "contents": {
                        "type": "bubble",
                        "hero": {
                        "type": "image",
                        "url": "https://imgur.com/GteXIvk.jpg",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "action": {
                            "type": "text",
                            "text":"借錢要還，誰還要借?"
                        }
                        },
                        "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                            "type": "text",
                            "text": "簡化版本",
                            "size": "xl",
                            "weight": "bold"
                            },
                            {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                    "type": "text",
                                    "text": result+". . .",
                                    "flex": 5,
                                    "size": "sm",
                                    "color": "#666666",
                                    "wrap": True
                                    }
                                ]
                                },
                            ]
                            }
                        ]
                        },
                        "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 0,
                        "spacing": "sm",
                        "contents": [
                            {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "查看更多",
                                "uri": "https://liff.line.me/1654876504-rK3v07Pk"
                            },
                            "height": "sm",
                            "style": "link"
                            },
                            {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "記錄分帳",
                                "uri": "https://liff.line.me/1654876504-9wWzOva7"
                            },
                            "height": "sm",
                            "style": "link"
                            },
                            {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "編輯分帳者",
                                "uri": "https://liff.line.me/1654876504-QNXjnrl2"
                            },
                            "height": "sm",
                            "style": "link"
                            },
                            {
                            "type": "spacer",
                            "size": "sm"
                            }
                        ]
                        }
                    }
                    }
            line_bot_api.reply_message(event.reply_token,messages=FlexSendMessage.new_from_json_dict(flexmsg))

        elif input_text =='@稍微':             
            selfGroupId = history_list[0]['group_id'] 
            dataSettle_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId ).filter(usermessage.status=='save').filter(usermessage.type=='group') 
            historySettle_list = [] 
            person_list  = get_groupPeople(history_list,2)  #分帳設定人名
            person_num = get_groupPeople(history_list,1)  #分帳設定人數
            for _data in dataSettle_UserData: 
                historySettle_dic = {} 
                historySettle_dic['Account'] = _data.account 
                historySettle_dic['GroupPeople'] =_data.group_num 
                historySettle_dic['message'] = _data.message
                historySettle_list.append(historySettle_dic) 
                
            dataNumber=len(historySettle_list) 
            account= np.zeros((person_num,person_num)) 
            exchange_rate_USD = 0
            exchange_rate_JPY = 0
            exchange_rate_EUR = 0
            for i in range(dataNumber): 
                b=dict(historySettle_list[i]) 
                GroupPeopleString=b['GroupPeople'].split(' ')

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
                        exchange_rate_EUR = get_exchangeRate(3)
                        exchange_rate = exchange_rate_EUR
                else:
                    exchange_rate = 1
                payAmount = exchange_rate*int(b['Account']) / (len(GroupPeopleString)-1)  #不包含代墊者
                a1=set(person_list)      #分帳設定有的人 
                a2=set(GroupPeopleString) 
                duplicate = list(a1.intersection(a2))         #a1和a2重複的人名 

                for j in range(len(duplicate)):      #誰付誰錢矩陣 2給1 
                    place1=person_list.index(GroupPeopleString[0]) 
                    place2=person_list.index(duplicate[j]) 
                    account[place1][place2]+=payAmount 
            result=""
            for j in range ( person_num ): #誰付誰錢輸出 
                for i in range ( person_num ): 
                   payAmount = account[i][j] - account[j][i]
                   if ( payAmount>0 ): 
                        result += person_list[j]+'付給'+person_list[i] +" "+ str(round(payAmount,2)) +'元'+'\n' 
            output_text = result.strip('\n')
     
        elif input_text == '@清空資料庫':
            data_UserData = usermessage.query.filter(usermessage.status=='None').delete(synchronize_session='fetch')
            db.session.commit()
            output_text = '爽啦沒資料囉\n快給我重新設定匯率'
        
        elif '@查查廖擊敗'  in input_text:
            output_text = "欠錢不還啦 幹你娘"

        elif input_text =='@多多':
            try:
                message =TextSendMessage(
                    text="快速選擇下列功能：",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="主選單",text="@選單")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="查帳",text="@查帳")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="簡化結算",text="@結算")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="不簡化結算",text="@稍微")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="使用說明",text="@help")
                            ),
                        ]

                    )
                    )
                line_bot_api.reply_message(event.reply_token,message)
            except:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage ('發生錯誤!'))

        elif input_text =='@help' :
            Carousel_template = TemplateSendMessage(
                            alt_text='使用說明',
                            template=ImageCarouselTemplate(
                            columns=[
                ImageCarouselColumn(
                    image_url="https://imgur.com/xvZq2mD.png",
                    action=URITemplateAction(
                        uri="https://imgur.com/xvZq2mD.png"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://imgur.com/oER72MY.png",
                    action=URITemplateAction(
                        uri="https://imgur.com/oER72MY.png"
                    )
                )
            ]     
                            )
                        )
            line_bot_api.reply_message(event.reply_token,Carousel_template)


            line_bot_api.reply_message(event.reply_token,flexmsg)
        elif input_text =='@選單'  :
            message = ImagemapSendMessage(
                            base_url="https://imgur.com/cODeL32.jpg",
                            alt_text='功能總覽',
                            base_size=BaseSize(height=927, width=1040),
                            actions=[
            URIImagemapAction(
                #分帳者設定
                link_uri="https://liff.line.me/1654876504-QNXjnrl2",
                area=ImagemapArea(
                    x=0, y=464, width=522, height=459
                )
            ),
            URIImagemapAction(
                #記錄分帳
                link_uri="https://liff.line.me/1654876504-9wWzOva7",
                area=ImagemapArea(
                    x=0, y=0, width=521, height=463
                )
            ),
            MessageImagemapAction(
                #使用說明
                text="@help",
                area=ImagemapArea(
                    x=525, y=464, width=515, height=459
                )
            ),
            URIImagemapAction(
                #查帳結算
                link_uri="https://liff.line.me/1654876504-rK3v07Pk",
                area=ImagemapArea(
                    x=522, y=0, width=518, height=463
                )
            )
        ]
                       
                            )
            line_bot_api.reply_message(event.reply_token,message)
        
        
        elif input_text== '@官網':
            output_text = 'https://reurl.cc/4yjNyY'

        elif input_text=='@桌遊':
            output_text = str(get_Boardgame())

        elif input_text=='@電影':
            output_text = str(get_movie())

        elif input_text == '啾啾啾':
            output_text = '啾啾啾'

        elif input_text == '逛夜市' or input_text == '烤小鳥' or input_text == '@吳柏震 ' or input_text == '@林瑋晟 ' or input_text == '@王奕凱 ' or input_text == '@高子承 ' or input_text == '@廖奕翔 ':
            output_text = '不要吃焦阿巴'

        elif input_text == '@廖擊敗':
            output_text = '廖奕翔還錢 操!!'

        elif input_text == 'debug好累':
            output_text = '關我屁事，我已經好幾天沒睡了=='

        elif input_text ==  '乖狗狗':
            line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id=1, sticker_id=2))

        line_bot_api.reply_message(event.reply_token, TextSendMessage (output_text) )
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
#if __name__ == "__main__":
#    app.run()
