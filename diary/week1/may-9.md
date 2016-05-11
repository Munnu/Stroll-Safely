
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