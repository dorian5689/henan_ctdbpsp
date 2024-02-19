# _*_ coding: utf-8 _*_

import base64
import json
import subprocess
import time
from functools import partial

import requests
import schedule
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")

'''
CREATE TABLE ctbpsp (
  title VARCHAR(255),
  province VARCHAR(255),
  bulletin_type VARCHAR(255),
  accept_time DATE,
  detail_url VARCHAR(255)
);
'''


def get_decrypt_data(encrypt_data):
    try:
        des = DES.new(key="1qaz@wsx".encode('utf-8'), mode=DES.MODE_ECB)

        r = des.decrypt(base64.b64decode(encrypt_data))
        r = unpad(r, 8).decode('utf-8')
        resp = json.loads(r)
        return resp
    except:
        return 1


def get_results(page):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'http://ctbpsp.com',
        'Referer': 'http://ctbpsp.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    response = requests.get(
        f'https://custominfo.cebpubservice.com/cutominfoapi/recommand/type/5/pagesize/10/currentpage/{page}',
        headers=headers)
    time.sleep(2)
    # print(f'https://custominfo.cebpubservice.com/cutominfoapi/recommand/type/5/pagesize/10/currentpage/{page}')
    return response.text


def run_ctp(encrypt_data):
    from datetime import datetime

    today_time = datetime.now().strftime("%Y-%m-%d")
    decrypt_data = get_decrypt_data(encrypt_data)
    try:
        if decrypt_data != 1:
            data_list = decrypt_data['data']['dataList']

            for data in data_list:
                title = data['noticeName']
                province = data['reginProvince']
                bulletin_type = data['bulletinTypeName']
                accept_time = data['noticeSendTime']
                uuid = data['bulletinID']
                detail_url = f'http://ctbpsp.com/#/bulletinDetail?uuid={uuid}&inpvalue=&dataSource=0'
                print(title)
                # if contains_keywords(title):
                import pymysql

                # 建立数据库连接
                connection = pymysql.connect(
                    host='rm-2zej7q7186wi4eds5no.mysql.rds.aliyuncs.com',
                    user='xuzhiyong',
                    password='xzy@1234',
                    database='nanfangyunying'
                )

                # 创建游标对象
                cursor = connection.cursor()
                import datetime
                yestody_hms = (datetime.datetime.now() - datetime.timedelta(days=+1)).strftime('%Y-%m-%d')

                tomorrow_hms = (datetime.datetime.now() - datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
                if yestody_hms < accept_time < tomorrow_hms:
                    # 编写 SQL 插入语句，并使用 execute() 方法执行插入操作
                    sql = "INSERT INTO data_oms_ctbpsp (title, province, today_time,bulletin_type,accept_time,detail_url) VALUES (%s, %s, %s, %s, %s, %s)"
                    val = (title, province, today_time, bulletin_type, accept_time, detail_url)
                    try:
                        cursor.execute(sql, val)
                        # 提交更改
                        connection.commit()

                        # 关闭游标和数据库连接
                        cursor.close()
                        connection.close()

                        print(f'{now_time()}'-----
                            f'标题: {title}\n公告类型: {bulletin_type}\n省份: {province}\n接收时间: {accept_time}\n详情url地址: {detail_url}')
                    except:

                        # 如果小于则停止并关闭游标和数据库连接
                        cursor.close()
                        connection.close()

    except:
        pass

def now_time():
    from datetime import datetime

    # 获取当前时间
    current_time = datetime.now()

    # 格式化为字符串，包含年-月-日 时:分:秒
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time
def parse():
    print(F'开始运行！')

    # 获取当前的年月日
    for page in range(1, 1001):
        encrypt_data = get_results(page)


        print(F'{now_time()}---第{page - 1}页')

        try:
            run_ctp(encrypt_data)


        except:
            print(encrypt_data, '这里出错了! 重新运行！')
            time.sleep(5)
            run_ctp(encrypt_data)

            # if contains_keywords(title):
            #     print(
            #         f'标题: {title}\n公告类型: {bulletin_type}\n省份: {province}\n接收时间: {accept_time}\n详情url地址: {detail_url}')
            # else:
            #     print(f'0000')


def contains_keywords(title):
    keywords_1 = ["风电", "风机", "光伏", "新能源"]
    keywords_2 = ["运行", "维护", "运维", "委托", "外委"]
    if any(keyword in title for keyword in keywords_1) and any(keyword in title for keyword in keywords_2):
        return True
    return False


# parse()

if __name__ == '__main__':

    parse()
    # schedule.every(50).hours.do(parse)
    # schedule.every(50).minutes.do(parse)
    #
    # schedule.every().day.at("01:50").do(parse)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
