import re
from urllib.request import urlparse
from config import config
import requests
config = config['development']
def match_url(url):
    pattern = re.match(r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', url,
                       re.IGNORECASE)
    if pattern:
        return True
    else:
        return False

def match_ip(ip):
    pattern = re.match(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                       ip, re.IGNORECASE)
    if pattern:
        return True
    else:
        return False

def match_email(email):
    pattern = re.match(r'\w+@([0-9a-zA-Z]+[-0-9a-zA-Z]*)(\.[0-9a-zA-Z]+[-0-9a-zA-Z]*)+', email, re.IGNORECASE)
    if pattern:
        return True
    else:
        return False

def urlTodomain(url):
    parsed_url = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_url)
    if domain[0:4] == 'www.':
        domain = domain[4:]
    return domain

def urlTosite(url):
    parse_url = urlparse(url)
    site = '{uri.netloc}'.format(uri=parse_url)
    return site

def unabletouch(url):
    try:
        print(url)
        status = requests.get(url, headers=config.HRADER, timeout=10, verify=False).status_code
        if 200<=status<400:
            return True
        else:
            return False
    except:
        return False

if __name__ == '__main__':
    a = unabletouch('https://cn.wordpress.org/')
    print(a)