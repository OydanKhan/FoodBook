# Lab_03_Group_3

## Project Overview:
Title: Foodbook\
Objectives: Create a social restaurant recommendation website that allows users to view and recommend restaurants as well as invite friends to restaurants.\
Main features: 
* View restaurants
* Like / dislike restaurants
* Save restaurants + view saved restaurants
* Friends - add / delete friends
* View friends liked restaurants
* Dine buddy invites - invite friends to restaurants
* Access profile + friend profiles

## Installation Instructions:
Once downloaded, navigate to the Lab_03_Group_03/foodbook directory.

Ensure you have python and pip installed.

Run “pip install -r requirements.txt”

Requirements.txt - include:
* Django
* Pillow
* django-axes
* django-allauth
* requests
* PyJWT
* cryptography
* jsonschema

Run "python manage.py migrate" <br>
Run "python manage.py shell" <br>
Run "from django.contrib.contenttypes.models import ContentType <br>
ContentType.objects.all().delete()" (dont paste as one line) <br>
Type "exit()"  <br>
Run "python manage.py loaddata data.json" <br><br>

This will set up the database schema, and then load the data into them.

## Configuration and Environment Setup: 
### To Configure Google Provider in Django Admin for Google OAuth 2.0 implementation
Add the Google Provider in Django Admin:\
Files that were used to configure the project:
* settings.py (foodbook/settings.py)


1. Start your Django development server: python manage.py runserver
2. Go to the Django Admin interface: http://127.0.0.1:8000/admin/.
3. Locate Sites and ensure your domain is configured correctly (e.g., 127.0.0.1:8000 or localhost:8000), if not, create a new site with the correct domain
4. Go to Social Applications and click Add:
- Provider: Choose Google.
- Name: Give it a name (e.g., Google OAuth).
- Client ID: Paste the Client ID from the .env file
- Secret Key: Paste the Client Secret from the .env file
- Sites: Select your site (127.0.0.1:8000 or the one you set up).
5. Save the Social Application.

## Usage Instructions: 
In your terminal, navigate to the Lab_03_Group_03/foodbook directory.\
Once in the directory, run “python manage.py runserver”.\
The terminal should output a localhost link “127.0.0.1:8000” - check you can see this.\
You can then control click to open the link in your default web browser, or you can manually type the link “127.0.0.1:8000” into the browser address bar.\
You should now be able to see the website in your browser.

Instructions for using the application.

### Client Front End for Database
The team also used DB Browser for SQLite website, you can easily download and use to explore the db.sqlite3 file.

1. Go to the DB Browser for SQLite website.
2. Download the installer for your operating system (Windows .exe, macOS .dmg).
3. Run the installer and follow the instructions.
4. After installation launch DB Browser for SQLite
5. Click "Open Database" and navigate to your db.sqlite3 file.
6. Explore database features using "Database Structure" tab
7. Use the "Browse Data" tab to view and edit table data.
8. Run SQL queries directly using the "Execute SQL" tab.


### Usage of SQLite CLI
1. Open a terminal and navigate to the project directory.
2. Run the following command: sqlite3 db.sqlite3
3. Use `.tables` to see the list of tables and `.schema <table_name>` to view table details.


## API Documentation:
Please look [here](API_DOCS.md) for API documentation. 

## Known Issues:
- When admin creates new restaurant, the upload image functionality doesnt work as inten

## Plan for Future Features
- Expandable Restaurant cards that show more restaurant information. 
- Include messages in Dine Buddy invites. 

## For registration:
Username: Admin
pass: foodbook


Username: Nira
pass: 9!XR5d.hBZ#!R!V

