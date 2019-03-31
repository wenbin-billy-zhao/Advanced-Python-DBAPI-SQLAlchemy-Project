# For Flask Web App, These are imported dependencies and libraries
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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

## Home Page with all the links
@app.route("/")
def index():
       return """
              <html>
                     <head>Welcome to Advanced SQLAlchemy Magic Land!</head>
                     <body>
                            <h2>Surf Up! - Analysis of Hawaii Weather Data</h2>
                            <h4>In this analysis, we list several weather data set collected from Hawaii wether stations</h4>

                            <ul>
                                   <li>Date and Precipitation Result (12 Months): <br>
                                   <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
                                   <br><br>
                                   
                                   <li>List of Weather Stations: <br>
                                   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
                                   <br><br>
                                   
                                   <li>List of Observed Tempretures (TOBs) in last 12 Months:<br>
                                   <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
                                   <br><br>

                                   <li>Minimum, Maximum, Average Tempreture by Date:<br>
                                   <a href="/api/v1.0/2016-01-01">/api/v1.0/2016-01-01</a>
                                   <br><br>

                                   <li>Minimum, Maximum, Average Tempreture by Date Range:<br>
                                   <a href="/api/v1.0/2016-03-05/2016-03-20">/api/v1.0/2016-03-05/2016-03-20</a>
                                   <br><br>

                            </ul>
                     </body>
              </html>
       """

@app.route("/api/v1.0/precipitation")
def precipitation():
       session = Session(engine)
       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date = max_date[0]

       min_date = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366) 

       query_result = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= min_date).\
                order_by(Measurement.date).\
                all()

       precipitation_dict = dict(query_result)

       return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
       session = Session(engine)
       stations_query_result = session.query(Measurement.station).group_by(Measurement.station).all()
       stations_list = list(np.ravel(stations_query_result))  # np.ravel flattens the nested array into a simple list
       return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
       session = Session(engine)
       max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
       max_date = max_date[0]
       min_date = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
       
       tobs_query_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= min_date).all()
       return jsonify(tobs_query_result)

@app.route("/api/v1.0/<start>")
def start(start):
       session = Session(engine)

       start_query_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
       start_list = list(start_query_result)
       return jsonify(start_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def my_trip(start_date, end_date):
       session = Session(engine)
       trip_query_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
       trip_list = list(trip_query_result)
       return jsonify(trip_list)

if __name__ == "__main__":
   app.run(debug=True)