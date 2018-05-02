from flask import Flask, current_app, render_template, request, redirect, url_for
import pymysql
from pymongo import MongoClient
from nocache import nocache

app = Flask(__name__)

class NBADataMongo:
    client = MongoClient( host='localhost', port=27017) 

    def getTeams( self ):
        return self.client.csc545_final.teams.find().sort( "name", 1 )

    def _getTeams( self ):
        return self.client.csc545_final.teams

    def copyTeamsFromSQL( self, sql ):
        teams = self._getTeams()
        for team in sql.getTeams():
            teams.insert_one( team)
    
    def updateTeam( self, team_id, name ):
        self._getTeams().replace_one( { "id": team_id }, { "id": team_id, "name": name } );
        return True

    def getRosters( self ):
        rosters = []
        return rosters

    def deleteRoster( self, roster_id ):
        return True

    def addRoster( self, pos_c, pos_pg, pos_sg, pos_g, pos_pf, pos_sf, pos_f, pos_util ):
        return True
    
    def getPlayer( self, p_id ):
        player = {}
        return player

    def getPlayers( self ):
        players = []
        return players

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

    def updateTeam( self, team_id, name ):
        sql = "UPDATE teams SET name = %s WHERE id = %s"
        cursor = self.conn.cursor()
        cursor.execute( sql, ( name, team_id ) )
        return True

    def getRosters( self ):
        rosters = []
        cursor = self.conn.cursor()
        sql = "SELECT id, pos_c, pos_pf, pos_sf, pos_util, pos_g, pos_f, pos_pg, pos_sg FROM rosters ORDER BY id"
        cursor.execute( sql )
        for r_id, pos_c, pos_pf, pos_sf, pos_util, pos_g, pos_f, pos_pg, pos_sg in cursor.fetchall():
            rosters.append( { "id": r_id, "pos_c": pos_c, "pos_pf": pos_pf, "pos_sf": pos_sf, "pos_util": pos_util, "pos_g": pos_g, "pos_f": pos_f, "pos_pg": pos_pg, "pos_sg": pos_sg } ) 
        return rosters

    def deleteRoster( self, roster_id ):
        cursor = self.conn.cursor()
        sql = "DELETE FROM rosters WHERE id = %s"
        cursor.execute( sql, ( roster_id ) )
        return True

    def addRoster( self, pos_c, pos_pg, pos_sg, pos_g, pos_pf, pos_sf, pos_f, pos_util ):
        cursor = self.conn.cursor()
        sql = "INSERT INTO rosters ( pos_c, pos_pg, pos_sg, pos_g, pos_pf, pos_sf, pos_f, pos_util ) VALUES( %s, %s, %s, %s, %s, %s, %s, %s )"
        cursor.execute( sql, ( pos_c, pos_pg, pos_sg, pos_g, pos_pf, pos_sf, pos_f, pos_util ) )
        return True

    def getPlayer( self, p_id ):
        player = {}
        cursor = self.conn.cursor()
        sql = "SELECT id, position, name, salary, avg_ppg, team FROM players WHERE id = %s";
        cursor.execute( sql, ( p_id ) )
        for p_id, position, name, salary, avg_ppg, team in cursor.fetchall():
            player.update( { "id": p_id, "position": position, "name": name, "salary": salary, "avg_ppg": avg_ppg, "team": team } );
        return player

    def getPlayers( self, team = "ALL" ):
        players = []
        cursor = self.conn.cursor()
        if( team == "ALL" ):
            sql = "SELECT id, position, name, salary, avg_ppg, team FROM players ORDER BY name"
            cursor.execute( sql )
        else:
            sql = "SELECT id, position, name, salary, avg_ppg, team FROM players WHERE team = %s ORDER BY name"
            cursor.execute( sql, ( team ) )
        for p_id, position, name, salary, avg_ppg, team in cursor.fetchall():
            players.append( { "id": p_id, "position": position, "name": name, "salary": salary, "avg_ppg": avg_ppg, "team": team } );
        return players

    def __init__( self ):
        self.conn.autocommit( True );


data = NBADataSQL();
#data = NBADataMongo();

@app.route("/viewGames", methods=['POST', 'GET'] )
@nocache
def games():
    return render_template( 'viewGames.html', nba = data )

@app.route("/viewPlayers", methods=['POST', 'GET'] )
@nocache
def players():
    return render_template( 'viewPlayers.html', nba = data )

@app.route("/viewTeams", methods=['POST', 'GET'] )
@nocache
def teams():
    if request.method == "POST":
        for team in data.getTeams():
            if team["name"] != request.form.get( team["id"] + "_name" ):
                data.updateTeam( team["id"], request.form.get( team["id"] + "_name" ) );

    return render_template( 'viewTeams.html', nba = data )

@app.route("/createRoster", methods=['POST', 'GET'] )
@nocache
def createRoster():
    if request.method == "POST":
        data.addRoster( request.form.get( "pos_c" ),
                request.form.get( "pos_pg" ),
                request.form.get( "pos_sg" ),
                request.form.get( "pos_g" ),
                request.form.get( "pos_pf" ),
                request.form.get( "pos_sf" ),
                request.form.get( "pos_f" ),
                request.form.get( "pos_util" ) )

    return render_template( 'createRoster.html', nba = data )

@app.route("/rosters", methods=['POST', 'GET'] )
@nocache
def rosters():
    return render_template( 'rosters.html', nba = data )

@app.route("/", methods=['POST', 'GET'] )
@nocache
def index():
    return render_template( 'index.html', nba = data )

@app.route("/deleteRoster/<rosterId>" )
@nocache
def delete_roster( rosterId ):
    data.deleteRoster( rosterId )
    return redirect( url_for( 'rosters' ) )

@app.route("/copyToMongo", methods=['POST', 'GET'] )
@nocache
def copyMongo():
    mongo = NBADataMongo()
    mongo.copyTeamsFromSQL( data )
    return render_template( 'copy.html', nba = data )

@app.route( "/static/<fileName>" )
def static_files( fileName ):
    # this approach is technically bad, as it takes user input and will serve files
    # without checking to see if thats acceptable or not.  In a real production application
    # we would use a webserver such as nginx/apache to serve the static files, this is
    # just for development purposes
    return current_app.send_static_file( fileName )

if __name__ == '__main__':
    app.run( threaded=True, host='0.0.0.0' )


