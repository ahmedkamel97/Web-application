#Importing the libraries 
import os
import unittest
import sys
import requests

#Defining the  file path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from board import app, db

TEST_DB = 'test.db'

"""
Primary class containing all the tests 
"""
class Basic(unittest.TestCase):
    '''
    These instructions are executed prior to each test
    '''    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
    '''
    These instructions are executed after each test
    '''
    def tearDown(self):
        pass
    '''
    This function tests if the primary page is loaded or not 
    '''
    def test_main_page(self):        
        req = self.app.get('/main', follow_redirects=True)
        self.assertEqual(req.status_code, 200)
    '''
    This function tests that login page is shown to new users 
    '''
    def test_login(self):
        req = requests.get('http://127.0.0.1:5000/')
        self.assertEqual(req.url, 'http://127.0.0.1:5000/login')

    '''
    This functions tests that the registration page works properly and redirects users to the main page after registering 
    '''
    def test_registration(self):
        
        details = {'username':'Dolly', 'password':'ncelekckln!mv', 'repeat':'ncelekckln!mv'}
        req = requests.post('http://127.0.0.1:5000/register', data = details)
        req = requests.post('http://127.0.0.1:5000/login', data = details)
        self.assertEqual(req.url, 'http://127.0.0.1:5000/main')

    '''
    This functions tests that users with the proper credentials can login and view their data. 
    '''
    def test_correct_login(self):        
        details = {'username':'Dolly',  'password':'ncelekckln!mv'}
        req = requests.post('http://127.0.0.1:5000/login', data = details)
        self.assertEqual(req.url, 'http://127.0.0.1:5000/main')
    '''
    This function tests that users that are not registered cannot login 
    '''
    def test_faulty_login(self):
        details = {'username':'Rita', 'password':'fake'}
        req = requests.post('http://127.0.0.1:5000/login', data = details)
        self.assertEqual(req.url, 'http://127.0.0.1:5000/login')

#Running the tests
if __name__ == "__main__":
    unittest.main()
