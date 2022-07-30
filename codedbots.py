# -*- coding: utf-8 -*-
import base64
import json
import os
import sys
import time

import requests


class codedbots(object):
    def __init__(self):
        self.s = requests.Session()
        # self.s.proxies.update({'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080', })
        self.license = os.getenv('BOT_TOKEN')
        if len(self.license) != 64:
            print('license invalid')
            exit(1)
        self.mainurl = base64.b64decode('aHR0cHM6Ly9kaXNnYWVhLmNvZGVkYm90cy5jb20=').decode()
        self.key = None

    def rndid(self):
        if sys.version_info >= (3, 0):
            return os.urandom(16).hex()
        return os.urandom(16).encode('hex')

    def randomiv(self):
        return self.s.get(self.mainurl + '/iv', verify=False).content

    def encrypt(self, data, iv):
        body = {'data': base64.b64encode(json.dumps(data).encode()), 'iv': iv, 'license': self.license,
                'fuji_key': self.key}
        r = self.s.post(self.mainurl + '/encrypt', data=body, verify=False)
        if r.status_code == 200:
            return base64.b64decode(r.content)
        else:
            print('[%s] license key invalid or blocked [%s]' % (r.status_code, self.license))
            time.sleep(60)
            return None

    def decrypt(self, data, iv):
        body = {'data': data, 'iv': iv, 'fuji_key': self.key, 'license': self.license}
        r = self.s.post(self.mainurl + '/decrypt', data=body, verify=False)
        if r.status_code == 200:
            return json.loads(base64.b64decode(r.content))
        else:
            print('[%s] license key invalid or blocked [%s]' % (r.status_code, self.license))
            # time.sleep(60)
            return None
