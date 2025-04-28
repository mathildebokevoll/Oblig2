from shiny import App, ui, render, reactive
import pandas as pd
import sqlite3

def get_data(query, params=None):
    with sqlite3.connect("bysykkel.db") as con:
        return pd.read_sql(query, con, params=params)
    

# Make sure that the old tables and the following new ones are showing the updated view when the database changes.
    


##########          app_ui          ##########

app_ui = ui.page_fluid(
    ui.navset_tab(

        # Task 2:

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

    # Task 2:
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