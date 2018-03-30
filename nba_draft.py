from flask import Flask, current_app, render_template
import pymysql

app = Flask(__name__)

def getSQLDatabaseConn():
    conn = pymysql.connect( host='127.0.0.1', user='csc545_final', passwd='nb4f4nt4sy', db='csc545_final' )
    return conn

@app.route("/")
def index():
    conn = getSQLDatabaseConn()
    
    return render_template( 'index.html' )

@app.route( "/static/<fileName>" )
def static_files( fileName ):
    # this approach is technically bad, as it takes user input and will serve files
    # without checking to see if thats acceptable or not.  In a real production application
    # we would use a webserver such as nginx/apache to serve the static files, this is
    # just for development purposes
    return current_app.send_static_file( fileName )
