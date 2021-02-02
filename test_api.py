import unittest
import os
import json
from main import app, db
from werkzeug.security import generate_password_hash, check_password_hash
import pdb 
class APITestCase(unittest.TestCase):

    def setUp(self):
        # app.app.testing=True
        self.app = app.test_client()

    def test_getUser(self):
        result = self.app.get('/users')
        self.assertEqual(result.status_code, 200)

    def test_successful_register(self):
        payload = json.dumps({
                "name":"testing user",
                "password":"1234"
            })

        # When
        response = self.app.post('/register', headers={"Content-Type": "application/json"}, data=payload)

        # Then
        self.assertEqual(str, type(response.json['message']))
        self.assertEqual(200, response.status_code)

    # def test_successful_login(self):
    #     # Given
    #     name = "testing user"
    #     password = "1234"
    #     payload = json.dumps({
    #         "username": name,
    #         "password": password
    #     })

    # #     headers = {
    # #     'Authorization': 'Basic {}'.format(
            
    # #             '{username}:{password}'.format(
    # #                 username='testing user',
    # #                 password='1234')
    # #         )
    # #     ),
    # # }
    #     headers = {'Authorization': 'Basic {'anusha:1234'}'}

    #     #response = seslf.app.post('/login', headers={"Content-Type": "application/json"}, data=payload)

    #     # When
    #     response = self.app.post('/login', headers=headers, data=payload)

    #     print(response.json)

    #     # Then
    #     # self.assertEqual(str, type(response.json['token']))
    #     # self.assertEqual(200, response.status_code)


    def test__login(self):
        username = "anusha"
        password = generate_password_hash('1234', method='sha256')
        authorization = 'Basic ' + username + ":" + password
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': authorization
        }

        response = self.app.get('/login', headers=headers)
        # it returns None 
        authorization = response.headers.get("Authorization")

        self.assertIsNotNone(authorization)
        self.assertNotEqual(authorization, "")



if __name__=="__main__":
    unittest.main()