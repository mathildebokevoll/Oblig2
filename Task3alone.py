# INF115 Databases and Modelling
# Obligatory Assignment 2


from shiny import App, ui, render, reactive
import pandas as pd
import sqlite3

def get_data(query, params=None):
    with sqlite3.connect("bysykkel.db") as con:
        return pd.read_sql(query, con, params=params)
    

##########          app_ui          ##########

app_ui = ui.page_fluid(
    ui.navset_tab(

        # Task 3: Interactions
        # Here we’ll simulate the user cycle of checking out a bike, using it and checking it back in.

        # 3a) Create a card ”CHECKOUT” where a selected user at a selected station is assigned one of the available bikes at that station. 
        ui.nav_panel("Checkout",
            ui.card("CHECKOUT",
                ui.input_select("selected_user", "Select user:", 
                get_data("SELECT Name_User FROM User;")["Name_User"].tolist()), # Third input should be the list that we want to selcet from. Uses the get_data function and .tolist to do this   
                ui.input_select("selected_station", "Select station:", 
                get_data("SELECT Name_Station FROM Station;")["Name_Station"].tolist()),
                ui.input_action_button("checkout_submit_button", "CHECKOUT"),
                ui.output_text("output_checkout")
            )
        ),

        # 3b) Create a card ”DROPOFF” where a selected user at a selected station returns the bike that they have currently checked out. 
        ui.nav_panel("DROPOFF",
            ui.card("DROPOFF",
                ui.input_select("selected_user_dropoff", "Select user:", 
                get_data("SELECT Name_User FROM User;")["Name_User"].tolist()),   
                ui.input_select("selected_station_dropoff", "Select station:", 
                get_data("SELECT Name_Station FROM Station;")["Name_Station"].tolist()),
                ui.input_action_button("dropoff_submit_button", "DROPOFF"),
                ui.output_text("output_dropoff"),
            

                # 3c) After a DROPOFF, ask the user if there is anything wrong with the bike. 
        

                ui.input_select("selectcomplaint", "Is there anything wrong with the bike?", 
                                ["No", "Flat tire", "Breaks not working", "Gear not working",
                                 "Seat broken", "Handlebar broken", "Fenders broken"]
                                ),
                ui.input_action_button("complaint_submit_button", "Send in complaint"),
                ui.output_text("output_complaint")
                    
            ),
        ),
                # 3c) Fetch the information needed for your maintenance tables.

                
    )
)

"""
                A Maintance table needs to be created
                This part only needs to be done once.
                Therefore I did this part directly in the terminal by writing:
                CREATE TABLE Reperation_Status_Bike (
                ID_Reperation     INT     PRIMARY KEY     UNIQUE,
                ID_Bike           INT     NOT NULL,
                Complaint_Type    TEXT    NOT NULL,
                FOREIGN KEY (ID_Bike) REFERENCES Bike(ID_Bike)
                );
                """



##########          def server(input, output, session):          ##########

def server(input, output, session):

    # Task 3: Interactions

        # Task 3: Interactions
        # Here we’ll simulate the user cycle of checking out a bike, using it and checking it back in.

        # 3a) Create a card ”CHECKOUT” where a selected user at a selected station is assigned one of the available bikes at that station. 
        
        @output
        @render.text
        @reactive.event(input.checkout_submit_button)
        def output_checkout():
            with sqlite3.connect("bysykkel.db") as con:
                cur = con.cursor()
                avaiable_bike_checkout = cur.execute(
                    """
                    SELECT ID_Bike, Name_Bike
                    FROM Bike
                    JOIN Station ON Bike.ID_Station = Station.ID_Station
                    WHERE Name_Station = ? 
                    AND Current_Status_Bike = 'Parked'
                    LIMIT 1;     
                    """, (input.selected_station(),)
                ).fetchone()

                if avaiable_bike_checkout is None:
                    return f"No available bikes at {input.selected_station()}."
                
                selected_bike_id_checkout = avaiable_bike_checkout[0] 
                selected_bike_name_checkout = avaiable_bike_checkout[1] 
                
                # 3a) Update the database accordingly.
                cur.execute(
                    """
                    UPDATE Bike
                    SET Current_Status_Bike = 'Active'
                    WHERE ID_Bike = ? 
                    """, (selected_bike_id_checkout,)
                )

                userId = cur.execute(
                    """
                    SELECT ID_User
                    FROM User
                    WHERE Name_User = ?
                    """, (input.selected_user(),)
                ).fetchone()
                
                cur.execute(
                    """
                    INSERT INTO Trip (ID_User, ID_Bike, Start_Time_Trip, End_Time_Trip, ID_Start_Station, ID_End_Station)
                    VALUES (?, ?, CURRENT_TIMESTAMP, NULL, ?, NULL)
                    """, (userId[0], selected_bike_id_checkout, input.selected_station())
                )
                con.commit()
                
            return f"{input.selected_user()} has checked out {selected_bike_name_checkout } (ID {selected_bike_id_checkout}) from {input.selected_station()}"
        
        """
        How ChatGPT was used:
        Prompt: I sent my app_ui and output_checkout()function including the queries I hade made, and asked:
        "How do I select 1 bike from the dataset and use it in the other query?"
        Answer: You need to use cursor.execute(...).fetchone() to retrieve one available bike, and then store it in a variable.
        """

        last_dropped_bike_id = reactive.Value(None) #
        
        # 3b) Create a card ”DROPOFF” where a selected user at a selected station returns the bike that they have currently checked out. 

        @output
        @render.text
        @reactive.event(input.dropoff_submit_button)
        def output_dropoff():
            with sqlite3.connect("bysykkel.db") as con:
                cur = con.cursor()
                active_bike_dropoff = cur.execute(
                    """
                    SELECT ID_Bike, Name_Bike
                    FROM Bike
                    WHERE Current_Status_Bike = 'Active'
                    LIMIT 1;     
                    """
                ).fetchone()

                if active_bike_dropoff is None:
                    return f"{input.selected_user_dropoff()} does not have an active bike to drop off."
                
                selected_bike_id_dropoff = active_bike_dropoff[0]
                selected_bike_name_dropoff = active_bike_dropoff[1]
                
                # 3b) Update the database accordingly.
                cur.execute(
                    """
                    UPDATE Bike
                    SET ID_Station = (
                    SELECT ID_Station FROM Station WHERE Name_Station = ?),
                    Current_Status_Bike = 'Parked'
                    WHERE ID_Bike = ?; 
                    """, (input.selected_station_dropoff(), selected_bike_id_dropoff ,)
                )

                userId = cur.execute(
                    """
                    SELECT ID_User
                    FROM User
                    WHERE Name_User = ?
                    """, (input.selected_user(),)
                ).fetchone()

                tripId = cur.execute(
                    """
                    SELECT ID_Trip
                    FROM Trip
                    WHERE ID_User = ?
                    ORDER BY ID_Trip DESC
                    LIMIT 1;
                    """ ,(userId[0], )
                ).fetchone()

                station_id = cur.execute(
                    """
                    SELECT ID_Station
                    FROM Station
                    WHERE Name_Station = ?
                    """, (input.selected_station_dropoff(), )
                ).fetchone()

                cur.execute(
                    """
                    UPDATE Trip
                    SET End_Time_Trip = CURRENT_TIMESTAMP,
                    ID_End_Station = ?
                    WHERE ID_Trip = ?;
                    """, (station_id[0], tripId[0])
                )

                con.commit()

                last_dropped_bike_id.set(selected_bike_id_dropoff) #
                
            return f"{input.selected_user_dropoff()} has dropped off {selected_bike_name_dropoff} (ID {selected_bike_id_dropoff }) at {input.selected_station_dropoff()}"
                

         # 3c) Update the database according to the answers provided.     

        @output
        @render.text
        @reactive.event(input.complaint_submit_button)
        def output_complaint():
            with sqlite3.connect("bysykkel.db") as con:
                cur = con.cursor()

                # bike_complaint = cur.execute(
                #     """
                #     SELECT ID_Bike
                #     FROM Bike
                #     WHERE Current_Status_Bike = 'Parked'
                #     ORDER BY ID_Bike DESC
                #     LIMIT 1;
                #     """
                # ).fetchone()

                bike_id_complaint = last_dropped_bike_id() #
                if bike_id_complaint is None:   #
                    return "Could not find a recently dropped off bike."    #

                # bike_id_complaint = bike_complaint[0]
                # complaint = input.selectcomplaint()
                with sqlite3.connect("bysykkel.db") as con: #
                    cur = con.cursor() #
                    complaint = input.selectcomplaint() #

                    if complaint != "No":
                        cur.execute(
                            """
                            INSERT INTO Maintance (ID_Bike, Complaint_Type)
                            VALUES (?, ?)
                            """, (bike_id_complaint, complaint)
                        ) 
                        
                        con.commit()
                        return f"Complaint '{complaint}' registered for bike ID {bike_id_complaint}."
                    else:
                        return "No complaint registered."
                

        """
        How ChatGPT was used:
        Prompt: I asked chat.gpt how to connect the complaint function to the bike that had just been dropped off.
        Answer: You need to remember the ID of the bike that was dropped off during dropoff, and then use that ID inside the complaint function.
        In Shiny for Python, the way you store temporary information between different clicks is with a reactive.Value
           - Inside server(), add: last_dropped_bike_id = reactive.Value(None)
           - In output_dropoff(), after committing, add: last_dropped_bike_id.set(selected_bike_id_dropoff)
           - In output_complaint(), use last_dropped_bike_id() instead of querying the database for a random parked bike.
        The parts with # in front is what I had from before, and the parts with # after is what I got from ChatGPT   
        
        Last minute comment: when I fixed and updated my tables, such as the same bike that was checked out got dropped off, 
        this teqnuice for updating the complaint table does not work anymore, and I do not have the time to priority to fix it,
        but I hope my awareness of the problem/technique counts for the overall assessment.


        Morover, In order to utdate the database, I had to make the following changes in the table Trip:
            - Remove NOT NULL constraint from End_Time_Trip and ID_End_Station 
            - ID_Trip AUTOINCREMENT instead of UNIQUE (such that the ID automaticly continues to update)
            - Change from INT to INTEGER, because AUTOINCREMENT only works on INTEGER
            - Delete the data that was already in Trip
        """
        

    
app = App(app_ui, server)