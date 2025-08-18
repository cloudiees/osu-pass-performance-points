import sqlite3
from osu_api import osu_api
import ossapi
import asyncio
import math
import database
import argparse
import pyttanko
import requests
# This entire code is a crime towards the osu api
parser = argparse.ArgumentParser(description="idk man")

parser.add_argument(
    "-m", "--mapid", 
    type=int, 
    help="Map ID"
)
parser.add_argument(
    "-r", "--rank",
    type=int,
    help="Map Rank"
)

args = parser.parse_args()

async def get_map(map_id):
    """
    Gets map info
    
    Parameters:
    map_id (int): Map's id
    
    Returns: 
    ossapi.Beatmap: Returns beatmap of specified the id
    """
    return await osu_api.beatmap(map_id)

async def get_sr(mods: str, map: ossapi.Beatmap):
    """
    Gets star rating of a specific mod combo for a map
    
    Parameters:
    map (ossapi.Beatmap): Beatmap to get star rating of
    mods (str): Mod combo string
    
    Returns: 
    tuple: Calculated star rating, calculated fl mult, calculated hr mult, calculated dt mult
    """
    map_attr = await osu_api.beatmap_attributes(map.id, mods=ossapi.Mod(mods))
    return round(map_attr.attributes.star_rating, 2)

def calc_mults(map: ossapi.Beatmap):
    od = map.difficulty_rating
    cs = map.cs
    hp = map.drain
    ar = map.ar
    _, ar_hr, od_hr, cs_hr, hp_hr = pyttanko.mods_apply(mods=pyttanko.mods_from_str("HR"), ar=ar, od=od, cs=cs, hp=hp)
    hr_mult = 1 + (od_hr - od) * .05 + (cs_hr - cs) * .1 + (hp_hr - hp) * .05
    _, ar_dt, od_dt, cs_dt, hp_dt = pyttanko.mods_apply(mods=pyttanko.mods_from_str("DT"), ar=ar, od=od, cs=cs, hp=hp)
    dt_mult = 1.5 + (od_dt - od) * .15 + (cs_dt - cs) * .25 + (hp_dt - hp) * .15
    fl_mult = round(1.4 + ((map.total_length / 60) * .1), 2)
    return (round(hr_mult,2), round(dt_mult,2), round(fl_mult,2))

def submit_map(map_id:int,rank:int):
    with sqlite3.connect("osu_pass.db") as conn:
        map:ossapi.Beatmap = asyncio.run(get_map(map_id))
        print(f"Submitting {map.id} [{map.version}]")
        cursor = conn.cursor()
        sr_hr = asyncio.run(get_sr("HR", map))
        sr_dt = asyncio.run(get_sr("DT", map))
        sr_fl = asyncio.run(get_sr("FL", map))
        sr_hrdt = asyncio.run(get_sr("HRDT", map))
        sr_dtfl = asyncio.run(get_sr("DTFL", map))
        sr_hrfl = asyncio.run(get_sr("HRFL", map))
        sr_hrdtfl = asyncio.run(get_sr("HRDTFL", map))
        hr_mult, dt_mult, fl_mult = calc_mults(map)
        cursor.execute(
            """
            INSERT INTO maps (
                map_id, map_rank, map_name, diff_name, sr_nm,
                sr_hr, sr_dt, sr_fl, sr_hrdt, sr_dtfl,
                sr_hrfl, sr_hrdtfl, performance_points, hr_mult, dt_mult, fl_mult
            ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?)
            """,
            (
                map_id, rank, map._beatmapset.title, map.version, round(map.difficulty_rating, 2),
                sr_hr, sr_dt, sr_fl, sr_hrdt, sr_dtfl, sr_hrfl, 
                sr_hrdtfl, round(800 * math.pow((2*rank), -0.3) + 200, 2), hr_mult, dt_mult, fl_mult
            )
        )
        conn.commit()
        
if args.mapid and args.rank:
    submit_map(args.mapid, args.rank)
