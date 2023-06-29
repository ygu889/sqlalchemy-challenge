# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
#Create an app
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

#Query to retrieve only the last 12 months of data using date as the key and prcp as the value
# Calculate the date one year ago from the last date in the database
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year=dt.date(2017, 8, 23) - dt.timedelta(days=365)
    data=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=one_year).all()
    
 #Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_data= {date: prcp for date, prcp in data}
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
#Return a JSON list of stations from the dataset
 #query all the sation
   
    station=session.query(Station.station).all()
   
 #covert list of tuples into normal list
    all_station=list(np.ravel(station))
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most-active station for the previous year of data
    # Calculate the date one year ago from the last date in the database
    #query most active station
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year=dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station=session.query(Measurement.date,  Measurement.tobs).\
                            filter(Measurement.date >= one_year).\
                            filter(Measurement.station=='USC00519281').all()
    
    tobs_list = []
    for date, tobs in most_active_station:
        tobs_dict = {'date': date, 'tobs': tobs}
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start): # fetch the min, max, and average temperatures calculated from the given start date 
    
    start_date_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    #converts the result into dict of list
    temp_start_date=[]
    for rmin,ravg,rmax in start_date_data:
        temperature_dict = {'TMIN': rmin, 'TAVG': ravg, 'TMAX': rmax}
        temp_start_date.append(temperature_dict)
   
    
    # Return the JSON list of temperature data
    return jsonify(temp_start_date)

@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end): # fetch the min, max, and average temperatures calculated from the given start date and end date
   
    start_end_date = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
   
#convert the result into dict of list
    temp_start_end_date_data=[]
    for semin,seavg,semax in start_end_date:
        start_end_temperature_dict = {'TMIN': semin, 'TAVG': seavg, 'TMAX': semax}
        temp_start_end_date_data.append(start_end_temperature_dict)

    # Return the JSON list of temperature data
    return jsonify(temp_start_end_date_data)

if __name__ == '__main__':
    app.run(debug=True)







