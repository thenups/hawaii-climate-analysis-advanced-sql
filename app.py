# Dependencies
import datetime as dt
import numpy as np
import pandas as pd
from datetime import datetime, date

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
        f'/api/v1.0/YYYY-MM-DD #start date<br/>'
        f'/api/v1.0/YYYY-MM-DD/YYYY-MM-DD #start/end dates<br/>'
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
        dateDict[str(date.date)] = date.prcp
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
    lastDate = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()

    # Calculate the date 1 year ago
    yearAgo = date((lastDate.date).year - 1, (lastDate.date).month, (lastDate.date).day)

    # Select tobs data
    sel = [
            Measurement.date,
            Measurement.tobs
          ]

    # Query data from database and filter for last year
    results = session.query(*sel).\
        filter(Measurement.date <= lastDate.date, Measurement.date > yearAgo).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of allDates
    dictList = []

    for result in results:
            dateDict = {}
            dateDict[str(result[0])] = result[1]
            dictList.append(dateDict)

    # Return the json representation of your dictionary
    return jsonify(dictList)


@app.route('/api/v1.0/<string:start>')
def tempSummaryStart(start):

    sdt = datetime.strptime(start,'%Y-%m-%d').date()
    print(sdt)

    # Select data
    sel = [
            Measurement.date,
            func.avg(Measurement.tobs),
            func.min(Measurement.tobs),
            func.max(Measurement.tobs)
          ]

    results = session.query(*sel).\
        filter(Measurement.date >= sdt).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of allDates
    dictList = []

    for result in results:
            dateDict = {}
            dateDict['date'] = str(result[0])
            dateDict['tAvg'] = result[1]
            dateDict['tMin'] = result[2]
            dateDict['tMax'] = result[3]
            dictList.append(dateDict)

    # Return the json representation of your dictionary
    return jsonify(dictList)

@app.route('/api/v1.0/<string:start>/<string:end>')
def tempSummaryStartEnd(start,end):

    sdt = datetime.strptime(start,'%Y-%m-%d').date()
    edt = datetime.strptime(end,'%Y-%m-%d').date()

    # Select data
    sel = [
            Measurement.date,
            func.avg(Measurement.tobs),
            func.min(Measurement.tobs),
            func.max(Measurement.tobs)
          ]

    results = session.query(*sel).\
        filter(Measurement.date >= sdt, Measurement.date <= edt).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of allDates
    dictList = []

    for result in results:
            dateDict = {}
            dateDict['date'] = str(result[0])
            dateDict['tAvg'] = result[1]
            dateDict['tMin'] = result[2]
            dateDict['tMax'] = result[3]
            dictList.append(dateDict)

    #  Return the json representation of your dictionary
    return jsonify(dictList)

if __name__ == '__main__':
    app.run(debug=True)
