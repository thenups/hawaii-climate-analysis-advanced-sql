# Dependencies
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    """List all available api routes."""
    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/start/end<br/>'
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return the dates and temperature observations from the last year"""
    # Query for the dates and precipitation from the last year.
    results = session.query(Measurement).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of allDates
    allDates = []

    for date in results:
        dateDict = {}
        dateDict[date.date] = date.prcp
        allDates.append(dateDict)

    # Return the json representation of your dictionary
    return jsonify(allDates)


@app.route('/api/v1.0/stations')
def stations():
    """Return a json list of stations from the dataset"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    allStations = list(np.ravel(results))

    # Return a json list of stations from the dataset
    return jsonify(allStations)


@app.route('/api/v1.0/tobs')
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    # Query for the dates and temperature observations from the last year
    # Latest Date in data
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastDateTime = datetime.strptime(lastDate[0],'%Y-%m-%d')

    # Calculate the date 1 year ago
    oneYearAgoDate = datetime.date(lastDateTime) - dt.timedelta(days=365)

    # Select tobs data
    sel = [
            Measurement.date,
            Measurement.tobs
          ]

    # Query data from database and filter for last year
    results = session.query(*sel).\
        filter(Measurement.date < lastDateTime, Measurement.date > oneYearAgoDate).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of allDates
    dictList = []

    for result in results:
            dateDict = {}
            dateDict[result[0]] = result[1]
            allDates.append(dictList)

    # Return the json representation of your dictionary
    return jsonify(l)

@app.route('/api/v1.0/start/<start>')
def tempSummary(start,end):

    s = datetime.strptime(start,'%Y-%m-%d')

    try:
        e = datetime.strptime(end,'%Y-%m-%d')
        endDate = True
    except NameError:
        pass

    # Select data
    sel = [
            Measurement.date,
            func.avg(Measurement.tobs),
            func.min(Measurement.tobs),
            func.max(Measurement.tobs)
          ]

    if endDate == True:
        results = session.query(*sel).\
            filter(Measurement.date >= s, Measurement.date <= e).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
    else:
        results = session.query(*sel).\
            filter(Measurement.date >= s).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of allDates
    dictList = []

    for result in results:
            dateDict = {}
            dateDict['date'] = result[0]
            dateDict['tAvg'] = result[1]
            dateDict['tMin'] = result[2]
            dateDict['tMax'] = result[3]
            dictList.append(dateDict)

    return jsonify(dictList)

if __name__ == '__main__':
    app.run(debug=True)
