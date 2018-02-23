from flask import Flask, current_app, render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template( 'index.html' )

@app.route( "/static/<fileName>" )
def static_files( fileName ):
    # this approach is technically bad, as it takes user input and will serve files
    # without checking to see if thats acceptable or not.  In a real production application
    # we would use a webserver such as nginx/apache to serve the static files, this is
    # just for development purposes
    return current_app.send_static_file( fileName )
