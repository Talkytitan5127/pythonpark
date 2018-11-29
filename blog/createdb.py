#!/usr/bin/python3

import mysql.connector

host = 'localhost'
username = 'programmer'
password = 'password'
dbname = 'blogdb'

cnx = mysql.connector.connect(host=host, user=username, passwd=password)
cursor = cnx.cursor()
try:
    cursor.execute("create database {} default character set 'utf8'".format(dbname))
except mysql.connector.Error as err:
    print(err)

cnx.database = dbname

names = ['users', 'session', 'blogs', 'posts', 'post-blog', 'comments']

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
    "   foreign key (`user_id`) references users(`id`)"
    ")"
)

tables['blogs'] = (
    "create table `blogs` ("
    "   `body` text character set utf8 null,"
    "   `id` int not null auto_increment,"
    "   `theme` varchar(255) not null,"
    "   `user_id` int default null,"
    "   primary key (`id`),"
    "   foreign key (`user_id`) references users(`id`)"
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

for name in names:
    print(name)
    try:
        cursor.execute(tables[name])
    except mysql.connector.Error as err:
        print(err)

cursor.close()
cnx.close()
