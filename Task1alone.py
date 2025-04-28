# INF115 Databases and Modelling
# Obligatory Assignment 2

from shiny import App, ui, render, reactive
import pandas as pd
import sqlite3

def get_data(query):
    with sqlite3.connect("bysykkel.db") as con:
        return pd.read_sql(query, con)
    
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

        # Task 2:

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
            return f"{input.add_name()} has been registered as a user" # Included to easer see if the databse has been updated

        """
        Sources used for 1c):
        https://sqlite.org/lang_insert.html
        https://docs.python.org/3/library/sqlite3.html#tutorial
        ^(?,?,?) is used to prevent "SQL injection attacks"
        """
    
app = App(app_ui, server)