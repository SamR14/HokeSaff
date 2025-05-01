# Importē Flask klasi no flask bibliotēkas
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
import random
# Izveido Flask lietotnes objektu
app = Flask(__name__)

# Database setup
DATABASE = Path(__file__).parent / 'datubaze.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                age INTEGER NOT NULL,
                FOREIGN KEY (team_id) REFERENCES teams (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                coach TEXT NOT NULL,
                division TEXT NOT NULL
                logo TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                home_team_id INTEGER NOT NULL,
                away_team_id INTEGER NOT NULL,
                final_score TEXT NOT NULL,
                FOREIGN KEY (home_team_id) REFERENCES teams (id),
                FOREIGN KEY (away_team_id) REFERENCES teams (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playerstats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                assists INTEGER NOT NULL,
                shots_on_goal INTEGER NOT NULL,
                saves INTEGER,
                penalty_minutes INTEGER NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games (id),
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        db.commit()
        db.close()
# init_db()
@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM teams')
    teams = cursor.fetchall()
    db.close()

    return render_template("index.html", teams=teams)

@app.route("/add_team", methods=['GET', 'POST'])
def add_team():
    if request.method == 'POST':
        name = request.form.get('name')
        coach = request.form.get('coach')
        division = request.form.get('division')

        db = get_db()
        cursor = db.cursor()
        
        # Create new team
        cursor.execute('''
            INSERT INTO teams (name, coach, division)
            VALUES (?, ?, ?)
        ''', (name, coach, division))
        
        db.commit()
        db.close()
        return redirect(url_for('index'))

    return render_template("add_team.html")

@app.route("/games")
def games():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            games.id, 
            games.date, 
            games.location, 
            games.final_score, 
            home.name AS home_team, 
            away.name AS away_team 
        FROM games
        JOIN teams AS home ON games.home_team_id = home.id
        JOIN teams AS away ON games.away_team_id = away.id
        ORDER BY games.date DESC
    ''')
    
    games = cursor.fetchall()
    db.close()
    
    return render_template("games.html", games=games)

@app.route("/add_game", methods=['GET', 'POST'])
def add_game():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        date = request.form.get('date')
        location = request.form.get('location')
        home_team_id = request.form.get('home-team')
        away_team_id = request.form.get('away-team')
        score = request.form.get('score')

        # Insert game data into the games table
        cursor.execute('''
            INSERT INTO games (date, location, home_team_id, away_team_id, final_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, location, home_team_id, away_team_id, score))
        
        db.commit()
        db.close()
        return redirect(url_for('games'))

    # On GET: fetch all teams to populate the dropdowns
    cursor.execute('SELECT id, name FROM teams')
    teams = cursor.fetchall()
    db.close()

    return render_template("add_game.html", teams=teams)

@app.route("/roster/<int:team_id>")
def roster(team_id):
    db = get_db()
    cursor = db.cursor()
    
    # Fetch players for the selected team
    cursor.execute('SELECT * FROM players WHERE team_id = ?', (team_id,))
    players = cursor.fetchall()

    # Fetch the team name
    cursor.execute('SELECT name FROM teams WHERE id = ?', (team_id,))
    team = cursor.fetchone()
    db.close()
    
    return render_template("roster.html", players=players, team=team)

@app.route("/stats")
def stats():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT playerstats.*, players.name 
        FROM playerstats 
        JOIN players ON playerstats.player_id = players.id
    ''')
    stats = cursor.fetchall()
    db.close()

    return render_template("stats.html", stats=stats)

@app.route("/delete_team/<int:team_id>", methods=['POST'])
def delete_team(team_id):
    db = get_db()
    cursor = db.cursor()
    
    # Delete the team by ID
    cursor.execute('DELETE FROM teams WHERE id = ?', (team_id,))
    db.commit()
    db.close()
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True) 