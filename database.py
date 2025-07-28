# Database initialization
import sqlite3

conn = sqlite3.connect("osu_pass.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    discord_id INTEGER PRIMARY KEY,
    osu_id INTEGER UNIQUE,
    total_performance_points INTEGER,
    score_list TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS maps (
    map_id INTEGER PRIMARY KEY,
    performance_points INTEGER,
    hr_mult REAL,
    dt_mult REAL,
    ez_mult REAL,
    ht_mult REAL,
    fl_mult REAL
)                   
""")

conn.commit()
conn.close()