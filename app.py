from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
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
app = Flask(__name__)

line_bot_api = LineBotApi('bHi/8szU2mkZAaIMLGDKqTE8CnG4TjilHVVJsqDse2XD39ZUGdxiHRedvOGSC5Q7zJfFYZoOAIoMxeKAR5mQqbz0DomlYKjU7gMEK/zQ0QJFFVJLpDhwB8DRrJ8SAoqK+sEAMuD2PL0h0wdsZxncRwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2ee6a86bd730b810a7d614777f07cecb')

contents= {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "image",
        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip3.jpg",
        "size": "full",
        "aspectMode": "cover",
        "aspectRatio": "1:1",
        "gravity": "center"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "text",
                    "text": "Brown Grand Hotel",
                    "size": "xl",
                    "color": "#ffffff"
                  }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "contents": [
                  {
                    "type": "icon",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                  },
                  {
                    "type": "icon",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
                  },
                  {
                    "type": "text",
                    "text": "4.0",
                    "color": "#a9a9a9"
                  }
                ],
                "spacing": "xs"
              },
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                      {
                        "type": "text",
                        "text": "¥62,000",
                        "color": "#ffffff",
                        "size": "md",
                        "flex": 0,
                        "align": "end"
                      },
                      {
                        "type": "text",
                        "text": "¥82,000",
                        "color": "#a9a9a9",
                        "decoration": "line-through",
                        "size": "sm",
                        "align": "end"
                      }
                    ],
                    "flex": 0,
                    "spacing": "lg"
                  }
                ]
              }
            ],
            "spacing": "xs"
          }
        ],
        "position": "absolute",
        "offsetBottom": "0px",
        "offsetStart": "0px",
        "offsetEnd": "0px",
        "paddingAll": "20px"
      }
    ],
    "paddingAll": "0px"
  }
}

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
                userName = receivedmsg.strip(' 分帳設定 ').replace('  ',' ')
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
                            base_url="https://imgur.com/CRoZNQr.png",
                            alt_text='我要進來囉',
                            base_size=BaseSize(height=976, width=1240),
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


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text.lower()
    history_list = get_history_list()
    if history_list[0]['type'] == 'user':      #個人部分
        selfId = history_list[0]['user_id']
        if (history_list[0]['Status'] == 'save') and ('記帳' in input_text):
            output_text='記帳成功'
                
        elif input_text =='查帳':
            for i in range(10):
                output_text = get_accountList(selfId)
        
        elif input_text =='@help':
            Carousel_template = TemplateSendMessage(
                            alt_text='使用說明',
                            template=ImageCarouselTemplate(
                            columns=[
                ImageCarouselColumn(
                    image_url="https://imgur.com/6ZXZUPu.jpg",
                    action=URITemplateAction(
                        uri="https://imgur.com/6ZXZUPu.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://imgur.com/KS16CAT.jpg",
                    action=URITemplateAction(
                        uri="https://imgur.com/KS16CAT.jpg"
                    )
                )
            ]     
                            )
                        )
            line_bot_api.reply_message(event.reply_token,Carousel_template)
        elif input_text =='刪除':
            for i in range(3):
                data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='save').delete(synchronize_session='fetch')
            output_text='刪除成功'

        elif 'delete' in input_text:
            data_UserData = usermessage.query.filter(usermessage.user_id==selfId).filter(usermessage.status=='save').filter(usermessage.type=='user')
            count=0
            for _data in data_UserData:
                count+=1
            try:
                del_number = int (input_text.strip('delete '))  
                if del_number <= count :
                    data_UserData = usermessage.query.order_by(usermessage.birth_date).filter(usermessage.user_id==selfId).filter(usermessage.status=='save').filter(usermessage.type=='user')[del_number-1:del_number]
                    for _data in data_UserData:
                        personID = _data.id
                    data_UserData = usermessage.query.filter(usermessage.id==personID).delete(synchronize_session='fetch')
                    output_text='刪除成功'+'\n\n'+'記帳清單：'+'\n'+get_accountList(selfId)
                    db.session.commit()
                else:
                    output_text='刪除失敗'
            except:
                output_text='刪除失敗'

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

        else:
            output_text='記帳失敗，請再檢查記帳格式'+'\n'+'輸入：記帳 分類/項目 金額'+'\n'+'ex：記帳 吃/麻糬 200'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(output_text ))
        
    else:  #群組部分
        selfGroupId = history_list[0]['group_id']
        if (history_list[0]['Status'] == 'set') and ('分帳設定' in input_text):
            groupNumber=get_groupPeople(history_list,1)
            output_text='分帳設定成功:共有'+str(groupNumber)+'人分帳'

        elif (history_list[0]['Status'] == 'save') and ('分帳' in input_text):
            output_text='分帳紀錄成功'

        elif (history_list[0]['Status'] == 'None') and ('分帳' in input_text):
            output_text='分帳紀錄失敗'

        elif input_text == '設定查詢':
            groupMember=get_groupPeople(history_list,2)
            output_text="分帳名單："
            for i in range(get_groupPeople(history_list,1)):
                output_text+='\n'+groupMember[i]

        elif '美金設定' in input_text:
            NowRate=get_TodayRate(1)
            output_text="今日匯率："+str(NowRate)

        elif '日圓設定' in input_text:
            NowRate=get_TodayRate(2)
            output_text="今日匯率："+str(NowRate)
        
        elif '歐元設定' in input_text:
            NowRate=get_TodayRate(3)
            output_text="今日匯率："+str(NowRate)

        elif input_text == '刪除':
            for i in range(3):
                data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='save').delete(synchronize_session='fetch')
            output_text='刪除成功'
            db.session.commit()

        elif input_text == '設定刪除':
            data_UserData = usermessage.query.filter(usermessage.group_id==selfGroupId).filter(usermessage.status=='set').delete(synchronize_session='fetch')
            db.session.commit()
            output_text='刪除成功'
        
        elif 'clear' in input_text:  #刪除單個分帳者
            data_UserData = usermessage.query.filter(usermessage.status=='set').filter(usermessage.group_id==selfGroupId)
            del_spiltperson = ' '+input_text.replace('clear','').strip(' ') +' '
            for _data in data_UserData:
                old_nickname = ' '+_data.nickname+' '
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
                    output_text="刪除成功\n\n分帳名單:"
            try:
                if output_text=='刪除成功\n\n分帳名單:':
                    groupMember=get_groupPeople(history_list,2)
                    for i in range(get_groupPeople(history_list,1)):
                        output_text+='\n'+groupMember[i]
            except: 
                output_text = '刪除失敗'

        
        elif 'delete' in input_text: #刪除單筆分帳
            count = usermessage.query.filter(usermessage.status=='save').filter(usermessage.group_id==selfGroupId).count()
            try:
                del_number = int (input_text.strip('delete '))
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

        elif input_text == '查帳':
            output_text = get_settleList(selfGroupId)



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

            output_text = result.strip('\n')
            
            flexmsg = TemplateSendMessage(
                            alt_text='account',
                            template=ButtonsTemplate(
                            
            title="結算(簡化版本)",
            text=result,
            actions=[
                URITemplateAction(
                    label="詳細資訊",
                    uri="https://liff.line.me/1654876504-rK3v07Pk"
                )
            ]
        )
    )
            line_bot_api.reply_message(event.reply_token,flexmsg)

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
                        result += person_list[j]+'付給'+person_list[i] + str(round(payAmount,2)) +'元'+'\n' 
            output_text = result.strip('\n')
     
        elif input_text == '清空資料庫':
            data_UserData = usermessage.query.filter(usermessage.status=='None').delete(synchronize_session='fetch')
            db.session.commit()
            output_text = '爽啦沒資料囉\n快給我重新設定匯率'

        elif input_text =='帳獒':
            try:
                message =TextSendMessage(
                    text="快速選擇下列功能：",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="主選單",text="@選單")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="查帳",text="查帳")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="簡化結算",text="結算")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="不簡化結算",text="稍微")
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
                    image_url="https://imgur.com/8r5SMgQ.jpg",
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


            line_bot_api.reply_message(event.reply_token,flexmsg)
        elif input_text =='@選單'  :
            message = ImagemapSendMessage(
                            base_url="https://imgur.com/CRoZNQr.png",
                            alt_text='功能總覽',
                            base_size=BaseSize(height=976, width=1240),
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
        elif input_text == '哈哈':
            line_bot_api.reply_message(event.reply_token,FlexSendMessage(
                    alt_text = 'ccc',
                    contents = contents
                )
            )
        


if __name__ == "__main__":
    app.run()
