# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import requests
import time
with open('中原工学院', 'r') as f:
    for i in f.readlines():
        url = i.strip()
        data = {'url':url, 'number':1,'cycle':1,'secret_key':'57194b72-eb58-4d96-8ec6-16fcb84aa5c3'}
        try:
            req = requests.post(url='http://127.0.0.1:5000/v1/task/',data=data).text
            print(url, req)
        except Exception as e:
            print(e)
        time.sleep(40)
