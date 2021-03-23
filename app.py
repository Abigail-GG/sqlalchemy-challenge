import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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

    # Query all precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #Define data
    recent_date = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > year_ago).\
        filter(Measurement.station == 'USC00519281' ).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of results in temperature
    temp_results = []
    for date, prcp in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["prcp"] = prcp
        temp_results.append(temp_dict)

    return jsonify(temp_results)

@app.route("/api/v1.0/<start>")
def start_date(start):

    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    sel = [Measurement.date,
       func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]
    data = session.query(*sel)
    for start_date in data:
        
        if Measurement.date == start_date or start_date < Measurement.date :
            return jsonify(data)

    return jsonify({"error": f"No results for date {start_date} not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):

    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    sel = [Measurement.date,
       func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]
    data = session.query(*sel)
    for start_date in data:
        
        if Measurement.date == start_date and Measurement.date <=  end_date :
            return jsonify(data)

    return jsonify({"error": f"No results for date range {start_date}/{end_date} not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)