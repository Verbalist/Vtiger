import random

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

    def update(self, data, assigned_user_id=None):
        try:
            # if data.get('assigned_user_id') is None:
            #     data['assigned_user_id'] = assigned_user_id if assigned_user_id is not None else self.user_id
            r = self._post('/webservice.php', data={'operation': 'update',
                                                    'sessionName': self.session_name,
                                                    'element': json.dumps(data)})
            if r['success']:
                return r
            else:
                raise Exception(r['error'])
        except Exception as e:
            print(e)

    def delete(self, _id):
        try:
            r = self._post('/webservice.php', data={'operation': 'delete',
                                                    'sessionName': self.session_name,
                                                    'id': str(_id)})
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
                            d[x['name']] = x['label']
                    else:
                        print('label:', x['label'], 'inner_name:', x['name'], 'type:', x['type']['name'])
                        d[x['name']] = x['label']
                print(d)
            else:
                for x in r['result']['fields']:
                    if x['label'].lower() == label.lower():
                        print('label:', x['label'], 'inner_name:', x['name'], 'type:', x['type']['name'])
                        break
            return r['result']
        else:
            return r

    def query(self, q):
        """q must be in double quotes"""
        if not q.endswith(';'): q += ';'
        r = self._get('/webservice.php?operation=query&sessionName={0}&query={1}'.format(self.session_name, q))
        if r['success']:
            for x in r['result']:
                for k, v in x.items():
                    print(k, ':', v)
                # print(x)
            return r['result'][0] if len(r['result']) == 1 else r['result']
        else:
            return r


if __name__ == '__main__':
    # V = Vtiger('k.s.4invest@gmail.com', 'https://infoconsulting2.od2.vtiger.com', 'ez9k5qpJ6fBLOJM7')
    V = Vtiger('andreyfrost@gmail.com', 'https://gm64.od2.vtiger.com', '0KfHCXp6gynViFDi')
    V.login()
    # a = V.query("select id from paymetsdetail where firstname='%s' order by id desc limit 1" % 'Анна')

    a = V.describe('paymentsdetails', mandatory=False)
    print(a)
    # V.describe('Leads', mandatory=False)
    # refs = V.query("select id from Users where title = 'Sales Representative'")
    # ref = refs[random.randint(0, len(refs)-1)]['id']
asas