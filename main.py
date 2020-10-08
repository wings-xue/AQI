import requests

import logging
from datetime import datetime
import json
import time

logging.getLogger().setLevel(logging.INFO)


# 六个地区九个指标url
url = "https://api.waqi.info/api/feed/@5399/obs.en.json"
# 六个地区九个指标id
# 通过js加载获得，对应六个地区，如果改变，直接改变id， 如果有必要，也可以通过请求获取
uid = ["3668","5399","5400","5401","5402","5398"]
addr = {
    "3668": "十堰",
    "5399": "十堰滨河新村",
    "5400": "十堰刘家沟",
    "5401": "十堰铁二处",
    "5402": "十堰郧县城区空气自动站",
    "5398": "十堰武当山",
}


# 六个地区九个指标key，fetcher_six_nine_index函数中体现，如果改变直接修改函数


# 指标
index = ["SO2", "AQI", "PM2_5", "NO2", "CO", "O3"]

# 十堰市空气质量实时监测数据每小时
def per_hour_aqi_api()->str:
    for i in index:
        yield f"https://datacenter.mee.gov.cn/websjzx/dataproduct/airproduct/ajaxApi/querykqzlqs.vm?citycode=420100&daycons=1&kqzlwrw={i}&startdate=&enddate="



# 每小时十堰市的空气质量监测结果， 有时候需要验证码，更换这个cookie。 如果有必要可以通过程序过验证码,获取cookie
cookies = {
    'JSESSIONID': 'E1AC5D326E2BA683CAD5EFB1A0F5BDB1',
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}


def fetcher(url, header=None, method=None, data=None)->str:
    headers = header if header else {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
    if method == "POST" or method == "post":
        rst = requests.post(url, data=data, headers=headers)
    else:
        rst = requests.get(url, headers=headers)
    if rst.status_code != 200:
        raise Exception("spider refused by target web")
    return rst.text
    

def now()->str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:') + "00"


def save(name,content):
    with open(f"./data/{name}", "w") as f:
        f.write(content)
 

def fetcher_per_hour_index() -> str:
    for u in per_hour_aqi_api():
        logging.info(f"[fetcher_per_hour_index]--fetcher {u} index info")
        yield fetcher(u, header=headers)

def fetcher_nine_six_index() -> str:
    for i in uid:
        logging.info(f"[fetcher_nine_six_index]--fetcher {i} addr info")
        yield fetcher_nine_index(i)

def fetcher_nine_index(id: str)->str:
    if id not in uid:
        raise Exception("请检查网页是否有这个地址")
    # 获取当前时间戳的token
    # 对应的key均相同
    f_url = f"https://api.waqi.info/api/token/{id}"
    rst = fetcher(f_url)
    token = json.loads(rst).get("rxs", {}).get("obs", [])[0]["msg"]["token"]
    key = "_2Y2EvVB5mMxAcHTcISCJWXmpjaEE/LTdRFUYjZg=="

    # 获取当前token对应的观察数据
    data={
        "key": key,
        "token": token,
    }
    rst = fetcher(url, method="POST", data=data)
    msg = json.loads(rst).get("rxs", {}).get("obs", [])[0]["msg"]
    iaqi = msg.get("iaqi")
    return {
        addr[id]: iaqi
    }

def loop(i:int, f):
    while 1:
        logging.info("开始启动")
        f()
        logging.info(f"休眠{i}秒，请等待...")
        time.sleep(i)
       


def run():
    n = now()
    six_nine_indexs = []
    for rst in fetcher_nine_six_index():
        six_nine_indexs.append(json.dumps(rst))
    save(f"六个地区九个指标-{n}","\n\n".join(six_nine_indexs))

    
    per_hour_index = []
    for rst in fetcher_per_hour_index():
        per_hour_index.append(rst)
    save(f"指标每日变化-{n}","\n\n".join(per_hour_index))
     

def main():
    loop(60*40, run)


if __name__ == "__main__":
    main()