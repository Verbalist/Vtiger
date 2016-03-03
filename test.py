__author__ = 'verbalist'
import unittest
import vtiger
import time

class VtigerTest(unittest.TestCase):

    def setUp(self):
        self.v = vtiger.Vtiger('andreyfrost@gmail.com', 'https://gm64.od2.vtiger.com', '0KfHCXp6gynViFDi')
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
        r = self.v.query('select * from Leads limit 2')
        self.assertTrue(r['success'], msg=r)

    @unittest.skip
    def test_create(self):
        # cf_1022 code name for license
        self.v.create({'firstname': 'monty', 'lastname': 'python', 'emailoptout': 'aaa@bbb.com', 'cf_1022': 'Trial',
                       'cf_1177': 'Denis Petrov', 'leadsource': 'Test'}, 'Contacts')
        q = self.v.query('select firstname, id from Contacts where firstname=%s' % 'monty')
        self.assertEqual(q['firstname'], 'monty', msg=q)


    @unittest.skip
    def test_update(self):
        q = self.v.query('select firstname, lastname, leadsource, leadstatus, assigned_user_id, cf_1155, cf_1159, assigned_user_id from Leads where id=2x4727')
        self.v.update({'id': '2x4727', 'phone': '123', 'cf_1159': 'Denis Petrov', 'cf_1155': 'English',
                       'leadstatus': q['leadstatus'], 'leadsource': q['leadsource'], 'lastname': q['lastname'],
                       'assigned_user_id': q['assigned_user_id'], 'firstname': q['firstname']})
        q = self.v.query('select phone from Leads where id=2x4727')
        self.assertEqual(q['phone'], '123')

    @unittest.skip
    def test_delete(self):
        self.v.create({'firstname': 'monty', 'lastname': 'python', 'emailoptout': 'aaa@bbb.com', 'cf_1022': 'Trial',
                       'cf_1177': 'Denis Petrov', 'leadsource': 'Test'}, 'Contacts')
        q = self.v.query("select firstname from Contacts where firstname='%s'" % 'monty')
        self.v.delete(q['id'])
        q = self.v.query("select firstname from Contacts where firstname='%s'" % 'monty')
        self.assertEqual(q, [])

if __name__ == '__main__':
    unittest.main()
