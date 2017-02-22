# coding=utf-8
# _author_ = jiangzhuang
# from app import scheduler
import time
#from apscheduler.schedulers.blocking import BlockingScheduler
#schedudler = BlockingScheduler(daemonic = False)

# 1 完成活动任务
# @scheduler.scheduled_job('cron',second='10,20,30,40,50,60', day_of_week='0-7', hour='11-12,13')
def activity_over():
    # 每天分两个时间段完结活动（结束时间<当前时间）
    now = int(time.time())
    print '11111111111111111111111'
    print 'activity_over test :',str(now)
    return

# 2 读取qq日志文件任务


# 3 统计任务


# 4 同步QQ群任务