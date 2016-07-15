#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import logging

from Dater import config, mongo, app

app.config['TESTING'] = True
app.config['CSRF_ENABLED'] = False
app = app.test_client()
print app.post('/login', data=dict(email='stolman@gmail.com',password='qwerty123'), follow_redirects=True).data


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        # app.config['DEBUG'] = True
        app.config['CSRF_ENABLED'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def login(self, email, password):
        return self.app.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('eanegin@gmail.com', 'stixoplet123')
        assert 'You were logged in' in rv.data


if __name__ == '__main__':
    pass
    # unittest.main()