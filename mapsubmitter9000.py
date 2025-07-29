import sqlite3
from osu_api import osu_api
import ossapi
import asyncio
# This entire code is a crime towards the osu api
conn = sqlite3.connect("osu_pass.db")
cursor = conn.cursor()

map_id = 5041003
pp = 10000

async def get_map():
    return await osu_api.beatmap(map_id)

map:ossapi.Beatmap = asyncio.run(get_map())

async def get_sr(mods: str):
    map_attr = await osu_api.beatmap_attributes(map.id, mods=ossapi.Mod(mods))
    return map_attr.attributes.star_rating

sr_hr = asyncio.run(get_sr("HR"))
sr_dt = asyncio.run(get_sr("DT"))
sr_ez = asyncio.run(get_sr("EZ"))
sr_fl = asyncio.run(get_sr("FL"))
sr_ht = asyncio.run(get_sr("HT"))
sr_htez = asyncio.run(get_sr("HTEZ"))
sr_hthr = asyncio.run(get_sr("HTHR"))
sr_hrdt = asyncio.run(get_sr("HRDT"))
sr_ezdt = asyncio.run(get_sr("EZDT"))
sr_dtfl = asyncio.run(get_sr("DTFL"))
sr_hrfl = asyncio.run(get_sr("HRFL"))
sr_ezfl = asyncio.run(get_sr("EZFL"))
sr_htfl = asyncio.run(get_sr("HTFL"))
sr_hrdtfl = asyncio.run(get_sr("HRDTFL"))
sr_ezdtfl = asyncio.run(get_sr("EZDTFL"))
sr_hrhtfl = asyncio.run(get_sr("HRHTFL"))
sr_ezhtfl = asyncio.run(get_sr("EZHTFL"))

cursor.execute(
    """
    INSERT INTO maps (
        map_id, performance_points, map_name, diff_name, sr_nm,
        sr_hr, sr_dt, sr_ez, sr_fl, sr_ht,
        sr_htez, sr_hthr, sr_hrdt, sr_ezdt, sr_dtfl,
        sr_hrfl, sr_ezfl, sr_htfl, sr_hrdtfl, sr_ezdtfl,
        sr_hrhtfl, sr_ezhtfl
    ) VALUES (?, ?, ?, ?, ?,
              ?, ?, ?, ?, ?,
              ?, ?, ?, ?, ?,
              ?, ?, ?, ?, ?,
              ?, ?)
    """,
    (
        map_id, pp, map._beatmapset.title, map.version, round(map.difficulty_rating, 2),
        round(sr_hr, 2), round(sr_dt, 2), round(sr_ez, 2), round(sr_fl, 2), round(sr_ht, 2),
        round(sr_htez, 2), round(sr_hthr, 2), round(sr_hrdt, 2), round(sr_ezdt, 2), round(sr_dtfl, 2),
        round(sr_hrfl, 2), round(sr_ezfl, 2), round(sr_htfl, 2), round(sr_hrdtfl, 2), round(sr_ezdtfl, 2),
        round(sr_hrhtfl, 2), round(sr_ezhtfl, 2)
    )
)

conn.commit()
conn.close()