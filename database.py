# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            token TEXT,
            ip TEXT,
            location TEXT,
            latitude TEXT,
            longitude TEXT,
            user_agent TEXT
        )
    ''')
    conn.commit()
    conn.close()
