import sqlite3
import os


def initialize_database():
    if os.path.exists("main_database.db"):
        conn = sqlite3.connect('main_database.db')
    else:
        conn = sqlite3.connect('main_database.db')
    createDatabaseStructure(conn)


def createDatabaseStructure(connection):
    c = connection.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS `tb_users` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `username` varchar(80) UNIQUE NOT NULL,
      `password` varchar(80) NOT NULL,
      `role` varchar(20) NOT NULL,
      `site_username` varchar(80) NOT NULL,
      `site_password` varchar(80) NOT NULL
        )
    ''')
    connection.commit()

initialize_database()
