from apscheduler.schedulers.blocking import BlockingScheduler
from urllib.request import urlopen

# 宣告一個排程
sched = BlockingScheduler()

# 定義排程 : 在周一至周五，每 20 分鐘就做一次 def scheduled_jog()
@sched.scheduled_job('cron', day_of_week='mon-sun', minute='*/20')
def scheduled_job():
    url = "https://accountsheet.herokuapp.com/"
    connect = urlopen(url)
    for key, value in connect.getheaders():
        print(key, value)
    
sched.start()  # 啟動排程

