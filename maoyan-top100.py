import json
import requests as req
from requests.exceptions import RequestException
import re
from multiprocessing import Pool

'''
Q：爬取猫眼top100榜单
'''

# 获取榜单首页html
def get_page(url):
    try:
        res = req.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/77.0.3865.75 Safari/537.36 '
        })
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        return None


# 解析page
def parse_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>'
                         '.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>'
                         '.*?fraction">(.*?)</i>.*?</dd>', re.S)  # re.S 匹配任意字符
    items = re.findall(pattern,html)
    for item in items:
        yield {
            'index': item[0],
            'cover': item[1],
            'title': item[2],
            'star': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }

# 保存数据到本地文件
def save(data):
    with open('maoyan-top.txt', 'a') as f:
        f.write(json.dumps(data) + '\n')
        f.close()

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    for item in parse_page(get_page(url)):
        save(item)


if __name__ == '__main__':
    # for i in range(10):
        # main(i*10)

    # 使用多线程
    pool = Pool()
    pool.map(main, [i*10 for i in range(10)])