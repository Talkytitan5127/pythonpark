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

names = ['users', 'session']

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

for name in names:
    cursor.execute(tables[name])

cursor.close()
cnx.close()
