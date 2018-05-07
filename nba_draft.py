from flask import Flask, current_app, render_template, request, redirect, url_for
import pymysql
import sys
from pymongo import MongoClient
from nocache import nocache

app = Flask(__name__)

class NBADataMongo:
    client = MongoClient( host='localhost', port=27017) 
    sortFilter = {}

    def getTeams( self ):
        return self.client.csc545_final.teams.find().sort( "name", 1 )

    def deleteAll( self ):
        self.client.csc545_final.teams.drop()
        self.client.csc545_final.extended_players.drop()
        self.client.csc545_final.players.drop()
        self.client.csc545_final.rosters.drop()
        return True

    def copyFromSQL( self, sql ):
        teams = self.client.csc545_final.teams
        for team in sql.getTeams():
            teams.insert_one( team )
        
        players = self.client.csc545_final.players
        for player in sql.getPlayers():
            players.insert_one( player )
        
        extended_players = self.client.csc545_final.extended_players
        for extended_player in sql.getExtendedPlayers():
            extended_players.insert_one( extended_player )
        
        rosters = self.client.csc545_final.rosters
        for roster in sql.getRosters():
            rosters.insert_one( roster )
    
    def getPlayersByRoster( self, rosterId ):
        players = []
        roster = self.getRoster( rosterId )
        players.append( self.getPlayer( roster['pos_c'] ) )
        players.append( self.getPlayer( roster['pos_pg'] ) )
        players.append( self.getPlayer( roster['pos_sg'] ) )
        players.append( self.getPlayer( roster['pos_g'] ) )
        players.append( self.getPlayer( roster['pos_pf'] ) )
        players.append( self.getPlayer( roster['pos_sf'] ) )
        players.append( self.getPlayer( roster['pos_f'] ) )
        players.append( self.getPlayer( roster['pos_util'] ) )
        return players
   
    def updateTeam( self, team_id, name ):
        self.client.csc545_final.teams.replace_one( { "id": team_id }, { "id": team_id, "name": name } );
        return True
    
    def testConnection( self ):
        return True

    def getRosters( self ):
        return self.client.csc545_final.rosters.find().sort( "id", 1 )

    def getPlayer( self, p_id ):
        if p_id:
            return self.client.csc545_final.players.find_one({ "id": p_id })
        else:
            return {}

    def getPlayers( self, sortFilter = {} ):
        return self.client.csc545_final.players.find( sortFilter ).sort( "name", 1 )

    def getPlayerExtended( self, playerId ):
        return self.client.csc545_final.extended_players.find_one( { "playerid": playerId } )

    def getRoster( self, rosterId ):
        # there is some type issue here that is quite confusing but the following call doesnt work
        # return self.client.csc545_final.rosters.find_one( { "id": rosterId } )
        # so I am interating over the set to make this happen, not a great solution but it works!
        for roster in self.getRosters():
            if str( roster['id'] ) == str( rosterId ):
                return roster
        return {}

    def deleteRoster( self, roster_id ):
        self.client.csc545_final.rosters.remove( { 'id': int( roster_id ) } )
        return True

    def addRoster( self, pos_c, pos_pg, pos_sg, pos_g, pos_pf, pos_sf, pos_f, pos_util ):
        maxRoster = self.client.csc545_final.rosters.find_one( sort=[("id", -1)] )
        nextId = maxRoster['id'] + 1
        # need to cast all to int to preserve type!
        self.client.csc545_final.rosters.insert_one( { "id": int( nextId ), "pos_c": int( pos_c ), "pos_pg": int( pos_pg ), "pos_sg": int( pos_sg ), "pos_g": int( pos_g ), "pos_pf": int( pos_pf ), "pos_sf": int( pos_sf ), "pos_f": int( pos_f ), "pos_util": int( pos_util ) } )
        return True
    
class NBADataSQL:
    conn = pymysql.connect( host='127.0.0.1', user='csc545_final', passwd='nb4f4nt4sy', db='csc545_final' )
    sortFilter = {}

    def testConnection( self ):
        conn = pymysql.connect( host='127.0.0.1', user='csc545_final', passwd='nb4f4nt4sy', db='csc545_final' )
        return True

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

    def getRoster( self, rosterId ):
        roster = {}
        cursor = self.conn.cursor()
        sql = "SELECT id, pos_c, pos_pf, pos_sf, pos_util, pos_g, pos_f, pos_pg, pos_sg FROM rosters WHERE id = %s"
        cursor.execute( sql, ( rosterId ) )
        for r_id, pos_c, pos_pf, pos_sf, pos_util, pos_g, pos_f, pos_pg, pos_sg in cursor.fetchall():
            roster = { "id": r_id, "pos_c": pos_c, "pos_pf": pos_pf, "pos_sf": pos_sf, "pos_util": pos_util, "pos_g": pos_g, "pos_f": pos_f, "pos_pg": pos_pg, "pos_sg": pos_sg }
        return roster

    def getPlayerExtended( self, playerId ):
        player = {}
        cursor = self.conn.cursor()
        sql = "SELECT points, FGpct, Rebounds, Assists, Steals, Blocks FROM extended_players WHERE playerid = %s"
        cursor.execute( sql, ( playerId ) )
        for points, fgpct, rebounds, assists, steals, blocks in cursor.fetchall():
            player = { "points": points, "fgpct": str( fgpct ), "rebounds": rebounds, "assists": assists, "steals": steals, "blocks": blocks }
        return player

    def getExtendedPlayers( self ):
        players = []
        cursor = self.conn.cursor()
        sql = "SELECT playerid, points, FGpct, Rebounds, Assists, Steals, Blocks FROM extended_players"
        cursor.execute( sql )
        for playerid, points, fgpct, rebounds, assists, steals, blocks in cursor.fetchall():
            players.append( { "playerid": playerid, "points": points, "fgpct": str( fgpct ), "rebounds": rebounds, "assists": assists, "steals": steals, "blocks": blocks } )
        return players

    def getPlayersByRoster( self, rosterId ):
        players = []
        roster = self.getRoster( rosterId )
        players.append( self.getPlayer( roster['pos_c'] ) )
        players.append( self.getPlayer( roster['pos_pg'] ) )
        players.append( self.getPlayer( roster['pos_sg'] ) )
        players.append( self.getPlayer( roster['pos_g'] ) )
        players.append( self.getPlayer( roster['pos_pf'] ) )
        players.append( self.getPlayer( roster['pos_sf'] ) )
        players.append( self.getPlayer( roster['pos_f'] ) )
        players.append( self.getPlayer( roster['pos_util'] ) )
        return players

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

    def getPlayers( self, searchFilter = None ):
        players = []
        cursor = self.conn.cursor()
        sql = "SELECT id, position, name, salary, avg_ppg, team FROM players "
        where = ""

        if searchFilter:
            where = "WHERE "
            for column in searchFilter:
                if column == 'team':
                    searchFilter[column]['val'] = "'" + searchFilter[column]['val'] + "'"
                where = where + column + " " + searchFilter[column]['op'] + " " + searchFilter[column]['val'] + " "
        orderClause = "ORDER BY name"
        sql = sql + where + orderClause    
        cursor.execute( sql )
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
    data.testConnection()
    return render_template( 'viewGames.html', nba = data )

@app.route("/viewPlayers", methods=['POST', 'GET'] )
@nocache
def players():
    data.testConnection()
    filterSort = None
    if request.method == "POST" and request.form.get( 'column' ) and request.form.get( 'val' ):
        filterSort = { request.form.get( 'column' ): { "op": request.form.get( 'op' ), "val": request.form.get( 'val' ) } }

    return render_template( 'viewPlayers.html', nba = data, filterSort = filterSort  )

@app.route("/viewTeams", methods=['POST', 'GET'] )
@nocache
def teams():
    data.testConnection()
    if request.method == "POST":
        for team in data.getTeams():
            if team["name"] != request.form.get( team["id"] + "_name" ):
                data.updateTeam( team["id"], request.form.get( team["id"] + "_name" ) );

    return render_template( 'viewTeams.html', nba = data )

@app.route("/createRoster", methods=['POST', 'GET'] )
@nocache
def createRoster():
    data.testConnection()
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
    data.testConnection()
    return render_template( 'rosters.html', nba = data )

@app.route("/", methods=['POST', 'GET'] )
@nocache
def index():
    data.testConnection()
    return render_template( 'index.html', nba = data )

@app.route("/analyzeRoster/<rosterId>", methods=['POST', 'GET'] )
@nocache
def analyzeRoster( rosterId ):
    data.testConnection()
    return render_template( 'analyzeRoster.html', nba = data, rosterId = rosterId )

@app.route("/deleteRoster/<rosterId>" )
@nocache
def delete_roster( rosterId ):
    data.testConnection()
    data.deleteRoster( rosterId )
    return redirect( url_for( 'rosters' ) )

@app.route("/copyToMongo", methods=['POST', 'GET'] )
@nocache
def copyMongo():
    data.testConnection()
    mongo = NBADataMongo()
    mongo.deleteAll()
    mongo.copyFromSQL( data )
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


