# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import requests

# def cms(url):
#     headers ={
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     post = {
#         'hash':'0eca8914342fc63f5a2ef5246b7a3b14_7289fd8cf7f420f594ac165e475f1479',
#         'url': url
#     }
#     req = requests.post(url='http://whatweb.bugscaner.com/what/', data=post, headers=headers).text
#     print(req)
#
#
# cms('https://www.zut.edu.cn/')
import os
print(os.getcwd())
print(os.path.join(os.getcwd(), 'fingerprint', 'cms-fingerprint'))
print(os.path.join('\\fingerprint'))