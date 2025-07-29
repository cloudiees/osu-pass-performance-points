from bot import bot
import time
import asyncio
from db_commands import get_all_users, find_map, insert_score
from osu_api import osu_api

async def scan_recent():
    await bot.wait_until_ready()
    while not bot.is_closed():
        print(f"[{time.strftime('%X')}] running auto scan...")
        
        all_users = get_all_users()
        print("got all users")
        for user in all_users:
            print(f"submitting scores for {user[0]}")
            user_scores = await osu_api.user_scores(user[0], "recent", include_fails=False, mode="osu", limit=15, legacy_only=True)
            # print(f"scores: {user_scores}")
            for score in user_scores:
                if find_map(score.beatmap_id):
                    try:
                        print(f"attempt to submit score {score.beatmapset.title}")
                        await asyncio.to_thread(insert_score,score)
                        print("score submission successful")
                    except Exception as e:
                        print(f"there is a better score alr or: {e}")
                        continue
            
        print("i slep")
        await asyncio.sleep(600)
