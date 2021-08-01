# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
'''from operator import indexOf
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import json

from requests.sessions import session
import database
import datetime

from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
'''
from datetime import datetime

from werkzeug.datastructures import CombinedMultiDict
from scrapper import *
import sqlite3


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("main_database.db")
    except sqlite3.error as e:
        print(e)
    return conn

def updateStats(user):
    conn = db_connection()
    user_id = user[0]
    user_name = user[1]
    spare_room_username = user[4]
    spare_room_password = user[5]
    last_stats_update = user[7]

    session = getLoginSession(spare_room_username, spare_room_password)
    current_stats = getClicks(session)
    current_hour = int(str(datetime.now())[11:13])
    display_message = 'STATS NOT UPDATED; USER: {}; TIME: {}:00:00;'.format(user_name, current_hour)
    if(last_stats_update!=0):
        time_passed = abs(current_hour - last_stats_update)
        if(time_passed >= 1):
            conn.execute("UPDATE tb_stats SET clicks=? WHERE user_id=? AND timeStamp=?",(current_stats, user_id, current_hour))
            activity = 'Stats updated to {} for time {}:00:00'.format(current_stats, current_hour)
            conn.execute("INSERT INTO tb_logs (user_id, timeStamp, activity) VALUES (?, ?, ?)",(user_id, datetime.now(),activity))
            conn.execute("UPDATE tb_users SET last_stats_update=? WHERE id=?",(current_hour, user_id))
            display_message = ('STATS UPDATED; USER: {}; TIME: {}:00:00; CLICKS: {}'.format(user_name, current_hour, current_stats))
    else:
        conn.execute("UPDATE tb_stats SET clicks=? WHERE user_id=? AND timeStamp=?",(current_stats, user_id, current_hour))
        activity = 'Stats updated to {} for time {}:00:00'.format(current_stats, current_hour)
        conn.execute("INSERT INTO tb_logs (user_id, timeStamp, activity) VALUES (?, ?, ?)",(user_id, datetime.now(), activity))
        conn.execute("UPDATE tb_users SET last_stats_update=? WHERE id=?",(current_hour, user_id))
        display_message = ('STATS UPDATED; USER: {}; TIME: {}:00:00; CLICKS: {}'.format(user_name, current_hour, current_stats))
    print(display_message)
    conn.commit()

def sendMessagesToUncontactedPeople(user):
    conn = db_connection()
    user_id = user[0]
    user_name = user[1]
    spare_room_username = user[4]
    spare_room_password = user[5]
    session = getLoginSession(spare_room_username, spare_room_password)

    user_areas = conn.execute("SELECT * FROM tb_user_areas WHERE user_id=?",(user_id,))
    for user_area in user_areas:
        area_id = user_area[2]
        area = conn.execute("SELECT * FROM tb_areas WHERE id=?",(area_id,)).fetchone()
        area_name = area[1]

        UncontactedPeople = getPeopleIDs(session,area_name)
        #UncontactedPeople = ['15857312']
        for person_id in UncontactedPeople:
            conn.execute("INSERT INTO tb_people_contacted (user_id, person_id, isReplied, last_time_contacted) VALUES (?, ?, ?, ?)",(user_id, person_id, False, -1))            
            minTerm = minimumTerm(person_id)
            if(minTerm >= 24):
                message = conn.execute("SELECT longTermMessage FROM tb_messages WHERE user_id=?",(user_id,)).fetchone()[0]
            elif (minTerm >= 12):
                message = conn.execute("SELECT midTermMessage FROM tb_messages WHERE user_id=?",(user_id,)).fetchone()[0]
            else:
                message = conn.execute("SELECT shortTermMessage FROM tb_messages WHERE user_id=?",(user_id,)).fetchone()[0]

            sendMessage(session, person_id, message)
            msgCount = messageCount(session, person_id)

            activity = 'Message sent to Person({}) from {}'.format(person_id, area_name)
            conn.execute("INSERT INTO tb_logs (user_id, timeStamp, activity) VALUES (?, ?, ?)",(user_id, datetime.now(),activity))
            current_hour = int(str(datetime.now())[11:13])
            conn.execute("UPDATE tb_people_contacted SET last_time_contacted=?, total_messages=? WHERE user_id=? AND person_id=?",(current_hour, msgCount, user_id, person_id))

        if(len(UncontactedPeople) == 0):
            display_message = 'NO UNCONTACTED PERSON; USER: {}; AREA: {}; TIME: {}:00:00;'.format(user_name,area_name, int(str(datetime.now())[11:13]))
        else:
            display_message = ('MESSAGE SENT; USER: {}; AREA: {}; TIME: {}:00:00; PEOPLE: {}'.format(user_name,area_name, int(str(datetime.now())[11:13]), UncontactedPeople))
        print(display_message)

    conn.commit()

def checkForReply(user):
    conn = db_connection()
    user_id = user[0]
    user_name = user[1]
    spare_room_username = user[4]
    spare_room_password = user[5]
    session = getLoginSession(spare_room_username, spare_room_password)

    PersonNotReplied = conn.execute("SELECT person_id FROM tb_people_contacted WHERE user_id=? AND isReplied=?",(user_id, False)).fetchall()
    for person_id in PersonNotReplied:
        person_id = person_id[0]
        old_message_count = conn.execute("SELECT total_messages FROM tb_people_contacted WHERE user_id=? AND person_id=?",(user_id, person_id)).fetchone()[0]
        new_message_count = messageCount(session, person_id)
        if(new_message_count > old_message_count):
            conn.execute("UPDATE tb_people_contacted SET isReplied=?, total_messages=? WHERE user_id=? AND person_id=?",(True, new_message_count, user_id, person_id))
            print('USER RECEIVED REPLY; USER: {}; PERSON: {};'.format(user_name,person_id))

    conn.commit()


def sendFollowUpMessage(user):
    #based on follow up duration update tb_people_contacted last-time_contacted
    #also calculate time passed accordingly and compare with follow up duration maybe in months
    conn = db_connection()
    user_id = user[0]
    user_name = [1]
    spare_room_username = user[4]
    spare_room_password = user[5]
    session = getLoginSession(spare_room_username, spare_room_password)

    PersonNotReplied = conn.execute("SELECT person_id FROM tb_people_contacted WHERE user_id=? AND isReplied=?",(user_id, False)).fetchall()
    for person_id in PersonNotReplied:
        person_id = person_id[0]
        last_time_contacted = conn.execute("SELECT last_time_contacted FROM tb_people_contacted WHERE user_id=? AND person_id=?",(user_id, person_id)).fetchone()[0]
        current_hour = int(str(datetime.now())[11:13])
        FollowUpDuration = conn.execute("SELECT followUpDuration FROM tb_messages WHERE user_id=?",(user_id,)).fetchone()[0]
        FollowUpMessage = conn.execute("SELECT followUpMessage FROM tb_messages WHERE user_id=?",(user_id,)).fetchone()[0]
        if(abs(last_time_contacted-current_hour) >= FollowUpDuration):
            sendMessage(session, person_id, FollowUpMessage)
            current_hour = int(str(datetime.now())[11:13])
            msgCount = messageCount(session, person_id)
            conn.execute("UPDATE tb_people_contacted SET last_time_contacted=?, total_messages=? WHERE user_id=? AND person_id=?",(current_hour, msgCount, user_id, person_id))
            activity = 'Follow Up Message sent to Person({}) '.format(person_id)
            conn.execute("INSERT INTO tb_logs (user_id, timeStamp, activity) VALUES (?, ?, ?)",(user_id, datetime.now(),activity))
            print('FOLLOW UP MESSAGE SENT; USER: {}; PERSON: {};'.format(user_name,person_id))
    conn.commit()


def renew(user):
    conn = db_connection()
    user_id = user[0]
    user_name = user[1]
    spare_room_username = user[4]
    spare_room_password = user[5]
    session = getLoginSession(spare_room_username, spare_room_password)
    last_time_renewed = conn.execute("SELECT last_time_renewed FROM tb_users WHERE id=?",(user_id,)).fetchone()[0]
    renew_hours = conn.execute("SELECT renew_hours FROM tb_users WHERE id=?",(user_id,)).fetchone()[0]
    current_hour = int(str(datetime.now())[11:13])
    if(abs(last_time_renewed - current_hour)>=renew_hours):
        renewListings(session)
        activity = 'Listings renewed'
        conn.execute("INSERT INTO tb_logs (user_id, timeStamp, activity) VALUES (?, ?, ?)",(user_id, datetime.now(),activity))
        conn.execute("UPDATE tb_users SET last_time_renewed=? WHERE id=?",(current_hour,user_id))
        print('LISTINGS RENEWED; USER: {}; TIME: {}:00:00;'.format(user_name,current_hour))
    else:
        print('LISTINGS NOT RENEWED; USER: {}; TIME: {}:00:00;'.format(user_name,current_hour))
    conn.commit()

def updateRatio(area):
    conn = db_connection()
    area_id = area[0]
    area_name = area[1]
    last_ratio_update = area[3]
    current_hour = int(str(datetime.now())[11:13])
    if(current_hour-last_ratio_update == 0):
        ratio = getRoomsRatio(area_name)
        conn.execute("UPDATE tb_areas SET ratio = ?, last_ratio_update=? WHERE id=?",(ratio, current_hour,area_id))
        print('RATIO UPDATED; AREA: {}; TIME: {}:00:00;'.format(area_name, current_hour))
    else:
        print('RATIO NOT UPDATED; AREA: {}; TIME: {}:00:00;'.format(area_name, current_hour))

    conn.commit()


def main():
    #creating a db connection to fetch data from the database
    conn = db_connection()

    get_all_users_query = "SELECT * FROM tb_users"
    get_all_areas_query = "SELECT * FROM tb_areas"
    users = conn.execute(get_all_users_query).fetchall()
    areas = conn.execute(get_all_areas_query).fetchall()

    while(True):
        for user in users:
            print()
            updateStats(user)
            renew(user)

            sendMessagesToUncontactedPeople(user)
            checkForReply(user)
            sendFollowUpMessage(user)

        
        for area in areas:
            print()
            updateRatio(area)

        conn.commit()

            
    

if __name__ == "__main__":
    main()

    