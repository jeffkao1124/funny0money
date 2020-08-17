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
import requests
from bs4 import BeautifulSoup

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
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def get_exchangeRate():
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

   return data


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
        
    input_text = event.message.text
    if (eval(input_text)>0) and (eval(input_text)<=100000):
        output_text= input_text
    elif  input_text =="0":
        hot_movie=get_movie()
        output_text=hot_movie
    elif input_text =="-1":
        exchangeRate=get_exchangeRate()
        output_text=exchangeRate
    else:
        output_text="我是可愛的吉娃娃"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(str(output_text)))


    


if __name__ == "__main__":
    app.run()