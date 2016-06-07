# StrollSafely

### Special Thanks To
[NYC Resistor](http://nycr.us), [Miria Grunick](http://www.grunick.com/), also a fellow Resistor.

### Description
---
This project finds the safest possible route in NYC based on crimes provided by NYC Open Data via Google Maps. Based on a start and end location, the StrollSafely  geocodes the user's input, and uses Google API information to map out the steps in the route. The backend generates waypoints by interpolating and looking at which geohashes does the route fall under based on the NYC crime data. 

If the route falls on a high crime area, it checks other potential options against high crime areas and finds the safest route.

The map shows the original Google suggested route and then the adjusted safer route and dynamically renders heatmaps within the bounds of the route.

### Technologies Used
---
Flask, Python, PostgreSQL, PostGIS, HTML/CSS, JQuery, JavaScript, SQLAlchemy, Shapely, and the Google Maps API.

### Screenshots: Before and After
---
![image](progress_screenshots/waypoints_with_heatmap_before.png =500x)

![image](progress_screenshots/waypoints_with_heatmap_after.png =500x)

### Why Was This Made
---

A few months ago I met [Phoenix Perry](http://phoenixperry.com/). She told me about this interesting incident that had happened to her while travelling in France. She had inputted a route into Google Maps and it had routed her into a dangerous neighborhood. When she was at the red light (she was driving), someone had bashed into her glass and took out her purse in real time. When the police officer arrived, they had also admitted to having a similar incident happen to them not too far from where Phoenix' incident had happened.

I'm also living on the cusp of what is considered a dangerous neighborhood relative to the rest of San Francisco. I'm a very tiny individual and also very individualistic. I am also new to the area. I strongly dislike not being able to get to where I need to go be an impediment, especially when I'm officially in the heart of the city and may be walking around past sunset. What I became aware of is that there are some blocks that are more okay to travel through than others.

In the future, my code will work for San Francisco. I chose NYC because I am a NYC native and am more aware of which neighborhoods have what kind of stigma associated with it so it would be easier for me to verify information.

### Core Files
---
#### /

* ***application.py***
	* holds the flask routes
* ***model.py***
	* SQLAlchemy representation of the tables in PostgreSQL
* ***middle.py***
	* The most important file, it holds the brains of the application. It does the route manipulation and geocoding.

#### templates/
* ***main.html***
	* Holds the HTML form for the user's input and calls the JavaScript that talks to Flask. Holds Google Maps API library call.

#### static/
* ***main.js***
	* Sends/receives data to and from Flask. Also sends and receives data to and from Google Maps API. Handles user interface events.

* ***style.css***
	* Not that important, but it is the page styling, especially for the button.

### Setup Procedures
---
Okay, let's do this!

You will need to get your database set up. This project uses [PostgreSQL](https://www.postgresql.org/download/) and the PostGIS extension. You could also use the [Postgres.app](http://postgresapp.com/).

I also used [pgloader](http://pgloader.io/) SQLloader for Postgres. Here's the [pgloader github repo](https://github.com/dimitri/pgloader/blob/master/INSTALL.md) to load the CSV file so that if there are some bad data rows my table will still have entries. It also allows for inclusion/exclusion of whatever columns currently exist in the CSV.


1. Set up a database for Postgres in your terminal something like:

	```createdb crime_data_gis```

2. The next step is to connect into your Postgres database made in the previous step. Get [PostGIS extension set up](http://postgis.net/install/):
This project has the same exact file called ```postgis_init.sql``` inside of my ```sql_files``` folder.

	1. That being said you can do something like:
	```psql crime_data_gis < sql_files/postgis_init.sql```

	2. **Note:** To save you the trouble, some extensions may not work. In my case I was not able to successfully create the extension for postgis_sfcgal, address_standardizer, and address_standardizer_data_us. They are not necessary for this project.

3. Now you have to obtain the crime csv through [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/NYPD-7-Major-Felony-Incidents/hyij-8hr7). It was too large to put onto Github.
	1. Click on the Export button (as of June 2016, it's a light blue button around the top right section of the page)
	2. Then there is a **Download** dropdown. Expand that dropdown and under the Download As header, select CSV. It will take a minute or two to download.
	
4. You will need to modify the CSV to fit PostGIS and this current version of the project. Recording a VIM or Emacs macro (or whatever other tool that does the job) will work for this since there are over a million data entries and you don't want to modify each row by hand if there are millions of rows. After recording the macro, run the macro until the end of the file.
	1. I won't go over the way to do a [macro in VIM](http://vim.wikia.com/wiki/Macros) or how to use/access VIM through the terminal (unless someone asks). 
	2. In the CSV file it would be wise to add a Latitude and Longitude column and do a macro where all entries are populated with their Latitude and Longitude extracted from the Location column. The program currently relies on these two columns in addition to the Location column.
	3. You will also need to record and execute a macro for creating a `point` datatype for the entries in the Location column.
	4. Here is a snippet of what the end result of the csv file should look like:

	```
	OBJECTID,Identifier,Occurrence Date,Day of Week,Occurrence Month,Occurrence Day,Occurrence Year,Occurrence Hour,CompStat Month,CompStat Day,CompStat Year,Offense,Offense Classification,Sector,Precinct,Borough,Jurisdiction,XCoordinate,YCoordinate,Location, Latitude, Longitude
1,f070032d,09/06/1940 07:30:00 PM,Friday,Sep,6,1940,19,9,7,2010,BURGLARY,FELONY,D,66,BROOKLYN,N.Y. POLICE DEPT,987478,166141,point(40.6227027620001 -73.9883732929999),40.6227027620001,-73.9883732929999
2,c6245d4d,12/14/1968 12:20:00 AM,Saturday,Dec,14,1968,0,12,14,2008,GRAND LARCENY,FELONY,G,28,MANHATTAN,N.Y. POLICE DEPT,996470,232106,point(40.8037530600001 -73.955861904),40.8037530600001,-73.955861904
3,716dbc6f,10/30/1970 03:30:00 PM,Friday,Oct,30,1970,15,10,31,2008,BURGLARY,FELONY,H,84,BROOKLYN,N.Y. POLICE DEPT,986508,190249,point(40.688874254 -73.9918594329999),40.688874254,-73.9918594329999
4,638cd7b7,07/18/1972 11:00:00 PM,Tuesday,Jul,18,1972,23,7,19,2012,GRAND LARCENY OF MOTOR VEHICLE,FELONY,F,73,BROOKLYN,N.Y. POLICE DEPT,1005876,182440,point(40.6674141890001 -73.9220463899999),40.6674141890001,-73.9220463899999
5,6e410287,05/21/1987 12:01:00 AM,Thursday,May,21,1987,0,5,28,2009,GRAND LARCENY,FELONY,K,75,BROOKLYN,N.Y. POLICE DEPT,1017958,182266,point(40.6668988440001 -73.878495425),40.6668988440001,-73.878495425
	```

5. Now, let's use [pgloader to load the formatted CSV](http://pgloader.io/howto/csv.html) into Postgres.
	1. There is a file in this project: `csv_files/ny_with_gis_final_csv.load`.
	
		Run the pgloader load script by doing: `pgloader csv_files/ny_with_gis_final_csv.load`
	2. If there are any rows that don't conform to what Postgres is looking for, pgloader will continue to load the rows that adhere to the proper data type rules defined.

6. Also, dump the file `sql_files/project_setup_nyc.sql` into Postgres by doing `psql crime_data_gis < sql_files/project_setup_nyc.sql` (the same as what you did for creating the PostGIS extensions) once the crime data is loaded into the table. If interested, here is a somewhat incoherent excerpt from my [week2 progress diary entry](https://github.com/Munnu/Stroll-Safely/blob/master/diary/week2/may_16th_log.md) if things don't work out. If I missed something in my SQL, please let me know.

7. Don't forget to set up and activate your [virtual environment](https://virtualenv.pypa.io/en/stable/) if you have not. Once that's done, do a `pip install -r requirements.txt`.

8. To run the application, do `python application.py` or make it into an executable by changing the permissions. Whatever floats your boat. To see the application locally, go to [http://localhost:5000](http://localhost:5000)

**Now you should be set up!**