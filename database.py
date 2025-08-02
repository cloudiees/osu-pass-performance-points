# Database initialization
import sqlite3

conn = sqlite3.connect("osu_pass.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    discord_id INTEGER PRIMARY KEY,
    osu_id INTEGER UNIQUE NOT NULL,
    total_performance_points INTEGER DEFAULT 0,
    discord_name TEXT NOT NULL,
    osu_name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS maps (
    map_id INTEGER PRIMARY KEY,
    performance_points REAL NOT NULL DEFAULT 0,
    hr_mult REAL NOT NULL DEFAULT 1.2,
    dt_mult REAL NOT NULL DEFAULT 1.5,
    ez_mult REAL NOT NULL DEFAULT 0,
    ht_mult REAL NOT NULL DEFAULT 0,
    fl_mult REAL NOT NULL DEFAULT 2,
    map_name TEXT NOT NULL,
    diff_name TEXT NOT NULL,
    sr_nm REAL NOT NULL,
    sr_hr REAL NOT NULL,
    sr_dt REAL NOT NULL,
    sr_ez REAL NOT NULL DEFAULT 0,
    sr_fl REAL NOT NULL,    
    sr_ht REAL NOT NULL DEFAULT 0,
    sr_htez REAL NOT NULL DEFAULT 0,
    sr_hthr REAL NOT NULL DEFAULT 0,
    sr_hrdt REAL NOT NULL,
    sr_ezdt REAL NOT NULL DEFAULT 0,
    sr_dtfl REAL NOT NULL,
    sr_hrfl REAL NOT NULL,
    sr_ezfl REAL NOT NULL DEFAULT 0,
    sr_htfl REAL NOT NULL DEFAULT 0,
    sr_hrdtfl REAL NOT NULL,
    sr_ezdtfl REAL NOT NULL DEFAULT 0,
    sr_hrhtfl REAL NOT NULL DEFAULT 0,
    sr_ezhtfl REAL NOT NULL DEFAULT 0,
    map_rank INTEGER NOT NULL,
    top_acc REAL
)                   
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    score_id INTEGER PRIMARY KEY,
    user_osu_id INTEGER NOT NULL,
    map_id INTEGER NOT NULL,
    performance_points REAL NOT NULL,
    mods TEXT,
    star_rating REAL NOT NULL,
    accuracy REAL NOT NULL,
    FOREIGN KEY (user_osu_id) REFERENCES users(osu_id) ON DELETE CASCADE,
    FOREIGN KEY (map_id) REFERENCES maps(map_id) 
)          
""")

conn.commit()
conn.close()