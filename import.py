# TODO
"""write a program that will take the books and import them into your PostgreSQL database. 
You will first need to decide what table(s) to create, what columns those tables should have, and how they should relate to one another."""
#CS50 library has the SQL function which allows execution of sql queries
from cs50 import SQL

# The csv module implements classes to read and write tabular data in CSV format
import csv

reader = csv.DictReader(open(sys.argv[1], 'r')) #Openinig the csv file in read mode and assigning to reader object

    db = SQL("sqlite:///students.db") # This allows sqlite3 queries to be executed on students.db

    db.execute("DELETE from students") #for deleting any existing data in the table

    for row in reader: #accessing every row in reader object

        #splitting the single name into first, middle and last and storing in a list called split_name
        split_name = row["name"].split(" ")

        first = split_name[0] # Assigning the first value in list to variable 'first'

        # Assigning the other 2 values in list to variables 'mioddle' and 'last' respectively
        if len(split_name) > 2: # to check if there's a middle name
            middle = split_name[1]
            last = split_name[2]
        else: # Else condition is applied if there's no middle name
            middle = None
            last = split_name[1]

        # for storing all the 3 name variables and house, birth into students table
        db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)", first, middle, last, row["house"], row["birth"])

else: ##error message if 3 command line arguments are not entered
    print("Usage: python import.py characters.csv")