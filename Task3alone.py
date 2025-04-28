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
                
                selected_bike_id_checkout= avaiable_bike_checkout[0] 
                selected_bike_name_checkout = avaiable_bike_checkout[1] 
                
                # 3a) Update the database accordingly.
                cur.execute(
                    """
                    UPDATE Bike
                    SET Current_Status_Bike = 'Active'
                    WHERE ID_Bike = ? 
                    """, (selected_bike_id_checkout,)
                )
                con.commit()
                
            return f"{input.selected_user()} has checked out {selected_bike_name_checkout } (ID {selected_bike_id_checkout}) from {input.selected_station()}"
        
        """
        How ChatGPT was used:
        Prompt: I sent my app_ui and output_checkout()function including the queries I hade made, and asked:
        "How do I select 1 bike from the dataset and use it in the other query?"
        Answer: You need to use cursor.execute(...).fetchone() to retrieve one available bike, and then store it in a variable.
        """
        
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

                con.commit()
                
            return f"{input.selected_user_dropoff()} has dropped off {selected_bike_name_dropoff} (ID {selected_bike_id_dropoff }) at {input.selected_station_dropoff()}"
                

         # 3c) Update the database according to the answers provided.     

        @output
        @render.text
        @reactive.event(input.complaint_submit_button)
        def output_complaint():
            with sqlite3.connect("bysykkel.db") as con:
                cur = con.cursor()

                bike_complaint = cur.execute(
                    """
                    SELECT ID_Bike
                    FROM Bike
                    WHERE Current_Status_Bike = 'Parked'
                    ORDER BY ID_Bike DESC
                    LIMIT 1;
                    """
                ).fetchone()

                if bike_complaint is None:
                    return "Could not find a recently dropped off bike."

                bike_id_complaint = bike_complaint[0]
                complaint = input.selectcomplaint()

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
                

           # """
           # How ChatGPT was used:
           # Prompt: I asked chat.gpt how to connect the complaint function to the bike that had just been dropped off.
           # Answer:
           # The lines I got from ChatGPT for this task is
           # """

# What I am missing in taskk 3 now:
# The bike that is checkes out is not connected to the user
# so it is not neceseruly that bike the use droppes off
# and the bike that has been dropped off is not connected to the one getting complaints
# This needs to be fixed by updating the whole databse i.e Trip table in a)
# and use this tabel for b and c

#^ gjør 4 først og så kommer jeg tilbake til dette!

    
app = App(app_ui, server)