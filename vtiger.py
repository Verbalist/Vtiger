__author__ = 'verbalist'

import requests
import time
import hashlib
import json
import os
os.environ['TZ'] = 'UTC'


class Vtiger():

    session_name = None
    token = None
    expire = int(time.time())


    def __init__(self, username, main_url, access_key):
        self.username = username
        self.main_url = main_url
        self.access_key = access_key


    def _get(self, url, data=None):
        r = requests.get(self.main_url + url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        return r.json()

    def _post(self, url, data=None):
        r = requests.post(self.main_url + url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        return r.json()

    def _get_token(self):
        r = self._get('/webservice.php?operation=getchallenge&username={username}'.format(username=self.username))
        if r['success']:
            self.expire = int(r['result']['expireTime']) + int(time.time() - int(r['result']['serverTime']))
            self.token = r['result']['token']
        else:
            raise Exception(r['error'])

    def _check_expire(self):
        if self.expire < time.time():
            self._get_token()

    def extend_session(self):
        self._get('/webservice.php?operation=extendsession')

    def login(self):
        try:
            self._check_expire()
            r = self._post('/webservice.php', data={'operation': 'login', 'username': self.username,
                'accessKey': hashlib.md5((self.token + self.access_key).encode()).hexdigest()})
            if r['success']:
                self.user_id = r['result']['userId']
                self.session_name = r['result']['sessionName']
            else:
                raise Exception(r['error'])
        except Exception as e:
            print(e)

    def logout(self):
        try:
            r = self._post('/webservice.php', data={'operation': 'logout', 'sessionName': self.session_name})
            if not r['success']:
                raise Exception(r['error'])
        except Exception as e:
            print(e)

    def create(self, data, module, assigned_user_id=None):
        try:
            if data.get('assigned_user_id') is None:
                data['assigned_user_id'] = assigned_user_id if assigned_user_id is not None else self.user_id
            r = self._post('/webservice.php', data={'operation': 'create',
                                                    'sessionName': self.session_name,
                                                    'element': json.dumps(data),
                                                    'elementType': module})
            if r['success']:
                return r
            else:
                raise Exception(r['error'])
        except Exception as e:
            print(e)

    def update(self, data, module, assigned_user_id=None):
        try:
            if data.get('assigned_user_id') is None:
                data['assigned_user_id'] = assigned_user_id if assigned_user_id is not None else self.user_id
            r = self._post('/webservice.php', data={'operation': 'update',
                                                    'sessionName': self.session_name,
                                                    'element': json.dumps(data),
                                                    'elementType': module})
            if r['success']:
                return r
            else:
                raise Exception(r['error'])
        except Exception as e:
            print(e)

    def list(self):
        r = self._get('/webservice.php?operation=listtypes&sessionName=%s' % self.session_name)
        return r

    def describe(self, module, label=None, mandatory=True):
        r = self._get('/webservice.php?operation=describe&sessionName={0}&elementType={1}'
                      .format(self.session_name, module))
        if r['success']:
            if label is None:
                d = {}
                for x in r['result']['fields']:
                    if mandatory:
                        if x['mandatory']:
                            print('label:', x['label'], 'inner_name:', x['name'], 'type:', x['type']['name'])
                            d[x['name']] = None
                    else:
                        print('label:', x['label'], 'inner_name:', x['name'], 'type:', x['type']['name'])
                        d[x['name']] = None
                print(d)
            else:
                for x in r['result']['fields']:
                    if x['label'].lower() == label.lower():
                        print('label:', x['label'], 'inner_name:', x['name'], 'type:', x['type']['name'])
                        break
        return r

    def query(self, q):
        if not q.endswith(';'): q += ';'
        r = self._get('/webservice.php?operation=query&sessionName={0}&query={1}'.format(self.session_name, q))
        if r['success']:
            for x in r['result']:
                print(x)
        return r


if __name__ == '__main__':
    v = Vtiger('login', 'url', 'access_key')
    v.login()
    v.describe('Leads', mandatory=False)
