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

        # Task 4: Mapping

        ui.nav_panel("Mapping",
            # Create a selector (input selectize in Shiny) where you can choose one of the stations. 
            ui.input_selectize("select_station_for_availability", "Select station:",
                               get_data("SELECT Name_Station FROM Station;")["Name_Station"].tolist()),
                               
            
            # Next to the selector you should have a switch which represents if the trip is in progress or not.
            ui.input_switch("progress_switch", "Submit"),

            # When a station is chosen display a table where the first column is the station name and the second column is the availability.
            ui.output_table("availability_table")
        ),
    )            
)





##########          def server(input, output, session):          ##########

def server(input, output, session):

    # Task 4: Mapping

    @output
    @render.table(links=True, escape=False)
    @reactive.event(input.progress_switch())
    def availability_table():
        # When a station is chosen display a table where the first column is the station name and the second column is the availability.
        # The last column should be a link to the location of the station represented by a link to Openstreetmap using the latitude and longitude attributes of the station table.
        
        query = """
        SELECT Station.Station_Name AS Name,

        """

        return get_data(query,[f"%{input.select_station_for_availability()}%", ] )

    
    # The availability of a station should be represented as a percentage of the maximum spots at that station. 
    # If the trip is in progress, then the availability is the percentage of spots that are available at a station. 
    # If the trip is not in progress, then we assume that each non-available spot is occupied by a
    # bike that can be rented and availability is the percentage of non-available at a station.

    def calculate_availability():
        with sqlite3.connect("bysykkel.db") as con:
            cur = con.cursor()
        availability_station = cur.execute(
                """
                SELECT Maximum_Parking_Spots_Station, Avaiable_Parking_Spots_Station
                FROM Station
                WHERE Name_Station = ? 
                LIMIT 1;     
                """, (input.select_station_for_availability(),)
                ).fetchone()

        max_parking_spots = availability_station[0] 
        ava_parking_spots = availability_station[1] 

        if input.progress_switch():
            return (ava_parking_spots/max_parking_spots)*100 # Trip in progress
        else:
            return 100 - (ava_parking_spots/max_parking_spots)*100
        
       
    # The last column should be a link to the location of the station represented by a link to Openstreetmap 
    # using the latitude and longitude attributes of the station table.
    def location():
        with sqlite3.connect("bysykkel.db") as con:
            cur = con.cursor()
        
        location_station = cur.execute(
            """
            SELECT Latitude_Station, Longitude_Station
            FROM Station
            WHERE Name_Station = ?
            LIMIT 1;
            """, (input.select_station_for_availability(),)
        ).fetchone()

        LATITUDE = location_station[0]
        LONGITUDE = location_station[0]
        
        return f"""<a href="https://www.openstreetmap.org/#map=17/LATITUDE/LONGITUDE">Map</a>"""


app = App(app_ui, server)