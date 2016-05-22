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

#May 19th Log:
I didn't do a thing today. We had a fieldtrip and 2 hours to do our work... I also had advising. Didn't do a thing, nope. I know tomorrow will be even more limited time, so I might try again tonight.

#May 20th Log:
I thought I'd be done with my minimum viable product but I am not and that's mainly because there has been fieldtrips and very little time to work on it. I am also stuck on getting a JS object sent over to flask so that I could manipulate that data in python.

Today I learned about `git cherry-pick` because I accidentally pushed a commit to my master branch that had broken code. I'll try to do my work tonight and hope I will reach my MVP by Monday. My mentor had told me to redo my entire thing, which also made me spin my wheels until late in the night last night. It wasn't until in the morning I realized that's not a good idea until I get the main idea down: A safest possible route generated (even if it takes 5 minutes to load it). Tonight since it is highly likely I won't be able to solve the JS to Python thing, I will use the gmaps module in python to get the directions (which is the same exact data I'm retrieving from the JS end) and see if I could find what legs of the route overlaps what block(s) of the boundary.

#May 21st Log:
I spoke to a friend and I may be back on track. I'm attempting to use PostGIS now because it may seem easier and I won't be in the woods. I got help as to how I shouldn't worry about the best way but a way that works. I made a macro in VIM to alter my 1.1mil entries csv to ensure that my latitude and longitude are a geometry(point()) type and also forced in the latitude and longitude columns (type decimal).

I didn't know what type geohashes are, so today I learned about `pg_typeof()` from postgres documentation. It is the same as use typeof() in JavaScript or type() in python when you want to know the type of something. I thought this was great to share. It can be used like this: 

`SELECT pg_typeof("stu_id"), pg_typeof(100) from student_details limit 1;`

I also learned about this to convert my geometry(point((lat,lng))) into geohashes and insert them into my geohash column:

`UPDATE crime_data_nyc
SET geohash=(ST_GeoHash(location, 7));`

I also created an extra table that holds in all of the geohashes and the total number of crimes associated with that geohash.

```
CREATE TABLE nyc_crimes_by_geohash (
	id SERIAL PRIMARY KEY NOT NULL,
	geohash TEXT,
	total_crimes INTEGER,
	crime_index DECIMAL
);
```

Then did to load the database with all of the geohashes based on the crime locations

```
INSERT INTO nyc_crimes_by_geohash (geohash) 
SELECT distinct(geohash)
FROM crime_data_nyc;
```
Or as a better alternative:

```
INSERT INTO nyc_crimes_by_geohash (geohash, total_crimes) 
SELECT distinct(geohash), count(crime_id)
FROM crime_data_nyc GROUP BY geohash;
```

To get the top 5 geohashes with the highest number of crimes in all of nyc:

```
SELECT COUNT(crime_id) AS crime_count, geohash
FROM crime_data_nyc
GROUP BY geohash
ORDER BY crime_count
DESC LIMIT 5;
 crime_count | geohash 
-------------+---------
        3344 | hfugp69
        3123 | hfuum9q
        1523 | hfv59yx
        1464 | hfv58jz
        1400 | hfug5m4
```
A better table that shows the boroughs:

```
    borough    | crime_count | geohash 
---------------+-------------+---------
 MANHATTAN     |        3344 | hfugp69
 QUEENS        |        3123 | hfuum9q
 BRONX         |        1523 | hfv59yx
 BROOKLYN      |        1400 | hfug5m4
 BRONX         |        1271 | hfv58jz
 ```
 
The crime_count totals up all of the crimes in that one geohash. The geohash column is self-explanatory, it holds the grid on planet earth (associated with NYC) that has the most frequent crimes based on the data.
That being said, geohash `hfugp69`'s crime count of `3344` is what I should normalize everything against.

Then I found a great resource on visualizing sql joins [Coding horror visual explanation of SQL Joins](https://blog.codinghorror.com/a-visual-explanation-of-sql-joins/) and a [good link that reviews the database relationships](http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html)

```
SELECT nyc_crimes_by_geohash.id, nyc_crimes_by_geohash.geohash FROM nyc_crimes_by_geohash
INNER JOIN crime_data_nyc
ON nyc_crimes_by_geohash.geohash = crime_data_nyc.geohash;
```

My next attempt is to insert the total number of crimes by geohash into the nyc_crimes_by_geohash table... This was my attempt and right now I assume it is working:

```
INSERT INTO nyc_crimes_by_geohash (geohash) (
	SELECT count(crime_id)                        
	FROM crime_data_nyc
	CROSS JOIN nyc_crimes_by_geohash
	WHERE nyc_crimes_by_geohash.geohash = 
	crime_data_nyc.geohash
	GROUP BY crime_data_nyc.geohash
);
```

And that doesn't work, let's break it down and this works:

```
SELECT count(crime_id)                        
FROM crime_data_nyc
CROSS JOIN nyc_crimes_by_geohash
WHERE nyc_crimes_by_geohash.geohash = 
crime_data_nyc.geohash
GROUP BY crime_data_nyc.geohash
ORDER BY count(crime_id) DESC;
```

And to verify that it works, I added the geohash columns from both tables into the query:

```
SELECT crime_data_nyc.geohash, nyc_crimes_by_geohash.geohash, count(crime_id)                        
FROM crime_data_nyc
CROSS JOIN nyc_crimes_by_geohash
WHERE nyc_crimes_by_geohash.geohash = 
crime_data_nyc.geohash
GROUP BY crime_data_nyc.geohash, nyc_crimes_by_geohash.geohash
ORDER BY count(crime_id) DESC;
```

I figured out how to get this to work with an insert statement.

`select (2)::decimal/total_crimes from nyc_crimes_by_geohash where id=18379;`

To insert into the total_crimes column the normalizer value, this is hard-coded:

```
UPDATE nyc_crimes_by_geohash
SET crime_index=(total_crimes)::decimal/(3344);
```

Then add a unique constraint to the geohash:

`ALTER TABLE nyc_crimes_by_geohash ADD CONSTRAINT geohash_constraint UNIQUE (geohash);`

Add a fkey relationship constraint to crime_data_nyc

`
ALTER TABLE crime_data_nyc ADD CONSTRAINT geohash_fkey FOREIGN KEY (geohash) REFERENCES nyc_crimes_by_geohash (geohash);
`