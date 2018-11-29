#!/usr/bin/python3

import argparse
import mysql.connector

tables = {}
tables['users'] = (
    "create table `users` ("
    "   `username` varchar(255) not null unique,"
    "   `first_name` varchar(255) not null,"
    "   `last_name` varchar(255) not null,"
    "   `password` varchar(64) not null,"
    "   `id` int not null auto_increment,"
    "   primary key (`id`)"
    ")"
)

tables['session'] = (
    "create table `session` ("
    "   `token` varchar(255) not null unique,"
    "   `user_id` int not null,"
    "   foreign key (`user_id`) references users(`id`) on delete cascade"
    ")"
)

tables['blogs'] = (
    "create table `blogs` ("
    "   `body` text character set utf8 null,"
    "   `id` int not null auto_increment,"
    "   `theme` varchar(255) not null,"
    "   `user_id` int default null,"
    "   primary key (`id`),"
    "   foreign key (`user_id`) references users(`id`) on delete set null"
    ")"
)

tables['posts'] = (
    "create table `posts` ("
    "   `head` varchar(255) not null,"
    "   `body` text character set utf8 null,"
    "   `id` int not null auto_increment,"
    "   primary key(`id`)"
    ")"
)

tables['post-blog'] =(
    "create table `post_blog` ("
    "   `post_id` int not null,"
    "   `blog_id` int not null,"
    "   foreign key (`post_id`) references posts(`id`) on delete cascade,"
    "   foreign key (`blog_id`) references blogs(`id`) on delete cascade"
    ")"
)

tables['comments'] = (
    "create table `comments` ("
    "   `user_id` int not null,"
    "   `theme` varchar(255) not null,"
    "   `body` text character set utf8 not null,"
    "   `id` int not null auto_increment,"
    "   `post_id` int not null,"
    "   `comm_id` int,"
    "   primary key (`id`),"
    "   foreign key (`post_id`) references posts(`id`) on delete cascade,"
    "   foreign key (`comm_id`) references comments(`id`) on delete set null,"
    "   foreign key (`user_id`) references users(`id`)"
    ")"
)

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

if __name__ == '__main__':
    args = parse_args()
    args = args.__dict__

    cnx = mysql.connector.connect(host=args['host'], user=args['username'], passwd=args['password'])
    cursor = cnx.cursor()
    try:
        cursor.execute("create database {} default character set 'utf8'".format(args['dbname']))
    except mysql.connector.Error as err:
        print(err)

    cnx.database = args['dbname']

    names = ['users', 'session', 'blogs', 'posts', 'post-blog', 'comments']

    for name in names:
        print(name)
        try:
            cursor.execute(tables[name])
        except mysql.connector.Error as err:
            print(err)

    cursor.close()
    cnx.close()
