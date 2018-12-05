#!/usr/bin/python3

import argparse
import time
from faker import Faker
from database import Database
from random import randint

def parse_args():
    parser = argparse.ArgumentParser(description='This is file to create database in mysql')
    parser.add_argument(
        '-u',
        action="store",
        dest="username",
        type=str,
        help='username to mysql server')
    parser.add_argument(
        '-p',
        action="store",
        dest="password",
        type=str,
        help='password to login')
    parser.add_argument(
        '-s',
        action='store',
        dest="host",
        type=str,
        help='host server to mysql',
        default='localhost'
    )
    parser.add_argument(
        '-n',
        action="store",
        dest="dbname",
        type=str,
        help="name of database"
    )
    return parser.parse_args()

def gen_users(db):
    print("gen_users")
    fake = Faker()
    data = []
    uniq = []
    for i in range(1020):
        print(i)
        user = fake.simple_profile()
        first, last = user['name'].split(' ', 1)
        data_user = {
            'username': user['username'],
            'first_name': first,
            'last_name': last,
            'password': user['mail']
        }
        if data_user['username'] not in uniq:
            data.append(data_user)
            uniq.append(data_user['username'])
    command = ("insert into `users` (username, first_name, last_name, password) values (%(username)s, %(first_name)s, %(last_name)s, %(last_name)s)")
    db.cur.executemany(command, data)
    db.connect.commit()
    return "gen users successful"

def gen_blogs(db):
    print("gen_blogs")
    fake = Faker()
    data = []
    for i in range(101):
        print(i)
        theme = fake.word()
        body = ''.join(fake.sentences(nb=2))
        data.append((theme, body))
    command = ("insert into `blogs` (theme, body) values (%s, %s)")
    db.cur.executemany(command, data)
    db.connect.commit()
    return "gen blogs success"

def gen_posts(db):
    print("gen_posts")
    command = ("select theme from blogs")
    db.cur.execute(command)
    blogs = db.cur.fetchall()
    fake = Faker()
    posts = []
    for i in range(10000):
        print(i)
        data = {}
        data['head'] = fake.word()
        data['body'] = ''.join(fake.sentences(nb=2))
        posts.append(data)

    command = ("insert into `posts` (head, body) values (%(head)s, %(body)s)")
    db.cur.executemany(command, posts)
    print("add posts success")
    post_blogs = []
    blog = blogs.pop()[0]
    blog_id = db.get_blog(blog)
    for i in range(10000):
        print(i)
        post_id = db.get_post(posts[i]['head'])
        data = {}
        data['post_id'] = post_id
        data['blog_id'] = blog_id
        post_blogs.append(data)
        if not i % 100:
            blog = blogs.pop()[0]
            blog_id = db.get_blog(blog)
    command = ("insert into `post_blog` (post_id, blog_id) values (%(post_id)s, %(blog_id)s)")
    db.cur.executemany(command, post_blogs)
    db.connect.commit()
    return "gen posts success"

def get_user(db):
    command = ("select id from users")
    db.cur.execute(command)
    users = db.cur.fetchall()
    def process():
        index = randint(0, len(users)-1)
        return users[index]
    return process

def gen_comments(db):
    command = ("select head from posts");
    user = get_user(db)
    db.cur.execute(command)
    posts = db.cur.fetchall()
    print("gen_comments")
    fake = Faker()
    comments = []
    i = 0
    while i < 100000:
        print(i)
        user_id = user()[0]
        post = posts.pop()[0]
        for q in range(10):
            data = {}
            data['user_id'] = user_id
            data['post_id'] = db.get_post(post)
            data['theme'] = fake.word()
            data['body'] = ''.join(fake.sentences(nb=3))
            comments.append(data)
            i += 1
    command = ("insert into `comments` (user_id, theme, body, post_id) "
        "values (%(user_id)s, %(theme)s, %(body)s, %(post_id)s)")
    db.cur.executemany(command, comments)
    db.connect.commit()    
    return "get comments success"

def get_counter(db, column):
    command = "select count(*) from {}".format(column)
    db.cur.execute(command)
    res = db.cur.fetchone()[0]
    return res

if __name__ == '__main__':
    begin = time.time()
    args = parse_args()
    args = args.__dict__

    faker = Faker()
    db = Database(**args)
    
    print(gen_users(db))
    print(gen_blogs(db))
    print(gen_posts(db))
    print(gen_comments(db))
    print("finished in {} (o)_(o)".format(time.time()-begin))

    
