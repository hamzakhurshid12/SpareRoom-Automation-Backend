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

    queryUsers = '''
        CREATE TABLE IF NOT EXISTS `tb_users` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `username` varchar(80) UNIQUE NOT NULL,
      `password` varchar(80) NOT NULL,
      `role` varchar(20) NOT NULL,
      `site_username` varchar(80) NOT NULL,
      `site_password` varchar(80) NOT NULL,
      `renew_hours` INTEGER DEFAULT 1 NOT NULL,
      `last_stats_update` INTEGER DEFAULT 0 NOT NULL,
      `last_time_renewed` INTEGER DEFAULT 0 NOT NULL

      )
    '''

    queryMessages = '''
        CREATE TABLE IF NOT EXISTS `tb_messages` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `shortTermMessage` text NOT NULL,
      `midTermMessage` text NOT NULL,
      `longTermMessage` text NOT NULL,      
      `followUpMessage` text NOT NULL,
      `followUpDuration` INTEGER NOT NULL,
      `user_id` INTEGER NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )
    '''
    queryAreas = '''
        CREATE TABLE IF NOT EXISTS `tb_areas` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `areaName` varchar(150) NOT NULL,
      `ratio` INTEGER NOT NULL,
      `last_ratio_update` INTEGER DEFAULT 0 NOT NULL
      )
    '''
    queryUserAreas = '''
        CREATE TABLE IF NOT EXISTS `tb_user_areas` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `area_id` INTEGER NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
       FOREIGN KEY (`area_id`) REFERENCES `tb_areas`(`id`) 
      )
    '''
    queryStats = '''
        CREATE TABLE IF NOT EXISTS `tb_stats` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `clicks` INTEGER NOT NULL,
      `timeStamp` INTEGER DEFAULT 0 NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )
    '''

    queryLogs = '''
        CREATE TABLE IF NOT EXISTS `tb_logs` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `timeStamp` datetime NOT NULL,
      `activity` varchar(150) NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )
    '''

    queryPeopleContacted = '''
        CREATE TABLE IF NOT EXISTS `tb_people_contacted` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `person_id` varchar(80) NOT NULL,
      `isReplied` boolean NOT NULL,
      `last_time_contacted` INTEGER NOT NULL,
      `total_messages` INTEGER DEFAULT 0,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )
    '''
    
    c.execute(queryUsers)
    c.execute(queryMessages)
    c.execute(queryAreas)
    c.execute(queryUserAreas)
    c.execute(queryStats)
    c.execute(queryLogs)
    c.execute(queryPeopleContacted)
    connection.commit()

initialize_database()
