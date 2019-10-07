import requests
import re

html = requests.get("https://book.douban.com").text

print(html)