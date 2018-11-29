#!/usr/bin/python3

import jwt
import mysql.connector
from mysql.connector import errorcode
from hashlib import sha256

class Database:
    def __init__(self, host, username, password, dbname):
        try:
            self.connect = mysql.connector.connect(host=host, user=username, passwd=password, database=dbname)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        self.cur = self.connect.cursor(buffered=True)

#    def __del__(self):
#        self.cur.close()
#        self.connect.close()
    
    def register(self, data):
        command = ("insert into users "
            "(username, first_name, last_name, password) "
            "values (%(username)s, %(first_name)s, %(last_name)s, %(password)s)"
        )
        data['password'] = sha256(data['password'].encode()).hexdigest()
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
    
    def get_username(self, user_id):
        command = ("select username from users where id=%s")
        self.cur.execute(command, (user_id,))
        res = self.cur.fetchone()
        if not res:
            return None
        return res[0]
    
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
    
    def is_login(self, token):
        command = ("select user_id from session where token=%s")
        self.cur.execute(command, (token,))
        res = self.cur.fetchone()
        if not res:
            return None
        return res[0]

    def get_lists_user(self):
        command = ("select username, first_name, last_name from users")
        self.cur.execute(command)
        arr = self.cur.fetchall()
        return arr
 
    def create_blog(self, data):
        command = ("insert into blogs "
            "(theme, body) values "
            "(%(theme)s, %(body)s)"
        )
        if data['token'] is not None:
            query = ("select user_id from session where token=%s")
            self.cur.execute(query, (data['token'],))
            uid = self.cur.fetchone()
            if uid is None:
                return "no user with this token"
            else:
                data['uid'] = uid[0]
                command = ("insert into blogs "
                    "(theme, body, user_id) values "
                    "(%(theme)s, %(body)s, %(uid)s)"
                )
        else:
            data['uid'] = None
        
        self.cur.execute(command, data)
        self.connect.commit()
        return "Add blog successful"

    def delete_blog(self, data):
        command = ("delete from blogs where theme=%(theme)s")
        self.cur.execute(command, data)
        self.connect.commit()
        return "Delete successful"

    def get_blog(self, theme):
        command = ("select id from blogs where theme=%s")
        self.cur.execute(command, (theme,))
        result = self.cur.fetchone()
        if not result:
            return None
        return result[0]

    def get_blogs(self):
        command = ("select theme, body, user_id from blogs")
        self.cur.execute(command)
        blogs = self.cur.fetchall()
        return blogs

    def get_blogs_from_users(self):
        command = ("select theme, body, user_id from blogs where user_id is not null")
        self.cur.execute(command)
        blogs = self.cur.fetchall()
        return blogs
    
    def edit_blog(self, data):
        command = ("update blogs set theme=%(new_theme)s, body=%(body)s where theme=%(theme)s")
        self.cur.execute(command, data)
        self.connect.commit()
        return "edit successful"

    def create_post(self, data, blogs):
        command = (
            "insert into `posts` (head, body) "
            "values (%(head)s, %(body)s)"
        )
        self.cur.execute(command, data)
        self.connect.commit()

        command = (
            "insert into `post_blog` (post_id, blog_id) "
            "values (%s, %s)"
        )
        post_id = self.get_post(data['head'])
        for blog in blogs:
            blog = blog.strip()
            blog_id = self.get_blog(blog)
            self.cur.execute(command, (post_id, blog_id))
        self.connect.commit()
        return "Create post successful"

    
    def get_post(self, head):
        command = ("select id from `posts` where head=%s")
        self.cur.execute(command, (head, ))
        res = self.cur.fetchone()
        if not res:
            return None
        return res[0]

    def delete_post(self, data):
        command = ("delete from posts where head=%(head)s")
        self.cur.execute(command, data)
        self.connect.commit()
        return "delete post successful"
    
    def create_comment(self, data, comment):
        command = ("insert into `comments` (user_id, theme, body, post_id) "
        "values (%(user_id)s, %(theme)s, %(body)s, %(post_id)s)"    
        )
        post_id = self.get_post(data['post_id'])
        if post_id is None:
            return "post doesn't exist"
        data['post_id'] = post_id
        if comment != 'None':
            data['comm_id'] = self.get_comment(comment)
            command = ("insert into `comments` (user_id, theme, body, post_id, comm_id) "
        "values (%(user_id)s, %(theme)s, %(body)s, %(post_id)s, %(comm_id)s)"    
        )
        self.cur.execute(command, data)
        self.connect.commit()
        return "create comment successful"

    def get_comment(self, theme):
        command = ("select id from comments where theme=%s")
        self.cur.execute(command, (theme,))
        res = self.cur.fetchone()
        if not res:
            return None
        return res[0]
    
    def get_user_comments(self, user_id):
        command = ("select theme, body, post_id from comments where user_id=%s")
        self.cur.execute(command, (user_id,))
        comments = self.cur.fetchall()
        string = """
Post id: {}
Author_id: {}
theme: {}
comment: {}
------------------------"""
        for comment in comments:
            theme, body, post = comment
            print(string.format(post, user_id, theme, body))
        