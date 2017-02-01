import sys, os
import unittest

basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, basedir + '/../')

from soco import app, init_db#, clear_db
app.config['TESTING'] = True
#app.config['DEBUG'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        #clear_db()

if __name__ == '__main__':
    unittest.main()
