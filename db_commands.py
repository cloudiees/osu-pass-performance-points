import sqlite3

def search_disc_user(discord_id):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
        return cursor.fetchone()

def search_osu_user(osu_user_id):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE osu_id = ?", (osu_user_id,))
        return cursor.fetchone()

def insert_user(discord_id, osu_user_id):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (discord_id, osu_id) VALUES (?, ?)", (discord_id, osu_user_id))
        conn.commit()
        
def find_map(map_id):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM maps WHERE map_id = ?", (map_id,))
        return cursor.fetchone()
    
def delete_user(discord_id):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
        conn.commit()