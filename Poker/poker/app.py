import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import math

from helpers import login_required, usd


app = Flask(__name__)

#configures session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///poker.db")



@app.route("/", methods=["GET", "POST"])
def index():
    if 'user_id' not in session:
        return render_template("index.html")
        
    else:
        users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
        users=users[0]
        return render_template("index.html", users=users)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return render_template("error.html",message="No Username Entered")
        password = request.form.get("password")
        confirmed = request.form.get("confirmation")
        if not password:
            return render_template("error.html",message="No Password Entered")
        if len(password) <= 7:
            return render_template("error.html",message="Password must be atleast 8 characters")
        if password != confirmed:
            return render_template("error.html",message="Passwords do not match")


        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        except ValueError:
                return render_template("error.html", message="Username Taken")
        return redirect("/login")
    else:
        return render_template("register.html")







@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html",message="No Username Entered")
        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("error.html",message="No Password Entered")

        rows = db.execute("SELECT * FROM users WHERE username = ?",request.form.get("username"))
        id = db.execute("SELECT id FROM users WHERE username = ?",request.form.get("username"))

        password = request.form.get("password")

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return render_template("error.html",message="Username And/Or Password Is Incorrect")

        # Remember which user has logged in
        id=id[0]
        id = id['id']
        session["user_id"] = id





        session["user_id"] = id

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")



@app.route("/stats")
@login_required
def stats():
    users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    users=users[0]
    session.clear()
    redirect("/")

@app.route("/update", methods=["POST"])
@login_required
def update():
    id = session["user_id"]
    new_balance = request.form.get("newbalance")
    db.execute("UPDATE users SET balance = (balance + ?) WHERE id = ?", new_balance, id)
    return redirect("/")



@app.route("/track", methods=["GET", "POST"])
@login_required
def track():
    users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    users=users[0]
    if request.method == "POST":
        buyin = request.form.get("buyin")
        cashout = request.form.get("cashout")
        location = request.form.get("location")
        casino = request.form.get("casino")
        stakes = request.form.get("stakes")
        gametype = request.form.get("gametype")
        online = request.form.get("online")
        start = request.form.get("start_time")
        end = request.form.get("end_time")

        start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M')


        end = request.form.get("end_time")
        end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M')

        total_time_played = end_time - start_time
        
        
        current_datetime = datetime.now()
        if end_time > current_datetime:
            return render_template("error.html", message="You Cannot Record Games In The Future", users=users)


        


        total_hours_played = total_time_played.total_seconds() / 3600

        if total_hours_played <= 0:
            return render_template("error.html", message="Start Time Cannot Be After End Time", users=users)
        id= session["user_id"]

        earnings = int(cashout) - int(buyin)
        username = db.execute("SELECT username FROM users WHERE id = ?", id)
        username = username[0]
        username = username['username']

        check = db.execute("SELECT * FROM profile WHERE user_id = ?", id)
        if not check:
            db.execute("INSERT INTO profile (username, hours_played, lifetime_spend, lifetime_earnings, user_id) VALUES (?, ?, ?, ?, ?)",username, total_hours_played, buyin, earnings, id)

        else:




            db.execute("UPDATE profile SET hours_played = (hours_played + ?) WHERE user_id = ? ",total_hours_played, id)
            db.execute("UPDATE profile SET lifetime_spend = (lifetime_spend + ?) WHERE user_id = ? ",buyin, id)
            db.execute("UPDATE profile SET lifetime_earnings = (lifetime_earnings + ?) WHERE user_id = ? ",earnings, id)
            db.execute("UPDATE users SET balance = (balance + ?) WHERE id = ?",earnings, id)

        after_balance = db.execute("SELECT balance FROM users WHERE id = ?", id)
        after_balance = after_balance[0]
        after_balance = after_balance['balance']
        
        if online == "on":
            online = 1
        else:
            online = 0

        db.execute("INSERT INTO sessions (buyin, cashout, location, casino, stakes, gametype, is_online, start_time, end_time, user_id, current_balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", buyin, cashout, location, casino, stakes, gametype, online, start, end, id, after_balance)



    return render_template("record.html", users=users)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    users=users[0]
    casinos = []
    message = ""
    locations = db.execute("SELECT casino FROM sessions WHERE user_id = ?", session["user_id"])
    for location in locations:
        if location not in casinos:
            casinos.append(location)


    if request.method == "POST":
        stakes = request.form.get("stakes")
        gametype = request.form.get("gametype")
        online_live = request.form.get("online_live")
        casino_type = request.form.get("casino")
        if online_live == "Live":
            online_live = 0
        elif online_live == "Online":
            online_live = 1
        else:
            online_live = "Any"

        # Parameters list
        base_sessions_query =  "SELECT * FROM sessions WHERE user_id = ?"
        params = [session["user_id"]]

        if stakes != "Any":
            base_sessions_query += " AND stakes = ?"
            params.append(stakes)
        if online_live != "Any":
            base_sessions_query += " AND is_online = ?"
            params.append(online_live)
        if gametype != "Any":
            base_sessions_query += " AND gametype = ?"
            params.append(gametype)
        if casino_type != "Any":
            base_sessions_query += " AND casino = ?"
            params.append(casino_type)
        
        
        sessions = db.execute(base_sessions_query, *params)

        used = True
        if not sessions:
            used = False
            message = "No Sessions Found!"
        return render_template("history.html", sessions=sessions, users=users, usd=usd, used=used, round=round, casinos=casinos, message=message)

    else:
        sessions = db.execute("SELECT * FROM sessions WHERE user_id = ?", session["user_id"])
        used = True
        if not sessions:
            used = False
            message = "You Have Yet To Track Any Games!"

        return render_template("history.html", sessions=sessions, users=users, usd=usd, used=used, round=round, casinos=casinos, message=message)

def round_number(number, ndigits):
    return round(number, ndigits)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    is_friends = True
    users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    users=users[0]
    profile = db.execute("SELECT * FROM profile WHERE user_id = ?", session["user_id"])
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username[0]
    username = username['username']
   
    if not profile:
        db.execute("INSERT INTO profile (username, hours_played, lifetime_spend, lifetime_earnings, user_id) VALUES (?, ?, ?, ?, ?)",username, 0, 0, 0, session["user_id"])
        

    profile = db.execute("SELECT * FROM profile WHERE user_id = ?", session["user_id"])
    profile = profile[0]

    friends = db.execute("SELECT username FROM users WHERE id IN (SELECT friend_id FROM friends WHERE user_id = ?) ", session["user_id"])
    if not friends:
        is_friends = False
    friends_profiles = db.execute("SELECT * FROM profile WHERE user_id IN (SELECT friend_id FROM friends WHERE user_id = ?) ", session["user_id"])
    return render_template("profile.html", profile=profile, usd=usd, users=users, round=round_number, friends=friends, friends_profiles=friends_profiles, is_friends=is_friends)

    
@app.route("/addfriend", methods=["GET", "POST"])
@login_required
def addfriend():
    users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    users=users[0]

    friends_name = request.form.get('friendname')
    friend_id = db.execute("SELECT id FROM users WHERE username = ?", friends_name)

    if not friend_id:
        return render_template("error.html",message="Username is Invalid", users=users)
    friend_id = friend_id[0]
    friend_id = friend_id['id']
    db.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", session["user_id"], friend_id)
    db.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", friend_id, session["user_id"])


    
        
    return redirect("/profile")


@app.route("/viewstats", methods=["GET", "POST"])
@login_required
def viewstats():
    users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    users=users[0]

    user_id = request.form.get("friends_id")
    
    
    friendprofile = db.execute("SELECT * FROM profile WHERE user_id = ?", user_id)
    if friendprofile:
        friendprofile = friendprofile[0]
    
    return render_template("friendstats.html", friendprofile=friendprofile, usd=usd, users=users, round=round_number)


@app.route("/graphs",methods=["GET","POST"])
@login_required
def graphs():
    users = db.execute("SELECT * FROM users WHERE id == ?", session["user_id"])
    users=users[0]
    line_data = [0]
    labels = ['Starting Amount']
    profit = True

    casinos = []
    locations = db.execute("SELECT casino FROM sessions WHERE user_id = ?", session["user_id"])
    for location in locations:
        if location not in casinos:
            casinos.append(location)

    if request.method == "POST":
        line_data = [0]
        labels = ['Starting Amount']
        data = db.execute("SELECT start_time, current_balance FROM sessions WHERE user_id = ?", session["user_id"])
        if not data:
            line_data = [0, 0, 0]
            labels = ['Please Record Your First Cash Game']
            return render_template("graphs.html", users=users,line_data=line_data, labels=labels, profit=True, casinos=casinos)
        stakes = request.form.get("graph_stakes")
        gametype = request.form.get("graph_gametype")
        online_live = request.form.get("online_live")
        casino_type = request.form.get("graph_casino")
        if online_live == "Live":
            online_live = 0
        elif online_live == "Online":
            online_live = 1
        else:
            online_live = "Any"

        # Parameters list
        base_sessions_query =  "SELECT start_time, current_balance FROM sessions WHERE user_id = ?"
        params = [session["user_id"]]

        if stakes != "Any":
            base_sessions_query += " AND stakes = ?"
            params.append(stakes)
        if online_live != "Any":
            base_sessions_query += " AND is_online = ?"
            params.append(online_live)
        if gametype != "Any":
            base_sessions_query += " AND gametype = ?"
            params.append(gametype)
        if casino_type != "Any":
            base_sessions_query += " AND casino = ?"
            params.append(casino_type)
        
        
        alter_data = db.execute(base_sessions_query, *params)
        
        if not alter_data:
            line_data = [0, 0, 0]
            labels = ['No Data For These Variables']
            return render_template("graphs.html", users=users,line_data=line_data, labels=labels, profit=True, casinos=casinos)
        for day in alter_data:
            start_time = datetime.strptime(day['start_time'], '%Y-%m-%dT%H:%M')
            start_time = start_time.date()
            formatted_date = start_time.strftime('%d-%m-%Y')
            labels.append(formatted_date)

            line_data.append(day['current_balance'])
    
        if line_data[-1] <= line_data[0]:
            profit = False
        return render_template("graphs.html", users=users, line_data=line_data, labels=labels, profit=profit, casinos=casinos)


    else:
        data = db.execute("SELECT start_time, current_balance, buyin, cashout FROM sessions WHERE user_id = ?", session["user_id"])
        if not data:
            line_data = [0, 0, 0]
            labels = ['Please Record Your First Cash Game']
            return render_template("graphs.html", users=users,line_data=line_data, labels=labels, profit=True, casinos=casinos)
    
        running_total = 0
        for day in data:
            start_time = datetime.strptime(day['start_time'], '%Y-%m-%dT%H:%M')
            start_time = start_time.date()
            formatted_date = start_time.strftime('%d-%m-%Y')
            labels.append(formatted_date)
            profit = day['cashout'] - day['buyin']
            running_total += profit

            line_data.append(running_total)
    
        if line_data[-1] <= line_data[0]:
            profit = False
        return render_template("graphs.html", users=users, line_data=line_data, labels=labels, profit=profit, casinos=casinos)



@app.route("/removefriend", methods=["POST"])
def removefriend():
    friendid = request.form.get('delete_id')

    db.execute("DELETE FROM friends WHERE friend_id = ?", friendid)
    return redirect("/profile")