#from typing_extensions import Required
import flask
from flask import request, jsonify
import sqlite3
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("main_database.db")
    except sqlite3.error as e:
        print(e)
    return conn

@auth.verify_password
def verify_password(username, password):
    conn = db_connection()
    db_password = conn.execute("SELECT password FROM tb_users WHERE username= ?",(username,)).fetchone()
    if(db_password is not None): 
        db_password = db_password[0]
        if (db_password==password): return True #Correct username and password
        else: return False #Incorrect Password
    else: return False #Incorrect username


##############---------------USER DATABSE : tb_users----------------##############
'''`tb_users` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `username` varchar(80) UNIQUE NOT NULL,
      `password` varchar(80) NOT NULL,
      `role` varchar(20) NOT NULL,
      `site_username` varchar(80) NOT NULL,
      `site_password` varchar(80) NOT NULL,
      `renew_hours` INTEGER DEFAULT 1 NOT NULL,
      `last_stats_update` datetime NOT NULL,
      `last_time_renewed` datetime NOT NULL
      )'''

@app.route('/all_users', methods=['GET'])
@auth.login_required
def all_users():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor = conn.execute("SELECT * FROM tb_users")
        users = [
            dict(id=row[0],
             username=row[1], 
             password=row[2], 
             role=row[3], 
             site_username=row[4], 
             site_password=row[5], 
             renew_hours=row[6],
             last_stats_update=row[7],
             last_time_renewed=row[8] )
            for row in cursor.fetchall()
        ]
        if users is not None:
            return jsonify(users)

@app.route('/add_user', methods=['POST'])
def add_user():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        site_username = request.form["site_username"]
        site_password = request.form["site_password"]
        renew_hours = request.form["renew_hours"]
        last_stats_update = request.form["last_stats_update"]
        last_time_renewed = request.form["last_time_renewed"]
        sql = """INSERT INTO tb_users (username, password, role, site_username, site_password, renew_hours, last_stats_update, last_time_renewed)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor = cursor.execute(sql, (username, password, role, site_username, site_password, renew_hours, last_stats_update, last_time_renewed))
        conn.commit()
        return f"User created successfully", 201

@app.route("/user", methods=["GET", "PUT", "DELETE"])
@auth.login_required
def single_user():
    conn = db_connection()
    cursor = conn.cursor()
    id = request.args['id']
    if request.method == "GET":
        cursor.execute("SELECT * FROM tb_users WHERE id=?", (id,))
        rows = cursor.fetchall()
        for r in rows:
            user = r
        if user is not None:
            return jsonify(user), 200
        else:
            return "Something wrong", 404

    if request.method == "PUT":
        sql = """UPDATE tb_users
                SET username = ?, 
                password=?, 
                role=?, 
                site_username=?, 
                site_password=?, 
                renew_hours=?,
                last_stats_update=?,
                last_time_renewed=?
                WHERE id=? """

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        site_username = request.form["site_username"]
        site_password = request.form["site_password"]
        renew_hours = request.form["renew_hours"]
        last_stats_update = request.form["last_stats_update"]
        last_time_renewed = request.form["last_time_renewed"]
        updated_user = {
            "id": id,
            "username": username, 
            "password": password, 
            "role": role, 
            "site_username": site_username, 
            "site_password": site_password, 
            "renew_hours": renew_hours,
            "last_stats_update": last_stats_update,
            "last_time_renewed":last_time_renewed
        }
        conn.execute(sql, (username, password, role, site_username, site_password, renew_hours, last_stats_update,last_time_renewed, id))
        conn.commit()
        return jsonify(updated_user)

    if request.method == "DELETE":
        sql = """ DELETE FROM tb_users WHERE id=? """
        conn.execute(sql, (id,))
        conn.commit()
        return "The user with id: {} has been deleted.".format(id), 200


##############---------------MESSAGES DATABSE: tb_messages----------------##############
'''`tb_messages` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `shortTermMessage` text NOT NULL,
      `midTermMessage` text NOT NULL,
      `longTermMessage` text NOT NULL,      
      `followUpMessage` text NOT NULL,
      `followUpDuration` INTEGER NOT NULL,
      `user_id` INTEGER NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )'''

@app.route('/all_user_messages', methods=['GET'])
@auth.login_required
def all_user_messages():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor = conn.execute("SELECT * FROM tb_messages")
        user_messages = [
            dict(id=row[0],
             shortTermMessage=row[1], 
             midTermMessage=row[2], 
             longTermMessage=row[3], 
             followUpMessage=row[4], 
             followUpDuration=row[5], 
             user_id=row[6] )
            for row in cursor.fetchall()
        ]
        if user_messages is not None:
            return jsonify(user_messages)

@app.route("/user_messages", methods=["GET", "POST", "PUT", "DELETE"])
@auth.login_required
def user_messages():
    conn = db_connection()
    cursor = conn.cursor()
    user_id = request.args['user_id']

    if request.method == "GET":
        cursor.execute(f"SELECT * FROM tb_messages WHERE user_id=?", (user_id,))
        rows = cursor.fetchall()
        message = None
        for r in rows:
            message = r
        if message is not None:
            return jsonify(message), 200
        else:
            return "Something wrong", 404


    if request.method == "POST":
        shortTermMessage = request.form["shortTermMessage"]
        midTermMessage = request.form["midTermMessage"]
        longTermMessage = request.form["longTermMessage"]
        followUpMessage = request.form["followUpMessage"]
        followUpDuration = request.form["followUpDuration"]
        
        sql = """INSERT INTO tb_messages (shortTermMessage, midTermMessage, longTermMessage, followUpMessage, followUpDuration, user_id)
                 VALUES (?, ?, ?, ?, ?, ?)"""
                 
        cursor = cursor.execute(sql, (shortTermMessage, midTermMessage, longTermMessage, followUpMessage, followUpDuration, user_id))
        conn.commit()
        return "User Messages with user id: {} has been created successfully".format(user_id), 201


    if request.method == "PUT":

        sql = """UPDATE tb_messages
                SET shortTermMessage = ?, 
                midTermMessage=?, 
                longTermMessage=?, 
                followUpMessage=?, 
                followUpDuration=? 
                WHERE user_id=? """

        shortTermMessage = request.form["shortTermMessage"]
        midTermMessage = request.form["midTermMessage"]
        longTermMessage = request.form["longTermMessage"]
        followUpMessage = request.form["followUpMessage"]
        followUpDuration = request.form["followUpDuration"]

        updated_message = {
            "user_id": user_id,
            "username": shortTermMessage, 
            "midTermMessage": midTermMessage, 
            "longTermMessage": longTermMessage, 
            "followUpMessage": followUpMessage, 
            "followUpDuration": followUpDuration
        }
        conn.execute(sql, (shortTermMessage, midTermMessage, longTermMessage, followUpMessage, followUpDuration, user_id))
        conn.commit()
        return jsonify(updated_message)

    if request.method == "DELETE":
        sql = """ DELETE FROM tb_messages WHERE user_id=? """
        conn.execute(sql, (user_id,))
        conn.commit()
        return "The user messages with user id: {} has been deleted.".format(user_id), 200



##############---------------AREAS DATABSE: tb_areas----------------##############
'''`tb_areas` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `areaName` varchar(150) NOT NULL,
      `ratio` INTEGER NOT NULL,
      `last_ratio_update` datetime DEFAULT 0 NOT NULL
      )
    '''

@app.route('/all_areas', methods=['GET'])
@auth.login_required  #ask Hamza
def all_areas():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor = conn.execute("SELECT * FROM tb_areas")
        areas = [
            dict(id=row[0],
             areaName=row[1], 
             ratio=row[2],
             last_ratio_update = row[3]
             )
            for row in cursor.fetchall()
        ]
        if areas is not None:
            return jsonify(areas)

@app.route("/area", methods=["GET", "POST", "PUT", "DELETE"])
@auth.login_required
def area():
    conn = db_connection()
    cursor = conn.cursor()
    area_name = request.args['area_name']

    if request.method == "GET":
        cursor.execute(f"SELECT * FROM tb_areas WHERE areaName=?", (area_name,))
        rows = cursor.fetchall()
        area_deails = None
        for r in rows:
            area_deails = r
        if area_deails is not None:
            return jsonify(area_deails), 200
        else:
            return "Something wrong", 404


    if request.method == "POST":
        
        ratio = request.form["ratio"]
        last_ratio_update = request.form["last_ratio_update"]
        sql = """INSERT INTO tb_areas (areaName, ratio, last_ratio_update)
                 VALUES (?, ?, ?)"""
                 
        cursor = cursor.execute(sql, (area_name, ratio, last_ratio_update))
        conn.commit()
        return "Area {} has been created successfully".format(area_name), 201


    if request.method == "PUT":

        sql = """UPDATE tb_areas
                SET ratio = ?, last_ratio_update=?
                WHERE areaName=? """

        ratio = request.form["ratio"]
        last_ratio_update = request.form["last_ratio_update"]

        updated_area = {
            "areaName": area_name,
            "ratio": ratio,
            "last_ratio_update": last_ratio_update
        }
        conn.execute(sql, (ratio, last_ratio_update, area_name))
        conn.commit()
        return jsonify(updated_area)

    if request.method == "DELETE":
        sql = """ DELETE FROM tb_areas WHERE areaName=? """
        conn.execute(sql, (area_name,))
        conn.commit()
        return "The Area: {} has been deleted.".format(area_name), 200


##############---------------AREAS CORRESPONDING TO USERS DATABSE: tb_user_areas----------------##############
'''`tb_user_areas` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `area_id` INTEGER NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
       FOREIGN KEY (`area_id`) REFERENCES `tb_areas`(`id`) 
      )
   '''


@app.route("/user_area", methods=["GET","POST", "DELETE"]) #askk hamza put not required
@auth.login_required
def user_area():
    conn = db_connection()
    cursor = conn.cursor()
    user_id = request.args['user_id']

    if request.method == "GET":
        cursor = conn.execute("SELECT * FROM tb_user_areas WHERE user_id=? ", (user_id,))
        user_areas = [
            dict(id=row[0],
             user_id=row[1], 
             area_id=row[2]
             )
            for row in cursor.fetchall()
        ]
        if user_areas is not None:
            return jsonify(user_areas)

    if request.method == "POST":
        area_id = request.form['area_id']    #ask Hamza

        sql = """INSERT INTO tb_user_areas (user_id, area_id)
                 VALUES (?, ?)"""
                 
        cursor = cursor.execute(sql, (user_id,area_id))
        conn.commit()
        return "Area with id: {} has been created successfully for user with id : {}".format(area_id,user_id), 201


    if request.method == "DELETE":
        area_id = request.form['area_id']    #ask Hamza

        sql = """ DELETE FROM tb_user_areas WHERE user_id=? AND area_id=? """
        conn.execute(sql, (user_id, area_id))
        conn.commit()
        return "The Area with id: {} has been deleted for user with id:{}.".format(area_id,user_id), 200




##############---------------STATISTICS DATABSE: tb_stats----------------##############
'''`tb_stats` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `clicks` INTEGER NOT NULL,
      `timeStamp` datetime NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )'''

@app.route("/user_stats", methods=["GET", "POST", "PUT", "DELETE"])
@auth.login_required
def user_stats():
    conn = db_connection()
    cursor = conn.cursor()
    user_id = request.args['user_id']

    if request.method == "GET":
        cursor.execute(f"SELECT * FROM tb_stats WHERE user_id=?", (user_id,))
        user_stats = [
            dict(id=row[0],
             user_id=row[1], 
             clicks=row[2],
             timeStamp=row[3]
             )
            for row in cursor.fetchall()
        ]
        if user_stats is not None:
            return jsonify(user_stats)


    if request.method == "POST":
        
        clicks = request.form["clicks"]
        timeStamp = request.form["timeStamp"]
        
        sql = """INSERT INTO tb_stats (user_id, clicks, timeStamp)
                 VALUES (?, ?, ?)"""
                 
        cursor = cursor.execute(sql, (user_id, clicks, timeStamp))
        conn.commit()
        return "Stats for User with Id: {} have been added".format(user_id), 201


    if request.method == "PUT":

        sql = """UPDATE tb_stats
                SET clicks = ?
                WHERE timeStamp=? AND user_id=?"""

        clicks = request.form["clicks"]
        timeStamp = request.form["timeStamp"]

        updated_stats = {
            "clicks": clicks,
            "timeStamp": timeStamp
        }

        conn.execute(sql, (clicks, timeStamp, user_id))
        conn.commit()
        return jsonify(updated_stats)

    if request.method == "DELETE":
        timeStamp = request.form["timeStamp"]
        sql = """ DELETE FROM tb_stats WHERE user_id=? AND  timeStamp=?"""
        conn.execute(sql, (user_id, timeStamp))
        conn.commit()
        return "The data for Time: {} of User: {} has been deleted .".format(timeStamp,user_id), 200


##############---------------LOGGING DATABSE: tb_logs----------------##############
'''`tb_logs` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `timeStamp` datetime NOT NULL,
      `activity` varchar(150) NOT NULL,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )'''

@app.route("/user_logs", methods=["GET", "POST", "DELETE"])
@auth.login_required
def user_logs():
    conn = db_connection()
    cursor = conn.cursor()
    user_id = request.args['user_id']

    if request.method == "GET":
        cursor.execute(f"SELECT * FROM tb_logs WHERE user_id=?", (user_id,))
        user_logs = [
            dict(id=row[0],
             user_id=row[1], 
             timeStamp=row[2],
             activity=row[3]
             )
            for row in cursor.fetchall()
        ]
        if user_logs is not None:
            return jsonify(user_logs)


    if request.method == "POST":
        
        timeStamp = request.form["timeStamp"]
        activity = request.form["activity"]
        
        sql = """INSERT INTO tb_logs (user_id, timeStamp, activity)
                 VALUES (?, ?, ?)"""
                 
        cursor = cursor.execute(sql, (user_id, timeStamp, activity))
        conn.commit()
        return "Data Logged for User with Id: {}".format(user_id), 201


    if request.method == "DELETE":
        sql = """ DELETE FROM tb_logs WHERE user_id=?"""
        conn.execute(sql, (user_id))
        conn.commit()
        return "All logs of User: {} have been deleted .".format(user_id), 200



##############---------------PEOPLE CONTACTED DATABSE: tb_people_contacted----------------##############
'''`tb_people_contacted` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `user_id` INTEGER NOT NULL,
      `person_id` varchar(80) NOT NULL,
      `isReplied` boolean NOT NULL,
      `last_time_contacted` datetime NOT NULL,
      `total_messages` INTEGER DEFAULT 0,

       FOREIGN KEY (`user_id`) REFERENCES `tb_users`(`id`) 
      )'''


@app.route("/people_contacted", methods=["GET", "POST","PUT", "DELETE"])
@auth.login_required
def people_contacted():
    conn = db_connection()
    cursor = conn.cursor()
    user_id = request.args['user_id']

    if request.method == "GET":
        cursor.execute(f"SELECT * FROM tb_people_contacted WHERE user_id=?", (user_id,))
        people_contacted = [
            dict(id=row[0],
             user_id=row[1], 
             person_id=row[2],
             isReplied=row[3],
             last_time_contacted=row[4],
             total_messages = row[5]
             )
            for row in cursor.fetchall()
        ]
        if people_contacted is not None:
            return jsonify(people_contacted)


    if request.method == "POST":
        
        person_id = request.form["person_id"]
        isReplied = request.form["isReplied"]
        last_time_contacted = request.form["last_time_contacted"]
        total_messages = request.form["total_messages"]

        sql = """INSERT INTO tb_people_contacted (user_id, person_id, isReplied, last_time_contacted, total_messages)
                 VALUES (?, ?, ?, ?, ?)"""
                 
        cursor = cursor.execute(sql, (user_id, person_id, isReplied, last_time_contacted, total_messages))
        conn.commit()
        return "User:{} details for Person:{} added successfully".format(user_id, person_id), 201

    if request.method == "PUT":

        sql = """UPDATE tb_people_contacted
                SET isReplied=?, last_time_contacted=?, total_messages=?
                WHERE user_id=? AND person_id = ?"""

        person_id = request.form["person_id"]
        isReplied = request.form["isReplied"]
        last_time_contacted = request.form["last_time_contacted"]
        total_messages = request.form["total_messages"]


        updated_people_contacted = {
            "user_id": user_id,
            "person_id": person_id,
            "isReplied": isReplied,
            "last_time_contacted": last_time_contacted,
            "total_messages": total_messages
        }

        conn.execute(sql, (isReplied, last_time_contacted, total_messages, user_id, person_id))
        conn.commit()
        return jsonify(updated_people_contacted)

    if request.method == "DELETE":
        sql = """ DELETE FROM tb_people_contacted WHERE user_id=?"""
        conn.execute(sql, (user_id))
        conn.commit()
        return "All Person Ids of User: {} have been deleted .".format(user_id), 200




if __name__ == "__main__":
    app.run(debug=True)