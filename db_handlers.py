import sqlite3


class DatabaseHandler:
    DEFAULT_ORDER = "ORDER BY score DESC, time ASC, date DESC"


    def __init__(self):
        self.conn = sqlite3.connect("SNAKE_SCORE.db")
        self.cur = self.conn.cursor()
        self.create_score_table()


    def __del__(self):
        print("Now being deleted....")
        self.cur.close()
        self.conn.close()


    def create_score_table(self):
        try:
            self.cur.execute("""CREATE TABLE score(
                player TEXT NOT NULL, 
                mode TEXT NOT NULL, 
                score INTEGER NOT NULL, 
                time REAL NOT NULL, 
                date REAL NOT NULL);"""
            )
            self.conn.commit()
        except Exception as e:
            # TABLE ALREADY EXISTS IN THE DATABASE
            pass

    
    def get_game_modes(self):
        return self.cur.execute("SELECT DISTINCT mode FROM score;").fetchall()

    
    def get_all_scores(self):
        return self.cur.execute(f"SELECT * FROM score {self.DEFAULT_ORDER};").fetchall()


    def get_mode_scores(self, mode=None):
        if mode:
            return self.cur.execute(f"SELECT * FROM score where mode=? {self.DEFAULT_ORDER};", (mode, )).fetchall()
        else:
            return self.get_all_scores()

    
    def set_score(self, player, mode, score, time, date):
        self.cur.execute("INSERT INTO score VALUES(?,?,?,?,?);", (player.upper(), mode, score, time, date))
        self.conn.commit()


    def get_top_10_scores(self, mode):
        return self.get_high_scores(mode)[:10]


    def get_all_time_top_10(self):
        return self.cur.execute("SELECT * FROM score ORDER BY score DESC LIMIT 10;").fetchall()


    def delete_all_scores(self):
        self.cur.execute("DELETE FROM score;")
        self.conn.commit()


    def get_totals(self, mode=""):
        return self.cur.execute("""SELECT COUNT(*), 
            COUNT(DISTINCT player), 
            COUNT(DISTINCT mode), 
            SUM(score), 
            SUM(time), 
            MIN(date), 
            MAX(date) 
            FROM score WHERE mode LIKE ?;""", (f"%{mode}%", )
        ).fetchone()


    def get_all_dates(self, mode=""):
        return self.cur.execute("SELECT date FROM score WHERE mode LIKE ?", (f"%{mode}%", )).fetchall()

