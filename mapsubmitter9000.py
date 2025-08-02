import sqlite3
from osu_api import osu_api
import ossapi
import asyncio
import math
import database
# This entire code is a crime towards the osu api


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
    float: Calculated star rating
    """
    map_attr = await osu_api.beatmap_attributes(map.id, mods=ossapi.Mod(mods))
    return map_attr.attributes.star_rating

def submit_map(map_id:int,rank:int):
    with sqlite3.connect("osu_pass.db") as conn:
        map:ossapi.Beatmap = asyncio.run(get_map(map_id))
        print(f"Submitting {map.id} [{map.version}]")
        cursor = conn.cursor()
        sr_hr = asyncio.run(get_sr("HR", map))
        sr_dt = asyncio.run(get_sr("DT", map))
        # sr_ez = asyncio.run(get_sr("EZ", map))
        sr_fl = asyncio.run(get_sr("FL", map))
        # sr_ht = asyncio.run(get_sr("HT", map))
        # sr_htez = asyncio.run(get_sr("HTEZ", map))
        # sr_hthr = asyncio.run(get_sr("HTHR", map))
        sr_hrdt = asyncio.run(get_sr("HRDT", map))
        # sr_ezdt = asyncio.run(get_sr("EZDT", map))
        sr_dtfl = asyncio.run(get_sr("DTFL", map))
        sr_hrfl = asyncio.run(get_sr("HRFL", map))
        # sr_ezfl = asyncio.run(get_sr("EZFL", map))
        # sr_htfl = asyncio.run(get_sr("HTFL", map))
        sr_hrdtfl = asyncio.run(get_sr("HRDTFL", map))
        # sr_ezdtfl = asyncio.run(get_sr("EZDTFL", map))
        # sr_hrhtfl = asyncio.run(get_sr("HRHTFL", map))
        # sr_ezhtfl = asyncio.run(get_sr("EZHTFL", map))

        # cursor.execute(
        #     """
        #     INSERT INTO maps (
        #         map_id, map_rank, map_name, diff_name, sr_nm,
        #         sr_hr, sr_dt, sr_ez, sr_fl, sr_ht,
        #         sr_htez, sr_hthr, sr_hrdt, sr_ezdt, sr_dtfl,
        #         sr_hrfl, sr_ezfl, sr_htfl, sr_hrdtfl, sr_ezdtfl,
        #         sr_hrhtfl, sr_ezhtfl, pp
        #     ) VALUES (?, ?, ?, ?, ?,
        #               ?, ?, ?, ?, ?,
        #               ?, ?, ?, ?, ?,
        #               ?, ?, ?, ?, ?,
        #               ?, ?, ?)
        #     """,
        #     (
        #         map_id, rank, map._beatmapset.title, map.version, round(map.difficulty_rating, 2),
        #         round(sr_hr, 2), round(sr_dt, 2), round(sr_ez, 2), round(sr_fl, 2), round(sr_ht, 2),
        #         round(sr_htez, 2), round(sr_hthr, 2), round(sr_hrdt, 2), round(sr_ezdt, 2), round(sr_dtfl, 2),
        #         round(sr_hrfl, 2), round(sr_ezfl, 2), round(sr_htfl, 2), round(sr_hrdtfl, 2), round(sr_ezdtfl, 2),
        #         round(sr_hrhtfl, 2), round(sr_ezhtfl, 2), round(800 * math.pow((2*rank), -0.3) + 200, 2)
        #     )
        # )

        cursor.execute(
            """
            INSERT INTO maps (
                map_id, map_rank, map_name, diff_name, sr_nm,
                sr_hr, sr_dt, sr_fl, sr_hrdt, sr_dtfl,
                sr_hrfl, sr_hrdtfl, performance_points
            ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?)
            """,
            (
                map_id, rank, map._beatmapset.title, map.version, round(map.difficulty_rating, 2),
                round(sr_hr, 2), round(sr_dt, 2), round(sr_fl, 2), round(sr_hrdt, 2), round(sr_dtfl), round(sr_hrfl, 2), 
                round(sr_hrdtfl, 2), round(800 * math.pow((2*rank), -0.3) + 200, 2)
            )
        )
        conn.commit()