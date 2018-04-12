from flask import Flask, current_app, render_template
import pymysql
from pymongo import MongoClient

app = Flask(__name__)

class NBAData:
    conn = pymysql.connect( host='127.0.0.1', user='csc545_final', passwd='nb4f4nt4sy', db='csc545_final' )

    def getTeams( self ):
        teams = []
        cursor = self.conn.cursor()
        sql = "SELECT id, name FROM teams ORDER BY name"
        cursor.execute( sql )
        for team_id, name in cursor.fetchall():
            teams.append( { "id": team_id, "name": name } )
        return teams

    def getRosters( self ):
        rosters = []
        return rosters

    def getPlayers( self ):
        players = []
        return players

    def getGames( self ):
        games = []
        return games


data = NBAData();

@app.route("/games", methods=['POST', 'GET'] )
def games():
    return render_template( 'games.html', nba = data )

@app.route("/players", methods=['POST', 'GET'] )
def players():
    return render_template( 'players.html', nba = data )

@app.route("/createRoster", methods=['POST', 'GET'] )
def createRoster():
    return render_template( 'createRoster.html', nba = data )

@app.route("/rosters", methods=['POST', 'GET'] )
def rosters():
    return render_template( 'rosters.html', nba = data )

@app.route("/", methods=['POST', 'GET'] )
def index():
    return render_template( 'index.html', nba = data )

@app.route( "/static/<fileName>" )
def static_files( fileName ):
    # this approach is technically bad, as it takes user input and will serve files
    # without checking to see if thats acceptable or not.  In a real production application
    # we would use a webserver such as nginx/apache to serve the static files, this is
    # just for development purposes
    return current_app.send_static_file( fileName )

if __name__ == '__main__':
    app.run( threaded=True, host='0.0.0.0' )


