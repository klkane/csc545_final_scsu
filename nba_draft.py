from flask import Flask, current_app, render_template
import pymysql
from pymongo import MongoClient

app = Flask(__name__)

class NBADataSQL:
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
        cursor = self.conn.cursor()
        sql = "SELECT id, pos_c, pos_pf, pos_sf, pos_util, pos_g, pos_f, pos_pg, pos_sg FROM rosters ORDER BY id"
        cursor.execute( sql )
        for r_id, pos_c, pos_pf, pos_sf, pos_util, pos_g, pos_f, pos_pg, pos_sg in cursor.fetchall():
            rosters.append( { "id": r_id, "pos_c": pos_c, "pos_pf": pos_pf, "pos_sf": pos_sf, "pos_util": pos_util, "pos_g": pos_g, "pos_f": pos_f, "pos_pg": pos_pg, "pos_sg": pos_sg } ) 
        return rosters

    def getPlayer( self, p_id ):
        player = {}
        cursor = self.conn.cursor()
        sql = "SELECT id, position, name, salary, avg_ppg, team FROM players WHERE id = %s";
        cursor.execute( sql, ( p_id ) )
        for p_id, position, name, salary, avg_ppg, team in cursor.fetchall():
            player.update( { "id": p_id, "position": position, "name": name, "salary": salary, "avg_ppg": avg_ppg, "team": team } );
        return player

    def getPlayers( self ):
        players = []
        cursor = self.conn.cursor()
        sql = "SELECT id, position, name, salary, avg_ppg, team FROM players ORDER BY name";
        cursor.execute( sql, ( p_id ) )
        for p_id, position, name, salary, avg_ppg, team in cursor.fetchall():
            players.append( { "id": p_id, "position": position, "name": name, "salary": salary, "avg_ppg": avg_ppg, "team": team } );
        return players

    def getGames( self ):
        games = []
        return games


data = NBADataSQL();

@app.route("/viewGames", methods=['POST', 'GET'] )
def games():
    return render_template( 'viewGames.html', nba = data )

@app.route("/viewPlayers", methods=['POST', 'GET'] )
def players():
    return render_template( 'viewPlayers.html', nba = data )

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


