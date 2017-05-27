#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sched
import time
from datetime import datetime, timedelta, timezone

import jpype

import crawler_today_data

# 初始化sched模块的scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)

logging.basicConfig(
        filename='schedule-crawler.log',
        level=logging.DEBUG,
        format='%(levelname)s:%(asctime)s:%(message)s'
    )


# 被周期性调度触发的函数
def func():
    # os.system("scrapy crawl News")
    print(' start scrapy')
    logging.debug(' start scrapy')

    crawler_today_data.crawler_today_date()

    # 调用上传数据的jar文件
    # jar_path = os.path.abspath(os.getcwd())
    # run_jar(jar_path)


def run_jar(jar_path):
    """
    运行jar文件
    :param jar_path: jar包位置
    :return: 
    """

    # 开启JVM，且指定jar包位置
    jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.ext.dirs=%s" % jar_path)

    # 引入java程序中的类.路径应该是项目中的package包路径.类名
    javaClass = jpype.JClass('HoroscopeDataUpload')

    # 创建一个对象
    javaInstance = javaClass()

    # 这一步就是具体执行类中的函数了
    javaInstance.uploadData()

    jpype.shutdownJVM()


def perform1(inc):
    schedule.enter(inc, 0, perform1, (inc,))
    func()    # 需要周期执行的函数


def my_main():
    delay = time_dis()

    time_str = time.strftime('%H:%M:%S', time.gmtime(delay))
    logging.info('预计%s后开始第一次任务' % time_str)
    print('预计%s后开始第一次任务' % time_str)
    sch_time = 60 * 60 * 24   # 单位：秒
    schedule.enter(delay, 0, perform1, (sch_time,))


def time_dis():
    """
    与第二天0点时间差 
    :return: 毫秒数 
    """
    _timezone = timezone(timedelta(hours=-7))
    _day = timedelta(days=1)
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    target_time = utc_dt.astimezone(_timezone)
    target_time = target_time.replace(hour=0, minute=0)
    target_time += _day

    now_time = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(_timezone)

    return target_time.timestamp() - now_time.timestamp()


if __name__ == "__main__":
    my_main()
    schedule.run()  # 开始运行，直到计划时间队列变成空为止


