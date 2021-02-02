import unittest
import os
import json
from main import app, db

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



if __name__=="__main__":
    unittest.main()