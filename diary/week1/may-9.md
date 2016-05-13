
#May 9th Log:

Today I started playing with the Google Maps API (directions). I started off with the tutorials on the API's website. I managed to figure out how to get two points on a screen, then I managed to figure out how to get a route between those two points.

I did get a little stuck because I was hung up over how to get my API key to work inside of my script tags in my HTML. I did not figure that part out, and apparently it is not necessary at this time (or ever).

I am glad that I figured out how to plot two points and get a route between the two. I do have a few questions:

1. WHat is response and status in JS land, response seems a little obscure to me especially regarding: `directionsDisplay.setDirections(response)`
2. How do I get a list of the route points/segments of the total route plotted?
3. How do I get the waypoints?
4. Is there any resource/guide that explains the API better without having to scour the entire Google Maps reference page?

In the mean time before my day ends, I will try to look into PostGIS which I heard will be helpful for storing geospacial data.

I will also look into SQL loader since it takes in CSV files and load them into databases. The data I found below limits the amount of data displayed in JSON which means that it would be best to store in a db since CSV reports crimes from even as old as the 40s (wow). 

Also, just in case these websites are down it is a good idea. 

1. [NYC Open Data: Crimes](https://data.cityofnewyork.us/Public-Safety/NYPD-7-Major-Felony-Incident-Map/dvh8-u7es)
2. [SF Open Data: Crimes](https://data.sfgov.org/Public-Safety/Map-Crime-Incidents-from-1-Jan-2003/gxxq-x39z)

# May 10th Log:

I forgot how much of my time is typically spent wrestling with environment stuff. Also, I forgot how bad SQL is at explaining errors. Not an easy thing to debug when the error messages are vague.
`Database error 42601: syntax error at or near "text"`
But, they're all type text for now! AUHIFWEOIFW ok. :|
5 minutes later: Heh, it was because I accidentally left a comma at the end of my sql table and column type association. Oh SQL... Or maybe not. Oh dear.

I figured it out, it was partially because vim duplicated a few columns a bunch of times. Some columns still had spaces instead of underscore: column_name. This caused the bugs.

I was able to load my data (though still need to read more on PostGIS). I changed the data types to not all be of type text as originally done to see if I could get pgloader to do something nice. I'm happy about my progress today despite having little time to work on my project (fieldtrip).

# May 11th Log:
I think I have not emphasized the struggle I always have with setting up environments. I failed to put in my first entry the matter of fact that I struggled to get pgloader and PostGIS on my computer properly (or so I had thought). It had come to my attention that PostGIS' inability to create certain extensions (believe it was sfcgal and decoder and decoder_us) would not have any bearing as to whether I could use the extension. It's totally useable. Because of this prior igorance, I had brew uninstalled my 9.4 postgresql to reinstall it... to install Postgresql.app (which has the latest Postgres 9.5.<something> and PostGIS 2.2) just to see that those same extensions had not been created.

pgloader was hilarious in a grim way... The only reason it ended up working on my mac is because I found a .pkg file and thought I had to do a make to get it to have it universally work. Nope... well, I don't know what the make is for (I know, shame on me) as much as I know that pgloader <name of my csv loader file>.load where the .load file is the example loader file from the docs modified. Whole lot better than trying to SQLAlchemy insert. The database is more than 1 GB and SQL is way more efficient in that respect.

Today one of my mentors had helped me to understand how to best go about learn about different modules or tools. They had showed me that they figure out how something works by going to their test docs and looking at what they're trying to accomplish through there. The unittest files are great for learning what the rules are because the rules are defined in those tests. How the method calls work and parameters are also demonstrated in this test file.

This helped me to better understand not only the API but also this other module called gmaps. Gmaps is the more current version of the googlemaps module.

#May 12th Log:
This was a frustrating wrestle with javascript/jquery just to realize why my plots were not showing up on the map happened to be because of a typo on the word 'longitude'. Today I managed to load up 3 arbitrary lat-long points onto google maps that display in addition to whatever route the user puts for Point A. Point B is hard-coded so far.

Hoping that I could easily do the sqlalchemy queries. I had to rename my sqlalchemy datatype of Point to text because it was not working well. Will figure that out later.

My plan by the end of this week is to be able to:

1. Have a bunch of crime locations to show up
2. A way that the user can input a lat, lng for Point A, Point B and have google maps dynamically generate a route.