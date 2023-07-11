# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
#Create an instance of Flask
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define the homepage route
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

#################################################
# Flask Routes
#################################################
# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the most recent date in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp) \
                     .filter(Measurement.date >= one_year_ago) \
                     .all()

    # Create a dictionary with date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations
    results = session.query(Station.station).all()

    # Convert the list of tuples to a list
    station_list = list(np.ravel(results))

    return jsonify(station_list)

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the most recent date in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

   # Query the most active station
    most_active_station = session.query(Measurement.station) \
                                 .group_by(Measurement.station) \
                                 .order_by(func.count(Measurement.station).desc()) \
                                 .first()[0]

    # Query the temperature observations for the last 12 months for the most active station
    results = session.query(Measurement.date, Measurement.tobs) \
                     .filter(Measurement.station == most_active_station) \
                     .filter(Measurement.date >= one_year_ago) \
                     .all()

    # Create a list of temperature observations
    temperature_list = list(np.ravel(results))

    return jsonify(temperature_list)

# Define the start and start-end range route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    # Query the minimum, average, and maximum temperature for the specified date range
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
                         .filter(Measurement.date >= start) \
                         .filter(Measurement.date <= end) \
                         .all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
                         .filter(Measurement.date >= start) \
                         .all()

    # Create a dictionary with temperature statistics
    temperature_stats = {
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    return jsonify(temperature_stats)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)