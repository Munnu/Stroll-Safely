from model import Crime_Data_NYC, connect_to_db, db, init_app

init_app()


def insert_lat_lng_values():
    # get all of the crimes, this is going to be a while, over 1 million records
    batch_size = 2000  # how many batches of data we will do this insertion per cycle

    # some raw sql to get the total number of entries in the database
    number_of_rows = db.engine.execute("select count(*) from crime_data_nyc").fetchone()[0]

    for n in range(number_of_rows/batch_size + 1):
        print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n BEGIN!"
        all_the_crimes = Crime_Data_NYC.query.filter_by(latitude=None).offset(n).limit(batch_size).all()

        print "\n\n\n\n this is the length of all of the crimes in the db", len(all_the_crimes)

        for crime in all_the_crimes:
            # do some string manipulation from the location column to put into
            # the latitude and longitude column
            crime_location = crime.location
            print "This is crime_location", crime_location

            # string magic here
            location = crime_location[1:-1].split(",")

            print "This is location", location
            location_lat = float(location[0].strip())
            location_lng = float(location[1].strip())

            crime.latitude = location_lat  # put that into the latitude column
            crime.longitude = location_lng  # now put that into the longitude column

            # commit those changes
            db.session.commit()

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."