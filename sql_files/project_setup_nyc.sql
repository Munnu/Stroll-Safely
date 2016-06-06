UPDATE crime_data_nyc
SET geohash=(ST_GeoHash(location, 7));


CREATE TABLE nyc_crimes_by_geohash (
    id SERIAL PRIMARY KEY NOT NULL,
    geohash TEXT,
    total_crimes INTEGER,
    crime_index DECIMAL
);

INSERT INTO nyc_crimes_by_geohash (geohash, total_crimes) 
SELECT distinct(geohash), count(crime_id)
FROM crime_data_nyc GROUP BY geohash;

SELECT nyc_crimes_by_geohash.id, nyc_crimes_by_geohash.geohash 
FROM nyc_crimes_by_geohash
INNER JOIN crime_data_nyc
ON nyc_crimes_by_geohash.geohash = crime_data_nyc.geohash;

INSERT INTO nyc_crimes_by_geohash (geohash) (
    SELECT count(crime_id)                        
    FROM crime_data_nyc
    CROSS JOIN nyc_crimes_by_geohash
    WHERE nyc_crimes_by_geohash.geohash = 
    crime_data_nyc.geohash
    GROUP BY crime_data_nyc.geohash
);

UPDATE nyc_crimes_by_geohash
SET crime_index=(total_crimes)::decimal/(3344);

ALTER TABLE nyc_crimes_by_geohash 
ADD CONSTRAINT geohash_constraint UNIQUE (geohash);


ALTER TABLE crime_data_nyc 
ADD CONSTRAINT geohash_fkey 
FOREIGN KEY (geohash) REFERENCES nyc_crimes_by_geohash (geohash);