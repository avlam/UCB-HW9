
# coding: utf-8

# # Climate App
# UCBE HW #9
# written by: A. Lam

# Dependencies
from flask import Flask, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from sqlalchemy import create_engine
from sqlalchemy.orm import Session 
from sqlalchemy.ext.automap import automap_base
Base = automap_base()

# Constants
DAYS_IN_YEAR = 365

# SQL Alchemy session and reflection of tables
engine = create_engine('sqlite:///hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect = True)
session = Session(bind=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

# create Flask service
app = Flask(__name__)

# setup endpoints
base = '/api/v1.0/'
# endpoints = ['precipitation',
#             'stations',
#             'tobs']


# @app.route(f'{base}<endpoint>')
# def director(endpoint):
#     pass

@app.route(f'{base}precipitation')
def precipitation():
    """query for precipitation measurements over the last year"""
    query_result = session.query(Measurement.date,func.avg(Measurement.prcp)).filter(
        extract('year',Measurement.date) == date.today().year-1).group_by(Measurement.date).all()
    dates = [response[0] for response in query_result]
    avg_prcp = [response[1] for response in query_result]
    out={}
    for i in range(len(dates)):
        out[datetime.strftime(dates[i],'%Y-%m-%d')] = avg_prcp[i]
    return jsonify(out)

@app.route(f'{base}stations')
def stations():
    query_result = session.query(Station.station).all()
    stations = [result[0] for result in query_result]
    return jsonify(stations)

@app.route(f'{base}tobs')
def tobs():
    """query for observed temperature measurements over the last year"""
    query_result = session.query(Measurement.date,func.avg(Measurement.tobs)).filter(
        extract('year',Measurement.date) == date.today().year-1).group_by(Measurement.date).all()
    dates = [response[0] for response in query_result]
    avg_tobs = [response[1] for response in query_result]
    out={}
    for i in range(len(dates)):
        out[datetime.strftime(dates[i],'%Y-%m-%d')] = avg_tobs[i]
    return jsonify(out)

@app.route(f'{base}<start_date_str>/<end_date_str>')
def temp_summary_start_end(start_date_str,end_date_str):
    return temp_summary(start_date_str,end_date_str)

@app.route(f'{base}<start_date_str>')
def temp_summary_start(start_date_str):
    return temp_summary(start_date_str,datetime.strftime(datetime.today(),'%Y-%m-%d'))

@app.route(f'{base}')
def temp_summary_def():
    return temp_summary(datetime.strftime(datetime.today() - timedelta(days = DAYS_IN_YEAR),'%Y-%m-%d'),datetime.strftime(datetime.today(),'%Y-%m-%d'))

def temp_summary(start_date_str,end_date_str):
#     date format: %Y-%m-%d
    try:
        start_date = datetime.strptime(start_date_str,'%Y-%m-%d')
    except ValueError as message:
        return f'{start_date_str} is not a valid start date. \n Start date needs to be in format: %Y-%m-%d' 
    try: 
        end_date = datetime.strptime(end_date_str,'%Y-%m-%d')
    except ValueError as message:
        return f'{end_date_str} is not a valid start date. \n End date needs to be in format: %Y-%m-%d' 
    query_result = session.query(
        func.min(Measurement.date),
        func.max(Measurement.date),
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)).filter( 
        Measurement.date.between(start_date - timedelta(days = 1), end_date)).all()[0] 
        # timedelta included due to inclusive bug with SQL ALchemy 'between'
    if not any(query_result):
        return f'{start_date_str} to {end_date_str} yielded no results from dataset'
    elif query_result:
        (d_min,d_max,t_min,t_max,t_avg) = query_result
        out = {
            'Start Date' : d_min,
            'End Date' : d_max,
            'Max Temperature' : t_max,
            'Min Temperature' : t_min,
            'Average Temperature' : t_avg  
            }
        return jsonify(out)
    else:
        return 'Something unexpected happened.'

@app.route('/')
def home():
    return '<p>Welcome! </p> \
    <p>Please query the endpoints below for info regarding weather measurements in Hawaii:</p> \
    <ul style="list-style-type:none"> \
    <li>List of Stations: <a href="/api/v1.0/stations">/api/v1.0/stations</a></li> \
    <li>Temperature Summary: <a href="/api/v1.0/">/api/v1.0/start_date/end_date</a></li> \
    <li>Precipitation for the past year: <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li> \
    <li>Observed Temperatures for the past year: <a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li> \
    </ul>'

if __name__ == '__main__':
    app.run()

