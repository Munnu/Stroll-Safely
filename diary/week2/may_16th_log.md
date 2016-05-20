#May 16th Log:
I didn't feel like I did a lot but I did something. I tried to write a couple of flask tests today on certain endpoints. I have a tendency to get stuck in the weeds assuming there is a 'right' way to do something so then I end up reaching paralysis by overthinking. I was hung up on whether I needed to do a setUp and tearDown in my tests, specifically of creating a new table and populating the table. I used pgloader originally to load in all of the crime data so I thought I needed to do it a different way (assuming it would be a 'better way') by generating from the csv from python using sqlalchemy. I was told that if I used pgloader to load in the csv, do the same thing with the test data. That being said, the test data gets pre-loaded before the tests begin. The set up will not handle this part, it will just connect to the database.


I tried to do a little bit of the bounds creation. I haven't gotten to the point where I can display my top left and bottom right corners, but right now I am assuming they work. I am missing some sort of weird crucial piece as to generating that bound. I know that the only way for me to generate a bound is whenever there is a start and end address loaded into the map itself. Once I can think through that part and confirm that the top left and bottom right coords make sense, I'll definitely be on the right track.

#May 17th Log:
I forgot to do a log for today but I am writing this on the 18th. I have a tendency to be into the woods and think that there is a much better way to do things and then spin my wheels. It was suggested to me to use PostGIS but I don't think I have time to learn this new technology. I also spent a lot of time yesterday trying to figure out how to generate bounds. It was really simple. A matter of adding 0.01 or something to latitude and longitude values to create a buffer based on the latitude and longitude of the route generated. I knew that, but at the same time I thought it needed to be way more complex, that and I couldn't get my bounds to agree. I found out I had a slight typo somewhere. 

[This wiki resource on Decimal Degrees](https://en.wikipedia.org/wiki/Decimal_degrees) was helpful to me in order to understand how many decimal points equal to a block or two. I also recognized that my bounds can go beyond the size of the land itself and into the water because it is highly unlikely that I would have to route through water (is that even possible with google maps), or have a crime that's positioned in the water.

I also generated this script that is still running as I speak (On May 18th minutes to 1pm) that would decimalize the latitude and longitude into their separate columns. Right now in my table the location (latitude, longitude) is of type text. I wanted to use Point but that's a learning curve I don't have time for this week. I want to be able to finish up my algorithm. My entries are over 1.1 million in my database and since I'm using python to do string magic and populate these two columns, it's been taking hours to do.

What I need to do for the May 18th is to create a 2d array grid based on the latitude and longitude values and section them into N pieces, then find the crimes that fit inside of each block. Once I do that, one half of my algorithm will be complete.

#May 18th Log:
I don't know why but my brain went for a second lunch later today and I forgot how to implement a 2d array and had to noodle around in my python terminal. Oh the simple things in life.

So far as of 5pm I managed to create the 2d array to hold in what the latitude and longitude limit values are for each grid...?
Anyway, the next step is to input the number of crimes that are in that grid segment.
I notice when I do my query where I try to do something like
SELECT * FROM crime_data_nyc WHERE latitude BETWEEN <value> AND <value> AND longitude BETWEEN <value> AND <value> I am highly likely to return nothing for all of my entries. So I need to think through this part better... If I exclude the second BETWEEN ... AND I get way too many results (iirc via psql) to the magnitude of 2k+ results. Paused for a bit, I guess I need to do things bird by bird.