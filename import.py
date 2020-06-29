# The csv module implements classes to read and write tabular data in CSV format
import csv

import os

from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker

# database engine object from SQLAlchemy that manages connections to the database
# os.getenv() method in Python returns the value of the environment variable key if it exists otherwise returns the default value.
engine = create_engine(os.getenv("DATABASE_URL"))

# create a 'scoped session' that ensures different users' interactions with the database are kept separate
db = scoped_session(sessionmaker(bind=engine)) #Picked from web

count = 0 #Enable if you wish to have the count of rows inserted

with open("books.csv", "r") as file: #using 'with' assuming that it's the safest option of opening a file 
    reader = csv.reader(file)
    next(file) #for skipping the title row from getting inserted into the table
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                {"isbn": isbn, 
                 "title": title,
                 "author": author,
                 "year": year})
        count += 1 #Enable if you wish to have the count of rows inserted

        print(f"Added book {title} to database.") #Visual for each row insertion

    db.commit() #Commit has been kept ouside the loop assuming it will lead to faster insert. (not sure)

print(count) #Enable if you wish to have the count of rows inserted
