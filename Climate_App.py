
# Import Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
import datetime as dt
import numpy as np
from flask import Flask, jsonify

# Connect to sqlite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect hawaii database 
Base = automap_base()

# Reflect the tables from hawaii database
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.measurement

# Create flask app
app = Flask(__name__)

# Create homepage route and list available routes
@app.route("/")
def HomePage():
    """List all available routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
         )

# Return dictionary of all dates and precipitation values
@app.route("/api/v1.0/precipitation")
def Preciptitation():

    # Create session link
    session = Session(engine)

    # Query the database for date and prcp
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()
    
    # Set query data to dict then append to list
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)

    # Close session
    session.close()

    # Return jsonified list of dicts    
    return jsonify(prcp_list)    

# Return list of all stations in dataset
@app.route("/api/v1.0/stations")
def Stations():

    session = Session(engine)

    # Query stations data
    results = session.query(Station.station).all()

    # Append station to list if not in list already
    stations = []
    for station in results:
        if station not in stations:
            stations.append(station)

    session.close()

    return jsonify(stations)

# Return dictionaries of dates and temperature observations (tobs) from last year of data
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    # Query most recent date from dataset
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Find date one year before most recent date
    year_ago = (dt.datetime.strptime(most_recent[0],'%Y-%m-%d') \
                - dt.timedelta(days=365)).strftime('%Y-%m-%d')  

    # Query database for date and temp observations from last year
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.date >= year_ago).\
              order_by(Measurement.date).all()
    
    tobs_list = []

    # Create dicts of date and temp observations, append to list
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    session.close()

    return jsonify(tobs_list)

# Return temperature min, max and avg from specified start date till end of dataset
@app.route("/api/v1.0/<start>")
def Temp_Data(start):
    """Temperature Min, Max and AVG from specified starting date.

    Arguments:
        start (string): A date string in the format %Y-%m-%d

    Returns:
        Temperature Min, Max, AVG
    """

    session = Session(engine)

    returns = []

    # Query database for min, max and avg temp observation from
    # specified start date
    results = session.query(
                func.min(Measurement.tobs),\
                func.max(Measurement.tobs),\
                func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    # Create dict of temp data and specified start date
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict["Start Date"] = start
        tobs_dict["Temp Min"] = min
        tobs_dict["Temp Max"] = max
        tobs_dict["Temp AVG"] = avg
        returns.append(tobs_dict)

    session.close()

    return jsonify(returns)

# Return min, max and avg temperature from within specified date range
@app.route("/api/v1.0/<start>/<end>")
def Temp_Data2(start, end):
    """Temperature Min, Max and AVG for specified start and end dates.

    Arguments:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d

    Returns:
        Temperature Min, Max, AVG
    """

    session = Session(engine)

    returns2 = []

    # Same query as above but with specified end date
    results = session.query(
                func.min(Measurement.tobs),\
                func.max(Measurement.tobs),\
                func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    # Append temp data and start, end date to dict
    for min, max, avg in results:
        tobs2_dict = {}
        tobs2_dict["Start Date"] = start
        tobs2_dict["End Date"] = end
        tobs2_dict["Temp Min"] = min
        tobs2_dict["Temp Max"] = max
        tobs2_dict["Temp AVG"] = avg
        returns2.append(tobs2_dict)

    session.close()

    return jsonify(returns2)
        

# Run app in debug mode    
if __name__ == "__main__":
    app.run(debug=True)