# TODO
"""write a program that will take the books and import them into your PostgreSQL database. 
You will first need to decide what table(s) to create, what columns those tables should have, and how they should relate to one another."""
#CS50 library has the SQL function which allows execution of sql queries
from flask_sqlalchemy import SQLAlchemy

# The csv module implements classes to read and write tabular data in CSV format
import csv

reader = csv.DictReader(open(books.csv, 'r')) #Openinig the csv file in read mode and assigning to reader object

db = SQLAlchemy() # This allows sqlite3 queries to be executed on students.db

    #db.execute("DELETE from students") #for deleting any existing data in the table

for row in reader: #accessing every row in reader object
    print(row)

        # for storing all the 3 name variables and house, birth into students table
        #db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)", first, middle, last, row["house"], row["birth"])

