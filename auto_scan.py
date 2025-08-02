from bot import bot
import time
import asyncio
from db_commands import get_all_users, find_map, insert_score
from osu_api import osu_api
from console import print_to_console

async def scan_recent():
    """
    Scans all user's latest scores
    
    Parameters:
    None
    
    Returns:
    None
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        print_to_console("Running auto scan...")
        all_users = get_all_users()
        for user in all_users:
            user_scores = await osu_api.user_scores(user[0], "recent", include_fails=False, mode="osu", limit=15, legacy_only=True)
            for score in user_scores:
                if find_map(score.beatmap_id):
                    await asyncio.to_thread(insert_score,score)
            await asyncio.sleep(0.5)
            
        print_to_console("Auto scan complete!")
        await asyncio.sleep(600)
