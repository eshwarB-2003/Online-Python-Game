import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
env_path = BASE_DIR / ".env"
print("Loading .env from:", env_path)
load_dotenv(dotenv_path=env_path)
class DB:
    def __init__(self):
        self.db = psycopg2.connect(
            database="quiz_game",     # change to your DB name
            host="localhost",
            user="postgres",
            password="eshwarB1*",  # put your actual password here
            port="5432"
        )
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self):
        query = """CREATE TABLE IF NOT EXISTS wins (
            username VARCHAR(255) PRIMARY KEY,
            wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0,
            rating INTEGER NOT NULL DEFAULT 1000
        );"""
        callback = lambda: self.cursor.execute(query)
        self.execute(callback)
    
    def execute(self, callback):
        try:
            callback()
            self.db.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
    
    def increase_wins(self, username):
        query = """
        WITH upsert AS (
            UPDATE wins 
            SET wins = wins + 1
            WHERE username = %s
            RETURNING *
        )
        INSERT INTO wins (username, wins, losses, rating) 
        SELECT %s, 1, 0,1000
        WHERE NOT EXISTS (SELECT 1 FROM upsert);"""
        callback = lambda: self.cursor.execute(query, (username, username))
        self.execute(callback)
    
    def increase_losses(self, username):
        query = """
        WITH upsert AS (
            UPDATE wins 
            SET losses = losses + 1
            WHERE username = %s
            RETURNING *
        )
        INSERT INTO wins (username, wins, losses, rating) 
        SELECT %s, 0, 1, 1000
        WHERE NOT EXISTS (SELECT 1 FROM upsert);"""
        callback = lambda: self.cursor.execute(query, (username, username))
        self.execute(callback)

    def get_user_stats(self, username):
        query = """SELECT wins, losses, rating
                    FROM wins
                    WHERE username = %s;"""
        self.cursor.execute(query, (username, ))
        result = self.cursor.fetchone()  # fetchone() retrieves one record

        if result is not None:
            return {'wins': result[0], 'losses': result[1], 'rating': result[2]}
        else:
            return {'wins': 0, 'losses': 0, 'rating': 1000 }
        
    def get_rating(self, username):
        query = "SELECT rating FROM wins WHERE username = %s;"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return 1000  # default rating 

    def update_rating(self, username, new_rating):
        query = """
        INSERT INTO wins (username, wins, losses, rating)
        VALUES (%s, 0, 0, %s)
        ON CONFLICT (username)
        DO UPDATE SET rating = EXCLUDED.rating;
        """
        callback = lambda: self.cursor.execute(query, (username, new_rating))
        self.execute(callback)
    def update_elo_atomic(self, winner, loser):
        try:
            self.cursor.execute("BEGIN;")
            # Lock both rows
            self.cursor.execute(
                 "SELECT rating FROM wins WHERE username = %s FOR UPDATE;",
                 (winner,)
                 )
            winner_rating = self.cursor.fetchone()[0]
            self.cursor.execute(
                "SELECT rating FROM wins WHERE username = %s FOR UPDATE;",
                (loser,)
                )
            loser_rating = self.cursor.fetchone()[0]
            K = 32
            expected_win = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
            expected_loss = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
            new_winner_rating = int(winner_rating + K * (1 - expected_win))
            new_loser_rating = int(loser_rating + K * (0 - expected_loss))
            self.cursor.execute(
                 "UPDATE wins SET rating = %s WHERE username = %s;",
                 (new_winner_rating, winner)
                   )
            self.cursor.execute(
                "UPDATE wins SET rating = %s WHERE username = %s;",
                (new_loser_rating, loser)
                )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print("ELO update failed:", e)

    def get_top_players(self):
        query = """
        SELECT username, rating, wins, losses
        FROM wins
        ORDER BY rating DESC
        LIMIT 10;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        leaderboard = []
        for row in results:
            leaderboard.append({
                "username": row[0],
                "rating": row[1],
                "wins": row[2],
                "losses": row[3]
            })
        return leaderboard
    
    def __del__(self):
        self.cursor.close()
        self.db.close()