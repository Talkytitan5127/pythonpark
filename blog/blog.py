#!/usr/bin/python3

from database import Database

class Base:
    def __init__(self):
        self.db = Database(
            host='localhost',
            username='programmer',
            password='password',
            dbname='blogdb'
        )

class User(Base):
    def register(self):
        data = {}
        data['username'] = input("Enter username: ")
        data['password'] = input("Enter password: ")
        data['first_name'], data['last_name'] = input("Enter [first name] [last name]\n").split()
        self.db.register(data)
        return "register successful"
    
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
        users = self.db.get_lists_user()
        print("ALL USERS")
        for user in users:
            print("username={}\nfull name={} {}".format(*user))
            print('-'*20)

class Blog(Base):        
    def create_blog(self, token=None):
        data = {}
        data['theme'] = input("Enter theme of blog: ")
        data['body'] = input("Enter text of blog: ")
        data['token'] = token
        status = self.db.create_blog(data)
        print(status)

    def edit_blog(self):
        blog = input("Enter the theme of blog: ")
        blog_id = self.db.get_blog(blog)
        if not blog_id:
            print("No blog with theme `{}`".format(blog))
            return
        data = {}
        data['theme'] = blog
        data['new_theme'] = input("Enter new theme: ") or blog
        data['body'] = input("Enter new body: ")
        status = self.db.edit_blog(data)
        print(status)

    def delete_blog(self):
        data = {}
        data['theme'] = input("Enter theme of blog: ")
        status = self.db.delete_blog(data)
        print(status)

    def get_blogs(self):
        blogs = self.db.get_blogs()
        print("ALL BLOGS")
        string = """
--------------------------
        {}
--------------------------
{}
Create by: {}
--------------------------"""
        for theme, body, uid in blogs:
            uid = uid or "Admin"
            print(string.format(theme, body, uid))

    def get_blogs_from_users(self):
        blogs = self.db.get_blogs_from_users()
        print("ALL BLOGS")
        string = """
--------------------------
        {}
--------------------------
{}
Create by: {}
--------------------------"""
        for theme, body, uid in blogs:
            uid = uid or "Admin"
            print(string.format(theme, body, uid))

class Post(Base):
    def create_post(self):
        data = {}
        data['head'] = input("Enter name of post: ")
        data['body'] = input("Enter text of post: ")
        blogs = input("Enter theme of blogs, format [blog1,blog2,...,blogn]: ").split(',')
        status = self.db.create_post(data, blogs)
        print(status)
    
    def delete_post(self):
        data = {}
        data['head'] = input("Enter head of post: ")
        status = self.db.delete_post(data)
        print(status)
    
    def edit_post(self):
        data = {}
        head = input("Enter the head of post: ")
        post_id = self.db.get_post(head)
        if post_id is None:
            print("post doesn't exist")
        data['head'] = input("Enter new name of post: ")
        data['body'] = input("Enter new text of post: ")
        blogs = input("Enter theme of blogs, format [blog1,blog2,...,blogn]: ").split(',')
        self.db.delete_post({'head':head})
        status = self.db.create_post(data, blogs)
        print(status)
    
class Comment(Base):
    def create_comm(self, token=None):
        user_id = self.db.is_login(token)
        if user_id is None:
            print("User isn't login")
            return
        data = {}
        data['user_id'] = user_id
        data['body'] = input("Enter the comment: ")
        data['post_id'] = input("to which post: ")
        data['theme'] = input("theme of comment: ")
        comment = input("to which comment, enter theme [None]: ")
        status = self.db.create_comment(data, comment)
        print(status)

    def get_user_comments(self, token=None):
        user_id = self.db.is_login(token)
        if user_id is None:
            print("User isn't login")
            return
        self.db.get_user_comments(user_id)
    