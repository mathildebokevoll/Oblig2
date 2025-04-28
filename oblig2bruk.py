# INF115 Databases and Modelling
# Obligatory Assignment 2

#%%
"""
Sources:
To solve these problems, the lecture notes, modules and assignments provided by David Grellscheid from INF115 were used.
Other usefull sources that were used are https://docs.python.org/3/library/sqlite3.html#tutorial , https://sqlite.org and https://shiny.posit.co/py/
Moreover, the built in information provided by python/VS-code was used*

*by clicking "Command" on keyboard and holding or cliking mouse on "ui" to read about and test the different alternatives in my code, 
in order to understand which to choose for the different tasks. Here is the path to the general "ui"-page:
/Users/mathildebokevoll/anaconda3/lib/python3.11/site-packages/shiny/ui/__init__.py
and the more specific pages ui.xxx_xxx were also used as sources, for instance the ui.input_selectize:
/Users/mathildebokevoll/anaconda3/lib/python3.11/site-packages/shiny/ui/_input_select.py
Some places in the code, I have made comments based on the information from this source, in order to understand and remember the connections and meanings.

In addition, ChatGPT was used as a tool to:
* solve errors, escpecially when the code would not run and I could not find the problem myself
* send prompts and answer questions to learn types of coding I did not know from before, or could not find quick answers to in the mentioned sources
* to improve the different parts of code I made, confirm its quality and make sure the sql-querys were safely written
I have continously made sure I understand the code or answers I got from ChatGPT, and have only used the answers I understood and could have managed to teach myself with other more time-consuming tools.
How and where ChatGPT was used, is written continously in the code.

Reflection:
In the code I have made I used the bysykkel.db database file (where I imported data from the bysykkel.csv file provided) I made in Obligatory Assignment 1, to test my code in this assignmengt.
Therefore I have continued with the names I made in that database/assignment.
However, I am unsure if this code will work with the file you are testing, and therefore I have uploaded my bysykkel.db file as well,
to show you that my code works, even though I have not been able to make it work for general example filen, but only my special one.
"""
#%%

from shiny import App, ui, render, reactive
import pandas as pd
import sqlite3

def get_data(query, params=None):
    with sqlite3.connect("bysykkel.db") as con:
        return pd.read_sql(query, con, params=params)
    
"""
My code is diveded into two main parts:
The app_ui part, which includes the different ui.inputs and ui.outputs which make the application
and the def server(input, output, session):, which includes the different functions to solve the tasks
This means that the solution to each task needs to be seen as a whole of the two parts.
"""


##########          app_ui          ##########

app_ui = ui.page_fluid(
    ui.navset_tab(

        # Task 1: Adding Users
        ui.nav_panel("Add User",
            # 1a) Create a form, i.e. a set of text input boxes, that asks for name, phone number and email of a User in your design. 
            ui.input_text("add_name", "Name:"),
            ui.input_text("add_phonenumber", "Phone Number:"),
            ui.input_text("add_email", "E-mail:"),

            # 1a) The form should have a submit button. 
            ui.input_action_button("add_user_submit_button", "Add User"),

            # 1a) Print the input values below the form when it is submitted.
            ui.output_text("output_add_name"),
            ui.output_text("output_add_phonenumber"),
            ui.output_text("output_add_email"),

            # 1c)
            ui.output_text("update_database_with_new_user")
        ),

        # Task 2: Database analysis

        # Make sure that the old tables and the following new ones are showing the updated view when the database changes.
        # When the panels consisting of these tables are reloaded after the database changes, the tables show the updated view

        # Keep the output cards from oblig 1 that show users’ names, bike status overview and the subscription overview
        ui.nav_panel("Name Users", 
            ui.output_table("User_Table")
        ),
        ui.nav_panel("Bike Names and Status", 
            ui.output_table("Bike_Table")
        ),
        ui.nav_panel("Subscription Types", 
            ui.output_table("Subscription_Table")
        ),

        # 2a) Add a text box and a button that filters the table users based on the user names
        ui.nav_panel("Filter Users",
            ui.input_text("filter_users", "Search user name:"),
            ui.input_action_button("search_user_submit_button", "Search User"),
            ui.output_table("users_filtered_table")
        ),

        # 2b) Produce a table that shows how many trips have ended on each station.
        ui.nav_panel("End Station Trips",
            ui.output_table("end_station_trips_table")
        ),

        # 2c) Provide a filterable station list with the names of the available bikes at each station. 
        #     One should be able to filter based on the station name and bike name.
        ui.nav_panel("Available Bikes",
            ui.input_text("avaiable_bikes", "Search bike name or station name:"),
            ui.input_action_button("search_avaiable_bikes_submit_button", "Search for avaiable bike"),
            ui.output_table("available_bikes_table")
        )

    )
)


##########          def server(input, output, session):          ##########

def server(input, output, session):

    # Task 1: Adding Users

        # 1b) Check the values that were submitted into the form for correctness.*
    
    @render.text # Connected to the ui.output_text part; displays the text
    @reactive.event(input.add_user_submit_button) # Makes sure the action only takes place when the action_button is clicked
    def output_add_name():

        #1b) *A valid name should only contain letters A-Å
        if (all(char.isalpha() or char.isspace() for char in input.add_name()) 
            and any(char.isalpha() for char in input.add_name())):
            status_name = "Valid"
        else:
            status_name = "Not Valid"

        """
        How ChatGPT was used for this part:
        Prompt: "How do you check if a name only consists of the letters A-Å?"
        Response: .isalpha()

        After testing the code, I noticed that writing two names in the text box resulted in "Not Valid"
        Prompt: I sent my code to and asked "How do you check if a name only consists of the letters A-Å and can consist of two names (have space)?"
        Response: all(char.isalpha() or char.isspace() for char in input.add_name())

        After testing this code, I noticed that only writing "space", will get "Valid".
        Prompt: "But it should not be valid if it ONLY contains spaces. How do I do that?
        Response: add: and any(char.isalpha() for char in input.add_name)
        Understanding: The code goes through all of the characters submitted in the text box and status become "Valid"" if all characters are letters or space,
        where at least one of the characters must be a letter.
        """

        # 1b) *Print, on the page, the input together with Valid or Not valid after the input on.
        return f"{input.add_name()} is {status_name}"
    
    @render.text
    @reactive.event(input.add_user_submit_button)
    def output_add_phonenumber():

        # 1b) A valid phone number should have exactly 8 digits.
        if len(list(input.add_phonenumber())) == 8:
            status_phonenumber = "Valid"
        else:
            status_phonenumber = "Not valid"

        # 1b) Print, on the page, the input together with Valid or Not valid after the input on.
        return f"{input.add_phonenumber()} is {status_phonenumber}"
    
    @render.text
    @reactive.event(input.add_user_submit_button)
    def output_add_email():

        # 1b) *A valid email should contain an @-sign.
        if "@" in input.add_email():
            status_email = "Valid"
        else:
            status_email = "Not Valid"

        # 1b) Print, on the page, the input together with Valid or Not valid after the input on.
        return f"{input.add_email()} is {status_email}"
    

        # 1c) Update your database design. Add email as an attribute to the User entity. 
        """
        This part only needs to be done once.
        Therefore I did this part directly in the terminal by writing:
        ALTER TABLE User ADD COLUMN Email_User;
        """

    # 1c) If you received valid input from the form, update the database with the new user.
    @render.text
    @reactive.event(input.add_user_submit_button)
    def update_database_with_new_user():
        if (all(char.isalpha() or char.isspace() for char in input.add_name()) 
        and any(char.isalpha() for char in input.add_name()) 
        and len(list(input.add_phonenumber())) == 8 
        and "@" in input.add_email()
        ):
            with sqlite3.connect("bysykkel.db") as con:
                con.execute(
                    """INSERT INTO User(Name_User, Phone_Number_User, Email_User) VALUES (?, ?, ?)""", 
                    (input.add_name(), input.add_phonenumber(), input.add_email())
                )
                con.commit()
            return f"{input.add_name()} has been registered as a user" # Included to easier see if the database has been updated

        """
        Sources used for 1c):
        https://sqlite.org/lang_insert.html
        https://docs.python.org/3/library/sqlite3.html#tutorial
        ^(?,?,?) is used to prevent "SQL injection attacks"
        """
    

    # Task 2: Database analysis
    # Make sure that the old tables and the following new ones are showing the updated view when the database changes.
    """
    To do this I added the relevant action buttons to the @reactive.event()
    """

    # Keep the output cards from oblig 1 that show users’ names, bike status overview and the subscription overview
   
    # Oblig 1(a): A table of the users’ names, sorted in alphabetical order.
    @output
    @render.table
    def User_Table():
        query = """
        SELECT Name_User
        FROM User
        ORDER BY Name_User;
        """
        return get_data(query)

    # Oblig 1(b): A table of the bike names together with their status.
    @output
    @render.table
    def Bike_Table():
        query = """
        SELECT Name_Bike, Current_Status_Bike
        FROM Bike;
        """
        return get_data(query)

    # Oblig 1(c): A table containing the number of times each subscription type was purchased.
    @output
    @render.table
    def Subscription_Table():
        query = """
        SELECT Type_Subscription, COUNT(*) AS Purchased
        FROM Subscription
        GROUP BY Type_Subscription;
        """
        return get_data(query)
    
    # 2a) Add a text box and a button that filters the table users based on the user names
    @output # må jeg ha denne med???
    @render.table
    @reactive.event(input.search_user_submit_button)
    def users_filtered_table():
        query = f"""
        SELECT ID_user AS user_id,
        Name_User AS Name,
        Phone_Number_User AS "Phone Number"
        FROM User
        WHERE Name_User LIKE ?
        """
        return get_data(query, [f"%{input.filter_users()}%"])

    """
    How ChatGPT was used for this part:
    Prompt: After making this function with input.filter_users() directly after the query, the table would not be displayed in the application. 
    Therefore I sent my code to ChatGPT and asked why it did not work.
    Response: ChatGPT explained that the issue was due to how pandas.read_sql() handles parameterized queries. 
    It suggested modifying the get_data() function to accept a second argument for parameters (params), 
    and to move the input.filter_users() to the return part. 
    Understanding: It is important to use placeholders (?) in queries to prevent users of the application to be able to write directly in you database, and change things. 
    With the help of Chat.GTP I now know how to do this using parameterized queries.
    """

    # 2b) Query the bysykkel database and produce a table that shows how many trips have ended on each station. 
    #     The table should consist of 3 columns. The station ID, the name of the station and the number of trips that have ended on that station.
    @output
    @render.table
    def end_station_trips_table():
        query = """
        SELECT Trip.ID_End_Station AS station_id,
        Station.Name_Station AS Name,
        COUNT(*) AS "Number of trips"
        FROM Trip
        JOIN Station ON Trip.ID_End_Station = Station.ID_Station
        GROUP BY Trip.ID_End_Station, Station.Name_Station;
        """
        return get_data(query)
    
    # 2c) Provide a filterable station list with the names of the available bikes at each station. 
    #     One should be able to filter based on the station name and bike name.
    @output
    @render.table
    @reactive.event(input.search_avaiable_bikes_submit_button)
    def available_bikes_table():
        query = """
        SELECT Station.Name_Station,
        Bike.Name_Bike
        FROM Bike
        JOIN Station ON Bike.ID_Station = Station.ID_Station
        WHERE (Name_Station LIKE ? 
        OR Name_Bike LIKE ?)
        AND Bike.Current_Status_Bike = "Parked";     
        """
        return get_data(query, [f"%{input.avaiable_bikes()}%", f"%{input.avaiable_bikes()}%"])
    

app = App(app_ui, server)

