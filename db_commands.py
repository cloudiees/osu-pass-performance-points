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

mod_combo_to_index = {
    "": 9,
    "HR": 10,
    "DT": 11,
    "EZ": 12,
    "FL": 13,
    "HT": 14,
    "EZHT": 26,
    "HTHR": 25,
    "DTHR": 17,
    "EZDT": 18,
    "DTFL": 19,
    "HRFL": 20,
    "EZFL": 21,
    "HTFL": 22,
    "DTHRFL": 23,
    "EZDTFL": 24,
    "HTHRFL": 25,
    "EZHTFL": 26
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

def insert_user(discord_id: int, osu_user_id: int, discord_name: str, osu_name: str):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (discord_id, osu_id, discord_name, osu_name) VALUES (?, ?, ?, ?)", (discord_id, osu_user_id, discord_name, osu_name))
        conn.commit()
        
def find_map(map_id: int):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM maps WHERE map_id = ?", (map_id,))
        return cursor.fetchone()
    
def delete_user(discord_id: int):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
        conn.commit()
        
def insert_score(score: Score):
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        map_id = score.beatmap_id
        score_id = score.id
        user_id = score.user_id
        cursor.execute("SELECT * FROM scores WHERE user_osu_id = ? AND map_id = ?", (user_id, map_id))
        prev_score = cursor.fetchone()
        mod_list = []
        mod_list_cleaned = []
        for mod in score.mods:
            mod_name = mod.acronym
            mod_list.append(mod_name)
            if mod_name == "NC":
                mod_list_cleaned.append("DT")
            elif mod_name in mod_col:
                mod_list_cleaned.append(mod_name)
            
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
        
        if mod_list:
            mod_clean_str = str(Mod(''.join(mod_list_cleaned)))
        else:
            mod_clean_str = ""
        star_rating = map_info[mod_combo_to_index[mod_clean_str]]
        cursor.execute("INSERT INTO scores (score_id, user_osu_id, map_id, performance_points, mods, star_rating) VALUES (?, ?, ?, ?, ?, ?)", (score_id, user_id, map_id, final_pp, mod_str, star_rating))
        
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
        
def get_leaderboard():
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT discord_name, total_performance_points FROM users ORDER BY total_performance_points DESC")
        return cursor.fetchall()
    
def get_top(user_id: int, stars: bool, reverse: bool):
    query = """
        SELECT maps.map_name, maps.diff_name, scores.star_rating, scores.mods, scores.performance_points
        FROM scores
        JOIN maps ON scores.map_id = maps.map_id
        WHERE scores.user_osu_id = ?
        ORDER BY
        """
    if stars:
        query += " scores.star_rating"
    else:
        query += " scores.performance_points"
        
    if reverse:
        query += " ASC"
    else:
        query += " DESC"
        
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        return cursor.fetchall()