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
    i = get_counter(db, 'users')
    while i < 1000:
        print(i)
        user = fake.simple_profile()
        first, last = user['name'].split(' ', 1)
        data = {
            'username': user['username'],
            'first_name': first,
            'last_name': last,
            'password': user['mail']
        }
        try:
            db.register(data)
            i += 1
        except Exception as e:
            print(e)

    return "gen users successful"

def gen_blogs(db):
    print("gen_blogs")
    fake = Faker()
    i = get_counter(db, 'blogs')
    while i < 100:
        print(i)
        data = {}
        data['theme'] = fake.word()
        data['body'] = ''.join(fake.sentences(nb=2))
        data['token'] = None
        try:
            db.create_blog(data)
            i += 1
        except Exception as e:
            print(e)
    return "gen blogs success"

def gen_posts(db):
    print("gen_posts")
    command = ("select theme from blogs")
    db.cur.execute(command)
    blogs = db.cur.fetchall()
    fake = Faker()
    i = get_counter(db, 'posts')
    while i < 10000:
        print(i)
        blog = [blogs.pop()[0]]
        for j in range(100):
            data = {}
            data['head'] = fake.word()
            data['body'] = ''.join(fake.sentences(nb=2))
            try:
                db.create_post(data, blog)
                i += 1
            except Exception as e:
                print(e)
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
    i = get_counter(db, 'comments')
    while i < 100000:
        print(i)
        user_id = user()[0]
        post = posts.pop()[0]
        for q in range(10):
            print(i+q)
            data = {}
            data['user_id'] = user_id
            data['post_id'] = post 
            data['theme'] = fake.word()
            data['body'] = ''.join(fake.sentences(nb=3))
            try:
                db.create_comment(data, None)
                i += 1
            except Exception as e:
                print(e)
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

    
