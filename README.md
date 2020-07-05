## Project 1 - Web Programming with Python and JavaScript

## Overview:

In this project, you’ll build a book review website. Users will be able to register for your website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. You’ll also use the a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users will be able to query for book details and book reviews programmatically via your website’s API.

## Languages and Frameworks used.

- Python 3.8
- HTML5
- PostgreSQL
- Flask
- Jinja2
- CSS
- Bootstrap

## Basics Summary.

1. `Python` programs would be used for the back-end.
2. `Flask` framework would be used for creating `views`, `decorators`, etc
3. `HTML5` would be used to build the front-end interface (webpage) for the user to enter/view relevant details.
4. `Bootstrap` would be used along with `CSS` to make the webpage look nicer and user friendly.
5. All data entered through the webpage or even needed for the webpage management would be stored in a `PostgreSQL` DB and accessed using the Python programs. 
6. The database would be hosted by Heroku, an online web hosting service.
7. `Jinja2` would be used for writing logics within the HTML webpages. For adding conditions, placeholders and stuff. 
8. API's for this project would be in `JSON` format.

## Tables Used

- books     : Stores the details extracted from `books.csv`
- users     : Stores the user credentials
- reviews   : Stores the reviews submitted by users. 

## Python Programs

- Import.py             - For reading the data from csv file and loading into database.
- login_decorator.py    - This is used to create a @login_required decorator.
- application.py        - holds the main application logic for all the views.

## HTML Templates

- layout.html   - This holds the common webpage layout that would be extended across the entire application.
- home.html     - Page for searching the books.
- login.html    - Login page.
- register.html - Page for new users to register.
- error.html    - Common error message page.
- results.html  - Displays the book search results in a card format.
- reviews.html  - Provides option for the user to enter the review, ratings and submitting it.

## Static files
- style.css - Holds all the style elements.

For more details of how I did this click on my notion page link.
https://www.notion.so/How-I-did-it-0810ef2b8e594d2b8f4f91c42d13abca

