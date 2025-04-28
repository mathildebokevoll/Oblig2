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

    @output
    @render.table(render_links=True, escape=False)
    @reactive.event(input.select_station_for_availability, input.progress_switch)  # Ikke på switch, men på valg av stasjon

    def availability_table():
        station_name = input.select_station_for_availability()

        query = """
            SELECT Name_Station, Maximum_Parking_Spots_Station, Avaiable_Parking_Spots_Station,
                   Latitude_Station, Longitude_Station
            FROM Station
            WHERE Name_Station = ?
            LIMIT 1;
        """

        data = get_data(query, params=(station_name,))

        if data.empty:
            return pd.DataFrame({"Station": [], "Availability (%)": [], "Map": []})
        
        max_spots = data["Maximum_Parking_Spots_Station"].iloc[0]
        available_spots = data["Avaiable_Parking_Spots_Station"].iloc[0]

        if available_spots in ['', None] or max_spots in ['', None]:
            return pd.DataFrame({"Station": [], "Availability (%)": [], "Map": []})

        # Kalkuler availability
        if input.progress_switch():
            availability = (available_spots / max_spots) * 100  # Trip in progress
        else:
            availability = (1 - float(available_spots) / float(max_spots)) * 100  # Trip not in progress

        # Lag link
        latitude = data["Latitude_Station"].iloc[0]
        longitude = data["Longitude_Station"].iloc[0]
    

        # Lag tabellen
        result = pd.DataFrame({
            "Station": [station_name],
            "Availability (%)": [f"{availability:.1f}%"],
            "Map": [f'<a href="https://www.openstreetmap.org/#map=17/{latitude}/{longitude}" target="_blank">Map</a>']
        })

        return result
    



#orginal     # Task 4: Mapping
#orginal 
#orginal     @output
#orginal     @render.table(render_links=True, escape=False)
#orginal     @reactive.event(input.progress_switch())
#orginal     def availability_table():
#orginal         # When a station is chosen display a table where the first column is the station name and the second column is the availability.
#orginal         # The last column should be a link to the location of the station represented by a link to Openstreetmap using the latitude and longitude attributes of the station table.
#orginal         
#orginal         query = """
#orginal         SELECT Station.Station_Name AS Name,
#orginal 
#orginal         """
#orginal 
#orginal         return get_data(query,[f"%{input.select_station_for_availability()}%", ] )
#orginal 
#orginal     
#orginal     # The availability of a station should be represented as a percentage of the maximum spots at that station. 
#orginal     # If the trip is in progress, then the availability is the percentage of spots that are available at a station. 
#orginal     # If the trip is not in progress, then we assume that each non-available spot is occupied by a
#orginal     # bike that can be rented and availability is the percentage of non-available at a station.
#orginal 
#orginal     def calculate_availability():
#orginal         with sqlite3.connect("bysykkel.db") as con:
#orginal             cur = con.cursor()
#orginal         availability_station = cur.execute(
#orginal                 """
#orginal                 SELECT Maximum_Parking_Spots_Station, Avaiable_Parking_Spots_Station
#orginal                 FROM Station
#orginal                 WHERE Name_Station = ? 
#orginal                 LIMIT 1;     
#orginal                 """, (input.select_station_for_availability(),)
#orginal                 ).fetchone()
#orginal 
#orginal         max_parking_spots = availability_station[0] 
#orginal         ava_parking_spots = availability_station[1] 
#orginal 
#orginal         if input.progress_switch():
#orginal             return (ava_parking_spots/max_parking_spots)*100 # Trip in progress
#orginal         else:
#orginal             return 100 - (ava_parking_spots/max_parking_spots)*100
#orginal         
#orginal        
#orginal     # The last column should be a link to the location of the station represented by a link to Openstreetmap 
#orginal     # using the latitude and longitude attributes of the station table.
#orginal     def location():
#orginal         with sqlite3.connect("bysykkel.db") as con:
#orginal             cur = con.cursor()
#orginal         
#orginal         location_station = cur.execute(
#orginal             """
#orginal             SELECT Latitude_Station, Longitude_Station
#orginal             FROM Station
#orginal             WHERE Name_Station = ?
#orginal             LIMIT 1;
#orginal             """, (input.select_station_for_availability(),)
#orginal         ).fetchone()
#orginal 
#orginal         LATITUDE = location_station[0]
#orginal         LONGITUDE = location_station[1]
#orginal         
#orginal         return f"""<a href="https://www.openstreetmap.org/#map=17/{LATITUDE}/{LONGITUDE}">Map</a>"""
#orginal     
#orginal # What I am missing in task 4 now:
#orginal # I have made the structure/principles, but I have not connected the code to make all of the parts work together
#orginal # This is something I have not prioritized using time to fix, but I hope my awareness of the problem/technique counts for the overall assessment


"""
"#original" is the starting point I made, and the rest is the result from prompting back and forth with ChatGPT

In addition, I have not prioritsed time to been able to update the Station table, so the Avaiability % will not change when the database/new bikes at different stations changes

"""
app = App(app_ui, server)