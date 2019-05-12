# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import requests
import re
# header = {
#     'Cookie':'yunsuo_session_verify=4cce7f3474ca34409f62018de4e107ea',
#     'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
# }
req = requests.get('http://bwc.hait.edu.cn/').text
body =  re.search(r"<body[^>]*>(.*?)</body>", req,re.S|re.M) or re.search(r"<BODY[^>]*>(.*?)</BODY>", req, re.S|re.M)
print(body)
if body:
    body = body.group(1).strip()

print(body)
