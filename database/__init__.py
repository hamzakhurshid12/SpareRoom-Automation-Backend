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
      `site_password` varchar(80) NOT NULL,
      `renew_time` INTEGER DEFAULT 1 NOT NULL
      `contact_message` varchar(80) NOT NULL,
      `follow_up_message` varchar(80) NOT NULL,
        )
    ''')

    create_table = '''
    CREATE TABLE IF NOT EXISTS click_history (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `hour1` INTEGER DEFAULT 0 NOT NULL,
      `hour2` INTEGER DEFAULT 0 NOT NULL,
      `hour3` INTEGER DEFAULT 0 NOT NULL,
      `hour4` INTEGER DEFAULT 0 NOT NULL,
      `hour5` INTEGER DEFAULT 0 NOT NULL,
      `hour6` INTEGER DEFAULT 0 NOT NULL,
      `hour7` INTEGER DEFAULT 0 NOT NULL,
      `hour8` INTEGER DEFAULT 0 NOT NULL,
      `hour9` INTEGER DEFAULT 0 NOT NULL,
      `hour10` INTEGER DEFAULT 0 NOT NULL,
      `hour11` INTEGER DEFAULT 0 NOT NULL,
      `hour12` INTEGER DEFAULT 0 NOT NULL,
      `hour13` INTEGER DEFAULT 0 NOT NULL,
      `hour14` INTEGER DEFAULT 0 NOT NULL,
      `hour15` INTEGER DEFAULT 0 NOT NULL,
      `hour16` INTEGER DEFAULT 0 NOT NULL,
      `hour17` INTEGER DEFAULT 0 NOT NULL,
      `hour18` INTEGER DEFAULT 0 NOT NULL,
      `hour19` INTEGER DEFAULT 0 NOT NULL,
      `hour20` INTEGER DEFAULT 0 NOT NULL,
      `hour21` INTEGER DEFAULT 0 NOT NULL,
      `hour22` INTEGER DEFAULT 0 NOT NULL,
      `hour23` INTEGER DEFAULT 0 NOT NULL,
      `hour24` INTEGER DEFAULT 0 NOT NULL,
      `user_id` INTEGER NOT NULL,
       FOREIGN KEY (user_id) REFERENCES tb_users(id) NOT NULL
        )'''
    
    c.execute(create_table)
    connection.commit()

initialize_database()
