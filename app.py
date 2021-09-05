import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    # Query 
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date > year_ago).all()

    session.close()

    # Create a dictionary from the row data and append to a list of percipitation
    percipitation = []
    for date, prcp in results:
        percipitation_dict = {}
        percipitation_dict["Date"] = date
        percipitation_dict["Percipitation"] = prcp
        percipitation.append(percipitation_dict)

    return jsonify(percipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(measurement.station).group_by(measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Query  the dates and temperature observations of the most active station for the last year of data.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    most_active = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active = most_active[0][0]

    results = session.query(measurement.tobs).filter(measurement.date > year_ago).filter(measurement.station == most_active).all()

    session.close()

    # Convert list of tuples into normal list
    observations = list(np.ravel(results))

    return jsonify(observations)


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range"""
    # Query all passengers
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.round(func.avg(measurement.tobs), 1)).filter(measurement.date > start).all()

    session.close()

    # Convert list of tuples into normal list
    observations = list(np.ravel(results))

    return jsonify(observations)


@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""
    # Query all passengers
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.round(func.avg(measurement.tobs), 1)).filter(measurement.date > start).filter(measurement.date < end).all()

    session.close()

    # Convert list of tuples into normal list
    observations = list(np.ravel(results))

    return jsonify(observations)


if __name__ == '__main__':
    app.run(debug=True)
