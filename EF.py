__author__ = 'verbalist'

import psycopg2
import datetime
import decimal
import json

# with open('/var/www/config.txt', 'r') as config:
#     db_config = {row.split('=')[0]: row.split('=')[1].strip('\n') for row in config}
db_config = {'host': '192.168.200.234', 'user': 'gofraud', 'database': 'main', 'password': 'kXLILCrAPp2yjEgH3xCpd'}


class Entity(object):

    @staticmethod
    def to_str(v):
            if type(v) in (datetime.date, datetime.datetime, datetime.timedelta):
                return str(v)
            elif type(v) == decimal.Decimal:
                return float(v)
            else:
                return v

    def __init__(self, atrs):
        for k,v in atrs.items():
            setattr(self, k, v)

    def to_dict(self):
        d = self.__dict__
        return {k: Entity.to_str(v) for k,v in d.items() if not k.startswith('__')}

    def json(self):
        return json.dumps(self.to_dict())


class PostgresStorage(object):

    def __init__(self, db_config, factory='Class'):
        """factory Class, Dict, Tuple"""
        self.conn = psycopg2.connect(dbname=db_config['dbname'], user=db_config['user'], password=db_config['password'],
                         host=db_config['host'], application_name=db_config['application_name'])
        self.conn.autocommit = True

        self.cur = self.conn.cursor()
        self.factory = factory

    def get_cursor(self):
        if self.cur.closed:
            return self.conn.cursor()
        else:
            return self.cur

    def query(self, query, args=()):
        C = self.get_cursor()
        C.execute(query, args)
        if self.factory == 'Class':
            return [Entity({C.description[i].name: Entity.to_str(r) for i, r in enumerate(row)}) for row in C.fetchall()]
        elif self.factory == 'Dict':
            return [{C.description[i].name: Entity.to_str(col) for i, col in enumerate(row)} for row in C.fetchall()]
        else:
            return [x for x in C.fetchall()]

    def query_one(self, query, args=()):
        C = self.get_cursor()
        C.execute(query, args)
        if self.factory == 'Class':
            return Entity({C.description[i].name: r for i, r in enumerate(C.fetchone())})
        elif self.factory == 'Dict':
            return {C.description[i].name: Entity.to_str(col) for i, col in enumerate(C.fetchone())}
        else:
            return C.fetchone()

    def mogrify(self, query, args=()):
        C = self.get_cursor()
        return C.mogrify(query, args).decode()

    def execute(self, query, args=()):
        C = self.get_cursor()
        C.execute(query, args)


db = PostgresStorage(db_config, factory='Class')

if __name__ == '__main__':
    db = PostgresStorage(db_config, factory='Dict')
    a = db.query("""select * from trader where trader.id = %s""", (43040,))
    print(a[0])
    db = PostgresStorage(db_config, factory='Class')
    a = db.query_one("""select * from trader_profit_log where trader_id = %s""", (43040,))
    print(a.__dict__)
    print(a.to_dict())
    print(a.json())
    print(a.date)
