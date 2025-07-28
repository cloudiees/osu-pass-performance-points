# TODO: Submit a score
import asyncio
import discord
from ossapi import Mod, Score
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import search_disc_user, find_map, insert_score

LEGAL_MODS = ["EZ","HD","HR","SD","DT","HT","NC","FL","SO","PF","CL"]

def find_illegal_mod(score: Score):
    contains_cl = False
    print("starting loop")
    print(f"mods: {score.mods}")
    if score.mods:
        for mod in score.mods:
            print(f"looking at {mod.acronym}")
            if mod.acronym not in LEGAL_MODS:
                print("illegal mod located")
                return mod.acronym
            elif mod.acronym == "CL":
                print("found cl")
                contains_cl = True
            # Enable if I want love to be included (would also allow lazer scores as long as they aren't using mod settings)
            # if mod.settings:
            #     print("found modified mod")
            #     return "-S"
            print(f"done looking at {mod}")
        if not contains_cl:
            print("No classic found")
            return "-CL"

async def illegal_mod_detection(score: Score, interaction: discord.Interaction):
    print(f"locating illegal mod for {score}")
    illegal_mod = find_illegal_mod(score)
    print("scanned all mods")
    if illegal_mod:
        print("illegal mod located")
        if illegal_mod == "-CL":
            print("no cl found")
            await interaction.response.send_message("This score is not set on stable.")
        # Enable if I want loved maps to be ranked
        # elif illegal_mod == "-S":
        #     print("mod setting found")
        #     await interaction.response.send_message("This score uses mod settings.")
        else:
            print("other illegal mod")
            await interaction.response.send_message(f"{illegal_mod} is an illegal mod, score will not be submitted.")
        return True
    print("no illegal mods")
    return False

def get_mod_list(score: Score):
    mod_list = []
    for mod in score.mods:
        if mod.acronym != "CL":
            mod_list.append(mod.acronym)
            
    return mod_list

class Submit(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="submit", description="todo")
    @app_commands.describe(score_id="score id")
    async def submit(self, interaction: discord.Interaction, score_id: int):
        print("starting submission")
        score = await osu_api.score(score_id)
        # print(f"got score info for {score.beatmap_id} which is {isinstance(score.beatmap_id, int)}")
        user_db_row = await asyncio.to_thread(search_disc_user, interaction.user.id)
        if not user_db_row:
            await interaction.response.send_message("Please link your account before submitting a score!")
        elif score.user_id != user_db_row[1]:
            user = await osu_api.user(user_db_row[1])
            await interaction.response.send_message(f"Sorry, but your discord account is linked to {user.username}. The score you are trying to submit is from {score._user.username}.")
            return
        
        if await asyncio.to_thread(find_map, score.beatmap_id):
            print("map in score db")
            if await illegal_mod_detection(score, interaction):
                print("illegal mod found")
                return
            print("no illegal mods found")
            if score.pp:
                print("score has pp")
                try:
                    await asyncio.to_thread(insert_score, score)
                    print("inserted score")
                    await interaction.response.send_message("Score submitted!")
                except Exception as e:
                    await interaction.response.send_message(str(e))
                
                return
            else:
                await interaction.response.send_message("HOW DARE YOU TRY TO SEND A LAZER SCORE YOU HEATHEN")
                return
                
        else:
            # print("map not in db")
            await interaction.response.send_message("This map is not a valid pass map.")
    
    @app_commands.command(name="submit_recent", description="todo")
    async def submit_recent(self, interaction: discord.Interaction):
        user_db_row = await asyncio.to_thread(search_disc_user, interaction.user.id)
        if user_db_row:
            recent_score = (await osu_api.user_scores(user_db_row[1], "recent", include_fails=False, mode="osu", limit=1, legacy_only=True))[0]
            if await asyncio.to_thread(find_map, recent_score.beatmap_id):
                if await illegal_mod_detection(recent_score, interaction):
                    print("illegal mod found")
                    return
                
                print("attempting to submit score")
                try:
                    await asyncio.to_thread(insert_score, recent_score)
                    await interaction.response.send_message("Score submitted!")
                except Exception as e:
                    await interaction.response.send_message(str(e))
                    
                return
                
            await interaction.response.send_message("This map is not a valid pass map.")
            return
        await interaction.response.send_message("Please link your account using `/link <osu!username>` before using this command!")
        
async def setup(bot):
    await bot.add_cog(Submit(bot))