import sqlite3
from ossapi import Score, Mod
from osu_api import osu_api

mod_col = {
    "EZ": 4,
    "HR": 2,
    "DT": 3,
    "HT": 5,
    "NC": 3,
    "FL": 6,
}

def search_disc_user(discord_id: int):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
        return cursor.fetchone()

def search_osu_user(osu_user_id: int):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE osu_id = ?", (osu_user_id,))
        return cursor.fetchone()

def insert_user(discord_id: int, osu_user_id: int):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (discord_id, osu_id) VALUES (?, ?)", (discord_id, osu_user_id))
        conn.commit()
        
def find_map(map_id: int):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM maps WHERE map_id = ?", (map_id,))
        return cursor.fetchone()
    
def delete_user(discord_id: int):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT osu_id FROM users WHERE discord_id = ?", (discord_id,))
        osu_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
        cursor.execute("DELETE FROM scores WHERE user_osu_id = ?", (osu_id,))
        conn.commit()
        
def insert_score(score: Score):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        map_id = score.beatmap_id
        score_id = score.id
        user_id = score.user_id
        cursor.execute("SELECT * FROM scores WHERE user_osu_id = ? AND map_id = ?", (user_id, map_id))
        prev_score = cursor.fetchone()
        mod_list = [mod.acronym for mod in score.mods]
        if "CL" in mod_list:
            mod_list.remove("CL")
        if mod_list:
            mod_str = str(Mod(''.join(mod_list)))
        else:
            mod_str = ""
            
        cursor.execute("SELECT * FROM maps WHERE map_id = ?", (map_id,))
        map_info = cursor.fetchone()
        initial_pp = map_info[1]
        final_pp = initial_pp
        for mod in mod_list:
            if mod in mod_col:
                final_pp += (map_info[mod_col[mod]] - 1) * initial_pp
        
        if prev_score:
            if prev_score[3] >= final_pp:
                raise Exception("Previous score with geq pp")
            
            delete_score(prev_score)
                
        cursor.execute("INSERT INTO scores (score_id, user_osu_id, map_id, performance_points, mods) VALUES (?, ?, ?, ?, ?)", (score_id, user_id, map_id, final_pp, mod_str))
        
        cursor.execute("UPDATE users SET total_performance_points = total_performance_points + ? WHERE osu_id = ?", (final_pp, user_id))
        
        print("success")
        conn.commit()
                
def delete_score(score):
    with sqlite3.connect("osu_pass.db") as conn:
        print("attempting to delete score")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET total_performance_points = total_performance_points - ? WHERE osu_id = ?", (score[3], score[1]))
        cursor.execute("DELETE FROM scores WHERE score_id = ?", (score[0],))
        conn.commit()