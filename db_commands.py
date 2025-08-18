import sqlite3
from ossapi import Score, Mod
from osu_api import osu_api
import asyncio
from console import print_to_console
import math

CLEANED_MODS = {"EZ","HR","DT","HT","NC","FL"}

MOD_COMBO_TO_INDEX = {
    "NM": 9,
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

COLUMN_INDEX_MAP = {
    "map_id": 0,
    "pp": 1,
    "hr_mult": 2,
    "dt_mult": 3,
    "ez_mult": 4,
    "ht_mult": 5,
    "fl_mult": 6,
    "map_name": 7,
    "diff_name": 8,
    "sr_nm": 9,
    "sr_hr": 10,
    "sr_dt": 11,
    "sr_ez": 12,
    "sr_fl": 13,
    "sr_ht": 14,
    "sr_htez": 15,
    "sr_hthr": 16,
    "sr_hrdt": 17,
    "sr_ezdt": 18,
    "sr_dtfl": 19,
    "sr_hrfl": 20,
    "sr_ezfl": 21,
    "sr_htfl": 22,
    "sr_hrdtfl": 23,
    "sr_ezdtfl": 24,
    "sr_hrhtfl": 25,
    "sr_ezhtfl": 26,
    "map_rank": 27,
    "top_acc": 28
}

COLUMN_INDEX_SCORE = {
    "score_id": 0,
    "osu_id": 1,
    "map_id": 2,
    "pp": 3,
    "mods": 4,
    "sr": 5,
    "acc": 6
}

def search_disc_user(discord_id: int):
    """
    Retrieves user data based on discord id
    
    Parameters:
    discord_id (int): Discord id to search for
    
    Returns:
    tuple or None: Returns the tuple of the discord id's data or nothing if discord user is not found 
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
            return cursor.fetchone()
        except Exception as e:
            print_to_console(f"Fetching discord user failed due to: {e}")

def search_osu_user(osu_user_id: int):
    """
    Retrieves user data based on osu! user id
    
    Parameters:
    osu_user_id (int): osu! id to search for
    
    Returns:
    tuple or None: Returns the tuple of the osu! id's data or nothing if osu! user is not found 
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE osu_id = ?", (osu_user_id,))
            return cursor.fetchone()
        except Exception as e:
            print_to_console(f"Fetching osu! user failed due to: {e}")

def insert_user(discord_id: int, osu_user_id: int, discord_name: str, osu_name: str):
    """
    Inserts user into database
    
    Parameters:
    discord_id (int): Discord id to insert
    osu_user_id (int): osu! id to insert
    discord_name (str): Discord id's associated name
    osu_name (str): osu! id's associated name
    
    Returns:
    None
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (discord_id, osu_id, discord_name, osu_name) VALUES (?, ?, ?, ?)", (discord_id, osu_user_id, discord_name, osu_name))
            conn.commit()
        except Exception as e:
            print_to_console(f"Inserting user failed due to: {e}")
        
def find_map(map_id: int):
    """
    Retrieves map data
    
    Parameters:
    map_id (int): Map id to search for
    
    Returns:
    tuple or None: Returns the tuple of the map id's data or nothing if map is not found 
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM maps WHERE map_id = ?", (map_id,))
            return cursor.fetchone()
        except Exception as e:
            print_to_console(f"Finding map failed due to: {e}")
    
def delete_user(discord_id: int):
    """
    Deletes user from database
    
    Parameters:
    discord_id (int): Discord id to delete
    
    Returns:
    None
    """
    with sqlite3.connect("osu_pass.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE discord_id = ?", (discord_id,))
            conn.commit()
        except Exception as e:
            print_to_console(f"Deleting user failed due to: {e}")
        
def calc_pp(map_info: tuple, mod_list: list[str], acc: float):
    """
    Calculates o!ppp
    
    Parameters:
    map_info (tuple): Map information from the database
    mod_list (list[str]): Cleaned list of mods to calculate pp for
    acc (float): Score accuracy
    
    Returns:
    float: Calculated o!ppp
    """
    best_acc = map_info[COLUMN_INDEX_MAP["top_acc"]]
    if not best_acc:
        best_acc = 0
    map_rank = map_info[COLUMN_INDEX_MAP["map_rank"]]
    if acc > best_acc:
        best_acc = acc
        initial_pp = map_info[COLUMN_INDEX_MAP["pp"]]
    else:
        initial_pp = 800 * math.pow((((best_acc/acc)*2)*map_rank), -0.3) + 200
    
    final_pp = initial_pp
    for mod in mod_list:
        final_pp += initial_pp * (map_info[MOD_COMBO_TO_INDEX[mod]] - 1)
        
    return float(round(final_pp, 2))
        
def calc_sr(map_info: tuple, mod_list: list[str]):
    """
    Calculates star rating
    
    Parameters:
    map_info (tuple): Map information from the database
    mod_list (list[str]): Cleaned list of mods to calculate pp for
    
    Returns:
    float: Calculated star rating
    """
    return float(map_info[MOD_COMBO_TO_INDEX[str(Mod(mod_list))]])

def update_map_pp(map_info: tuple):
    """
    Updates all of a specified map's pp values
    
    Parameters:
    map_info (tuple): Map data that is stored in the database
    
    Returns: 
    None
    """
    scores_list = get_all_scores(map_info[COLUMN_INDEX_MAP["map_id"]])
    for score in scores_list:
        mod_str = score[COLUMN_INDEX_SCORE["mods"]]
        mod_list = []
        for i in range(0, len(mod_str), 2):
            mod_temp = mod_str[i:i+2]
            if mod_temp == "NC":
                mod_list.append("DT")
            elif mod_temp in CLEANED_MODS:
                mod_list.append(mod_temp)
                
        new_pp = calc_pp(map_info, mod_list, score[COLUMN_INDEX_SCORE["acc"]])
        try:
            with sqlite3.connect("osu_pass.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET total_performance_points = total_performance_points - ? + ? WHERE osu_id = ?", (score[COLUMN_INDEX_SCORE["pp"]], new_pp, score[COLUMN_INDEX_SCORE["osu_id"]]))
                cursor.execute("UPDATE scores SET performance_points = ? WHERE score_id = ?", (new_pp, score[COLUMN_INDEX_SCORE["score_id"]]))
                conn.commit()
        except Exception as e:
            print_to_console(f"Failed to update score due to: {e}")
            
def insert_score(score: Score, pp: int = None):
    """
    Inserts a score into database
    
    Parameters:
    score (ossapi.Score): Score to insert
    pp (int, optional): Precalculated o!ppp value
    
    Returns:
    bool: If score insertion was successful
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        map_id = score.beatmap_id
        score_id = score.id
        user_id = score.user_id
        try:
            cursor.execute("SELECT * FROM scores WHERE user_osu_id = ? AND map_id = ?", (user_id, map_id))
            prev_score = cursor.fetchone()
        except Exception as e:
            print_to_console(f"Fetching previous score failed due to: {e}")
        mod_list = []
        mod_list_cleaned = []
        # Getting all mods, string is for db and list is for calcs
        for mod in score.mods:
            mod_name = mod.acronym
            mod_list.append(mod_name)
            if mod_name == "NC":
                mod_list_cleaned.append("DT")
            elif mod_name in CLEANED_MODS:
                mod_list_cleaned.append(mod_name)
        # ossapi breaks with CL so removing it    
        if "CL" in mod_list:
            mod_list.remove("CL")
        
        if mod_list:
            mod_str = str(Mod(''.join(mod_list)))
        else:
            mod_str = "NM"
        
        map_info = find_map(map_id)
        if pp:
            final_pp = pp
            star_rating = calc_sr(map_info, mod_list_cleaned)
        else:
            final_pp = calc_pp(map_info, mod_list_cleaned, score.accuracy)
            star_rating = calc_sr(map_info, mod_list_cleaned)
        
        if prev_score:
            if prev_score[3] >= final_pp:
                return False
            
            delete_score(prev_score)
        
        try:
            acc = round(float(score.accuracy), 2)
            cursor.execute("INSERT INTO scores (score_id, user_osu_id, map_id, performance_points, mods, star_rating, accuracy) VALUES (?, ?, ?, ?, ?, ?, ?)", (score_id, user_id, map_id, round(final_pp, 2), mod_str, round(star_rating,2), acc))  
            cursor.execute("UPDATE users SET total_performance_points = total_performance_points + ? WHERE osu_id = ?", (round(final_pp, 2), user_id))
            conn.commit()
            if not map_info[COLUMN_INDEX_MAP["top_acc"]]:
                cursor.execute("UPDATE maps SET top_acc = ? WHERE map_id = ?", (acc, map_id))
                conn.commit()
            elif acc > map_info[COLUMN_INDEX_MAP["top_acc"]]:
                cursor.execute("UPDATE maps SET top_acc = ? WHERE map_id = ?", (acc, map_id))
                conn.commit()
                update_map_pp(map_info)
            
                
        except Exception as e:
            print(f"sid: {score_id}, uid: {user_id}, mid: {map_id}, fpp: {final_pp}, mstr: {mod_str}, sr: {star_rating}, acc: {acc}")
            print_to_console(f"Score inseration failed due to: {e}")
            
        return True
            
def delete_score(score: tuple):
    """
    Deletes score from database
    
    Parameters:
    score (tuple): Score data from database of score to delete
    
    Returns:
    None
    """
    with sqlite3.connect("osu_pass.db") as conn:
        print("attempting to delete score")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET total_performance_points = total_performance_points - ? WHERE osu_id = ?", (score[3], score[1]))
            cursor.execute("DELETE FROM scores WHERE score_id = ?", (score[0],))
            conn.commit()
        except Exception as e:
            print_to_console(f"Deleting score failed due to: {e}")
           
def get_leaderboard():
    """
    Gets leaderboard
    
    Parameters:
    None
    
    Returns:
    list[tuple]: All users sorted by total o!ppp 
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT discord_name, total_performance_points FROM users ORDER BY total_performance_points DESC")
            return cursor.fetchall()
        except Exception as e:
            print_to_console(f"Fetching leaderboard data failed due to: {e}")
    
def get_top(user_id: int, stars: bool, reverse: bool):
    """
    Gets top scores for a user
    
    Parameters:
    user_id (int): osu! user id to fetch scores of
    stars (bool): Decides if to sort by stars instead of o!ppp
    reverse (bool): Decides if to sort in reverse order
    
    Returns:
    list[tuple]: List of specified user's top plays
    """
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
        try:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print_to_console(f"Fetching tops failed due to: {e}")
    
def get_all_maps():
    """
    Fetches all maps in database
    
    Parameters:
    None
    
    Returns:
    list[tuple]: List of all maps from the database with all the information
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM maps")
            return cursor.fetchall()
        except Exception as e:
            print_to_console(f"Getting all maps failed due to: {e}")
   
def get_all_scores(map_id: int):
    """
    Fetches all scores on a specified map
    
    Parameters:
    map_id (int): Map id you want to fetch
    
    Returns: 
    list[tuple]: Returns a list of scores from the database
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor();
        try:
            cursor.execute("SELECT * FROM scores WHERE map_id = ?", map_id)
            return cursor.fetchall()
        except Exception as e:
            print_to_console(f"Fetching all scores failed due to: {e}")
 
def get_all_users():
    """
    Fetch all osu! ids in database
    
    Parameters:
    None
    
    Returns:
    list[tuple]: List of all osu! ids from the database
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT osu_id FROM users")
            return cursor.fetchall()
        except Exception as e:
            print_to_console(f"Getting all users failed due to: {e}")
            
def get_score(score_id: int):
    """
    Fetches specific score base on a score id
    
    Parameters:
    score_id (int): id for the desired score
    
    Returns:
    tuple: The score's db row
    """
    with sqlite3.connect("osu_pass.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM scores WHERE score_id = ?", (score_id,))
            return cursor.fetchone()
        except Exception as e:
            print_to_console(f"Getting score failed due to: {e}")