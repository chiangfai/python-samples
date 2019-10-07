import urllib.request as req
import urllib.error
import socket

try:
    res = req.urlopen("http://www.baidu.com", timeout=0.001)
    # print(res.read().decode('UTF-8'))
except urllib.error.URLError as e:
    if isinstance(e.reason, socket.timeout):
        print('TIME OUT.')


