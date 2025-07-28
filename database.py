# Database initialization
import sqlite3

conn = sqlite3.connect("osu_pass.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    discord_id INTEGER PRIMARY KEY,
    osu_id INTEGER UNIQUE NOT NULL,
    total_performance_points INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS maps (
    map_id INTEGER PRIMARY KEY,
    performance_points REAL NOT NULL DEFAULT 0,
    hr_mult REAL NOT NULL DEFAULT 1.2,
    dt_mult REAL NOT NULL DEFAULT 1.5,
    ez_mult REAL NOT NULL DEFAULT 1.1,
    ht_mult REAL NOT NULL DEFAULT 0.5,
    fl_mult REAL NOT NULL DEFAULT 2
)                   
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    score_id INTEGER PRIMARY KEY,
    user_osu_id INTEGER NOT NULL,
    map_id INTEGER NOT NULL,
    performance_points REAL NOT NULL,
    mods TEXT,
    FOREIGN KEY (user_osu_id) REFERENCES users(osu_id)     
)          
""")

conn.commit()
conn.close()