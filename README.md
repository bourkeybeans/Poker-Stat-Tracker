#Details
- Project Name : Poker Tracker
- NAME : Finley Bourke
- Github : Bourkeybeans
- Edx : FinBourke
- Norwich : United Kingdom
- Date : Tuesday 13th August 2024, 13/08/2024
# POKER TRACKERß


#### Video Demo:  <URL HERE>
#### Description:
My project allows users to track and visually graph up there poker results, through recording different aspects of their session, including the casino type, if the game was online or live, the stakes of the game, and there buyin and cashout, alongside the start and end time, allowing me to later calculate their total hours played.

SQL -
This is all stored within a sql database, poker.db, in which contains tables for sessions, allowing a record of all past sessions, the details of each and the history of the users balance.
The users table stores - a hashed password making use of from werkzeug.security import check_password_hash, generate_password_hash, to ensure literal password values are not stored within the database, this also stores the users username alongside their bankroll.
ß
The next table is their profile, created upon login linked through the primary key ID, which stores general statistics, including their lifetime spend, total earnings, total hours played that is calculated through collected datetime objects, alongside their hourly rate, calculated through profits divided by hours played.

Another important table I implemented is the friends table, this contains two columns, user_id and friend_id, meaning once somebody uses the addfriend function, a connection can be established between two users ids, and be then later queried to be shown upon the users friends list.
This can be then used to view friends stats and graphs, allowing a user to compare their poker results to the results of others.

All this information is withdrawn via /track, a function available to the user once they register and login.

Another Feature, was the visual representation of this data, from my SQL database, Once a user tracks these details and they are stored within the sessions table, they can be seen within a line graph, which clearly displays the variation in the users bankroll, allowing them quickly to establish if they are a winning poker player. Through the use of the javascript library chart.js i was able to chart up this data.
If the users most recent session is below their intially entered bankroll, the line will show red, clearly indicating overall loss, however it will show green in the case that the user has been profitable and their balance is above their initially provided bankroll.
I added a dropdown menu, allowing users to query this data, allowing them to establish areas of poker in which they are most successful, this includes the type of game, if it was online, the casino alongside the stakes. I achieved this through creating a base SQL query, selecting all data, when a user selects a specific parameter in which they decide to narrow down E.g To show online only, the string query will have extra conjucated to it, extending the query to include the "WHERE casino = ?" allowing the data to be queried specifcally to the users needs.
I ensure throughout the graphs page, to ensure their is no errors by repeatedly checking that if their is no data, to send this message to the HTML page and display it accordingly. Upon a users first use, it will tell them to redirect to the track page, where they can input data, this is the same for the history page, that displays a history of all past sessions and can be queried in the same way as the graphs.
To allow myself to do this, i had to research into how to visually represent SQL data in the form of Graphs.


To ensure my flask application has a clean sleek design, i created a layout in which is consistent throughout each page on the site, as long as they are logged in via session, this contains both the navigation buttons, logo, alongside the logged in users current balance and an input box and button allowing them to deposit into their bankroll at any point throughout the application.
In addition to this, the site has a dynamic homepage, when a user is not logged in, it will display the features, describe the application, and prompt them to register with a button to direct them.
If a user is already logged in, the webpage will welcome the user back, and prompt them to the tracking page, where they can continue to record their most recent game.


The profile section of the application, displays overall statistics of the logged in user, but also a friends list, that checks the friends table for any linked ids, these will be displayed within the dropdown menu, alongside some available actions. These include a button to remove friend, deleting their connection from the database on both ends, meaning from both accounts they will no longer be shown as friends.
There is also a view stats button, that will redirect the user to the profile page, but instead displaying the friends username, and their statistics instead. 
In the case that a user has no friends this will be shown within the dropdown menu, the buttons will no longer show with a statement that their is no  actions to be made. 
Above i implemented a text input box, with the placeholder username, this will take the username submitted and query the database, if present they will be added as a friend, however in the case that this user does not exist the user will be alerted accordingly through a redirection and alert.

Within my application, session is used, a flask library allowing the browser to remember the logged in user, through an autoincremented ID that is inserted within the users SQL table. This will be able to both check if the user is logged in, by checking if the current user_id is within session, allowing the navigation bar to update. session is frequently also used to query the SQL database to find the data specific to the logged in user during data visualisation.
I also implemented aspects of bootstrap, particularly within the history and profile pages, as their interactive tables enhanced the visual aspects of my application.

Diffrent Files Within My App - 
App.py Contains the Backend of my flask application - and the following functions - 

1. @app.route("/", methods=["GET", "POST"])
def index():

This Will direct the user to the Homepage, with features and a register button for new users, and a welcome for logged in users

2. @app.route("/register", methods=["GET", "POST"])
def register():

Adds the users, inputted username from register.html and password hashed into the users table, and creates a new profile for them.
if the password is below 8 characters or the username is taken they will be redirected to error.html with a custom related error message.

3. @app.route("/login", methods=["GET", "POST"])
def login():

Takes the users, username and password, checks password hash, if both match up with someone in the users table, they will be logged in, setting session[user_id] to the equivilant id in the users database.


4. @app.route("/logout")
@login_required
def logout():

Logs Out the Current user, clearing the flask session


5. @app.route("/track", methods=["GET", "POST"])
@login_required
def track():
accepts post method to retrieve data from the form in record.html, taking poker data.
This will be added to the sessions table

if get method is used, they will be directed to the tracking form, where they can input this data.

6. @app.route("/history", methods=["GET", "POST"])
@login_required
def history():

Via GET this will, collect all the data of the logged in user, regarding prior sessions, and display them in a table
Via POST - it will take information from a dropdown menu, allowing the user to display information according to the selected variables, e.g only sessions at a specific casino, other variables can be left as the preselected ANY and will not be included in the formed SQL querey used to display this information form the database


7. @app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

Profile Will display the users statistics in a table, displayed within the profile table
it also selects usernames from users where the friend_id is paired with the current user_id in the friends table, enabling these friends usernames to be displayed in a friends list.

8. app.route("/addfriend", methods=["GET", "POST"])
@login_required
def addfriend():

Forms Said Connection within the friends table, between the logged in user and the typed username on the profile page.

9. @app.route("/viewstats", methods=["GET", "POST"])
@login_required
def viewstats():

Directs you to the friends stats, when the button view stats is clicked on the profile pages friends list. This will present their stats on a different html page.

10. @app.route("/graphs",methods=["GET","POST"])
@login_required
def graphs():

Post method, querys the data to enable customized options of the graphs data.
This creates a custom SQL query

Via Post, the javascript library chart.js is used, which takes the arrays for each axis of the graph.
These are passed in through SQL queries that take the session date, and the balance at the time, these are appended to seperate lists that are passed into javascript with jinja and then visualised within a line graph.
I debated adding an option to switch the graph to a bar chart, however, decided it to be unesssecary due to only using continuous data, and the line graph being more clear showing th change of balance over time.


11. @app.route("/removefriend", methods=["POST"])
def removefriend():
    
    This finds the id of the friend whos remove button is clicked, and deletes the connection between the logged in user id and the friends id, meaning they are no longer displayed as friends on the profiles page.


All Errors Throughout my App, where handled with an error.html page, in the future i would prefer to have implemented javascript alerts, with custom dropdowns so users are not inconvieniently sent to a seperate page. I may add this in a future update.

In addition to this, i would like to add the option to record tournament games, and the ability not just add friends, but send requests, enabling them to be accepted rather then being able to add whoever with their username alone. I believe i could do this through the use of an additional column in the friends table, that will establish if a friends connection is outgoing or has been accepted.


OVERALL SUMMARY -
Poker Tracker Application
Description: Developed a comprehensive web-based Poker Tracker application using Flask to help players efficiently manage and analyze their poker sessions. The application offers a full suite of features designed to enhance the user experience, including secure user authentication (login/logout), profile management, session tracking, and detailed financial analysis.
Key Features:
* Session Tracking: Users can log each poker session with start and end times, allowing the system to calculate total playtime. The application tracks individual session outcomes (winnings or losses) and aggregates this data for analysis.
* Profile Management: Implemented a robust profile management system where users can update their personal details and view their overall poker performance, including total playtime, cumulative winnings, and losses.
* Data Visualization: Integrated dynamic graphing capabilities that visualize the user's financial performance over time. The graphs provide insights into winnings and losses, allowing users to track their progress and identify trends.
* Historical Session Data: Users can review past poker sessions, providing them with a detailed history of their gameplay, including specific session dates, duration, and financial outcomes.
* User Authentication: Developed secure login and logout functionalities using Flask, ensuring user data integrity and privacy.
Technologies Used:
* Backend: Flask, SQLite (or other relational databases)
* Frontend: HTML, CSS, Bootstrap for responsive design, Javascript
* Data Visualization: Chart.js
* User Authentication: Flask-Session
Impact: This project demonstrates my ability to create full-stack web applications that handle sensitive user data, provide meaningful data analysis, and offer a user-friendly interface. It showcases my skills in backend development, data management, and front-end design, all while emphasizing secure coding practices.

This description highlights your project's functionality, the technology stack you used, and the impact of your work, making it attractive to potential employers.



