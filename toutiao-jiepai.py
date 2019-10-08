import json
import os
import re
import time
from urllib.parse import urlencode
from hashlib import md5
import pymongo
from bs4 import BeautifulSoup
import requests as req
from requests.exceptions import RequestException
from config import *
from multiprocessing import Pool

client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db = client.get_database(MONGO_DB_TOUTIAO)
collection = db.get_collection(MONGO_COLLECTION_TOUTIAO)


def get_index_page(offset, keyword):
    url = 'https://www.toutiao.com/api/search/content/?'
    params = {
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': int(round(time.time() * 1000))  # 时间戳
    }
    try:
        res = req.get(url + urlencode(params), headers={
            'cookie': 'tt_webid=6739390018118829575; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6739390018118829575; csrftoken=525869434cc1ee5dd467b9469cecedba; sso_uid_tt=d7e843b68f9f4c221806525ecc5c5195; toutiao_sso_user=b9fea94c7cd64721e804514e666fa93f; login_flag=4e60996667b43de6bbab7b99ecd70cbb; sessionid=d6b5831bf5f0132cd893dc95d89beee8; uid_tt=f312342cf2fa31bb358a51570d832137; sid_tt=d6b5831bf5f0132cd893dc95d89beee8; sid_guard="d6b5831bf5f0132cd893dc95d89beee8|1569137078|15552000|Fri\054 20-Mar-2020 07:24:38 GMT"; cp=5D87671D824ACE1; __tasessionId=9t2qyhzrt1570460453217; s_v_web_id=7e0d5a1bcb21083a2ad29c82f5d034e9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D%E7%BE%8E%E5%9B%BE'
        })
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        print('请求错误, url=%s' % url)
        return None


# parse json , get article_url
def parse_index_page(content):
    data = json.loads(content)
    if data and 'data' in data.keys():
        if data.get('data'):
            for item in data.get('data'):
                if 'article_url' in item and 'single_mode' not in item:
                    yield item.get('article_url')


def get_detail(url):
    try:
        res = req.get(url, headers={
            'cookie': 'tt_webid=6739390018118829575; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6739390018118829575; csrftoken=525869434cc1ee5dd467b9469cecedba; sso_uid_tt=d7e843b68f9f4c221806525ecc5c5195; toutiao_sso_user=b9fea94c7cd64721e804514e666fa93f; login_flag=4e60996667b43de6bbab7b99ecd70cbb; sessionid=d6b5831bf5f0132cd893dc95d89beee8; uid_tt=f312342cf2fa31bb358a51570d832137; sid_tt=d6b5831bf5f0132cd893dc95d89beee8; sid_guard="d6b5831bf5f0132cd893dc95d89beee8|1569137078|15552000|Fri\054 20-Mar-2020 07:24:38 GMT"; cp=5D87671D824ACE1; __tasessionId=9t2qyhzrt1570460453217; s_v_web_id=7e0d5a1bcb21083a2ad29c82f5d034e9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        })
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        print('请求详情页面失败,url = ' % url)  # 格式化输出 %s
        return None


def parse_detail(html, url):
    # use bs4 get title info
    bs = BeautifulSoup(html, 'lxml')
    title = bs.select('title')[0].get_text()
    # pattern = re.compile('.*?gallery: JSON.parse\("(.*?)\"\)',re.S) #正则化错误，没有找到真正的json对象（字符串）
    pattern = re.compile('gallery: JSON.parse\((.*?)\),', re.S)  # 正则化正解，找到json标准对象，需要双引号
    result = re.search(pattern, html)
    if result:
        data = eval(re.sub(r'\\', '', json.loads(result.group(1))))  # use eval将字符串形式转成字典形式
        if data and 'sub_images' in data.keys():
            subs = data.get("sub_images")
            images = [item.get('url') for item in subs]
            for url in images: save_image_2_local(url, title)

            yield {
                'title': title,
                'url': url,
                'images': images
            }


def save_2_mongo(data):
    if collection.insert(data):
        print('save 2 mongo success.')
        return True
    return False


def save_image_2_local(url, title):
    image_path = '{0}/{1}/{2}/'.format(os.getcwd(), 'images', title)
    try:
        res = req.get(url)
        if res.status_code == 200:  #

            if (not os.path.exists(image_path)): os.makedirs(image_path)  # 创建多级目录
            file_path = '{0}/{1}.{2}'.format(image_path, md5(res.content).hexdigest(), 'jpg')

            # 开始将图片二进制内容保存到本地
            if (not os.path.exists(file_path)):
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                    f.close()
    except RequestException:
        print('访问图片错误，url=%s' % url)
    except FileNotFoundError as e:
        print('文件[%s]不存在,' % e.filename)


def main(offset):
    for article_url in parse_index_page(get_index_page(offset, KEYWORD)):
        html = get_detail(article_url)
        for item in parse_detail(html, article_url):
            save_2_mongo(item)


if __name__ == '__main__':
    # Pool().map(main, [x*20 for x in range(GROUP_START, 1)])
    # main(20)
    Pool().map(main, [x*20 for x in range(GROUP_START, GROUP_END + 1)])
