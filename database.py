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
    lazer_mult INTEGER,
    hr_mult INTEGER,
    dt_mult INTEGER,
    ez_mult INTEGER,
    ht_mult INTEGER,
    fl_mult INTEGER
)                   
""")

conn.commit()
conn.close()