#!/usr/bin/python3

from database import Database

class Blog:
    def __init__(self):
        self.db = Database(
            host='localhost',
            username='programmer',
            password='password',
            db='blogdb'
        )

    def register(self):
        data = {}
        data['username'] = input("Enter username: ")
        data['password'] = input("Enter password: ")
        data['first_name'], data['last_name'] = input("Enter [first name] [last name]\n").split()
        self.db.register(data)
    
    def login(self):
        data = {}
        data['username'] = input("Enter username: ")
        data['password'] = input("Enter password: ")
        status, token = self.db.login(data)
        print(status)
        return token
    
    def logout(self, token):
        self.db.logout(token)
        print("logout successful")
        return
    
    def get_users(self):
        return self.db.get_lists_user()

    