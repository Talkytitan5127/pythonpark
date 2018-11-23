#!/usr/bin/python3

import jwt
import mysql.connector
from mysql.connector import errorcode
from hashlib import sha256
import pdb
class Database:
    def __init__(self, host, username, password, db):
        try:
            self.connect = mysql.connector.connect(host=host, user=username, passwd=password, database=db)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        self.cur = self.connect.cursor()

    def __del__(self):
        self.cur.close()
        self.connect.close()
    
    def register(self, data):
        command = ("insert into users "
            "(username, first_name, last_name, password) "
            "values (%(username)s, %(first_name)s, %(last_name)s, %(password)s)"
        )
        data['password'] = sha256(data['password'].encode()).hexdigest()
        print(data)
        self.cur.execute(command, data)
        self.connect.commit()

    def login(self, data):
        data['password'] = sha256(data['password'].encode()).hexdigest()
        command = ("select id from users where username=%(username)s and password=%(password)s")
        self.cur.execute(command, data)
        result = self.cur.fetchone()
        if result is None:
            return "user doesn't exist", None
        token = self.get_token(data['username'])
        user_id = result[0]
        command = ("insert into session (token, user_id) values (%s, %s)")
        self.cur.execute(command, (token, user_id))
        self.connect.commit()
        return "Login successful", token
    
    def get_token(self, username):
        secret = 'pythonblog'
        algorithm = 'HS256'
        token = jwt.encode({'user': username}, secret, algorithm=algorithm).decode()
        return token

    def logout(self, token):
        command = ("delete from session where token=%s")
        self.cur.execute(command, (token,))
        self.connect.commit()
        return "OK"


    def get_lists_user(self):
        command = ("select username from users")
        arr = self.cur.execute(command)
        return arr