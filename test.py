__author__ = 'verbalist'
import unittest
import vtiger
import time

class VtigerTest(unittest.TestCase):

    def setUp(self):
        self.v = vtiger.Vtiger('login', 'url', 'access_key')
        self.v.login()
        self.assertIsNotNone(self.v.token)

    def test_list(self):
        r = self.v.list()
        self.assertTrue(r['success'], msg=r)

    def test_describe(self):
        r = self.v.describe('Users')
        print(r)
        self.assertTrue(r['success'], msg=r)

    @unittest.skip
    def test_expire(self):
        self.v._get_token()
        time.sleep(301)
        r = self.v.list()
        self.assertTrue(r['success'])

    def test_query(self):
        r = self.v.query('select * from Leads')
        self.assertTrue(r['success'], msg=r)

    @unittest.skip
    def test_create(self):
        # cf_1022 code name for license
        self.v.create({'firstname': 'monty', 'lastname': 'python', 'emailoptout': 'aaa@bbb.com'}, 'Contacts')


if __name__ == '__main__':
    unittest.main()
