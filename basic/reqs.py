import requests as req
#
# res = req.get('http://httpbin.org/get')
# # res = req.post('http://httpbin.org/post')
# print(type(res))
# print(res.json())

# 读取二进制文件
res = req.get("http://github.com/favicon.ico")
with open('favicon2.ico', 'wb') as f:
    f.write(res.content)
    f.close()

