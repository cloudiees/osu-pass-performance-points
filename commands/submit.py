# TODO: Submit a score
import asyncio
import discord
from ossapi import Mod, Score
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import search_disc_user, find_map, insert_score, get_all_maps, calc_pp, get_score
from console import print_to_console
import time

# Comprehensive list of legal mods
LEGAL_MODS = ["HD","HR","SD","DT","NC","FL","SO","PF","CL"]

# Cooldown user dictionary for auto submit
user_cooldowns = {}

# Cooldown for auto submit
COOLDOWN_SECONDS = 3600

def find_illegal_mod(score: Score):
    """
    Given a score it goes through the mods and finds if the mod combination used is legal

    Parameters:
    score (ossapi.Score): Score to look through

    Returns:
    str or None: The violating mod, or "-CL" which means no classic mod was found, or nothing to indicate no illegal mods were found
    """
    contains_cl = False
    if score.mods:
        for mod in score.mods:
            if mod.acronym not in LEGAL_MODS:
                return mod.acronym
            elif mod.acronym == "CL":
                contains_cl = True
        if not contains_cl:
            return "-CL"

async def illegal_mod_detection(score: Score, interaction: discord.Interaction):
    """
    Given a score it goes through the mods and finds if the mod combination used is legal and outputs a message to discord

    Parameters:
    score (ossapi.Score): Score to look through
    interaction (discord.Interaction): Interaction to send a message through 

    Returns:
    bool: If a illegal mod was found
    """
    illegal_mod = find_illegal_mod(score)
    if illegal_mod:
        if illegal_mod == "-CL":
            embed = discord.Embed(title="Invalid Score", description="This score was not set on stable.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Invalid Score", description=f"**{illegal_mod}** is an illegal mod, score will not be submitted.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        return True
    return False

def get_mod_list(score: Score):
    """
    Looks through a score and returns the mod list, removing CL to ensure no issues with the ossapi

    Parameters:
    score (ossapi.Score): Score to look through

    Returns:
    list[str]: A list of mod acronyms that were used in the score
    """
    mod_list = []
    for mod in score.mods:
        if mod.acronym != "CL":
            mod_list.append(mod.acronym)
            
    return mod_list

def illegal_mod_and_clean_mod_list(score: Score):
    """
    Given a score it goes through the mods and finds if the mod combination used is legal

    Parameters:
    score (ossapi.Score): Score to look through
    
    Returns:
    list[str] or None: If there is an illegal mod nothing is returned, otherwise the list of mod acronyms used in the score are returned
    """
    contains_cl = False
    mod_list = []
    if score.mods:
        for mod in score.mods:
            if mod.acronym not in LEGAL_MODS:
                return
            elif mod.acronym == "CL":
                contains_cl = True
            
            if mod.acronym == "NC":
                mod_list.append("DT")
            elif mod.acronym in LEGAL_MODS:
                mod_list.append(mod.acronym)
            
        if not contains_cl:
            return
        
    return mod_list

class Submit(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="submit", description="todo")
    @app_commands.describe(score_id="score id")
    async def submit(self, interaction: discord.Interaction, score_id: int):
        print_to_console(f"User {interaction.user.id} is attempting to submit a score")
        try:
            score = await osu_api.score(score_id)
        except Exception as e:
            embed = discord.Embed(title="Error", description="Please ensure that you submitted a score id!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            print_to_console(f"User {interaction.user.id}'s score submit request failed due to: {e}")
            return
            
        user_db_row = await asyncio.to_thread(search_disc_user, interaction.user.id)
        if not user_db_row:
            embed = discord.Embed(title="Not Yet Linked", description="Please link your account before submitting a score by using `/link <osu_username>`.", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            print_to_console(f"User {interaction.user.id}'s score submit request failed because their account was not yet linked")
            return
        elif score.user_id != user_db_row[1]:
            user = await osu_api.user(user_db_row[1])
            embed = discord.Embed(title="Invalid User", description=f"Your discord account is linked to {user.username}. The score you are trying to submit is from {score._user.username}.", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            print_to_console(f"User {interaction.user.id}'s score submit request failed because they attempted to submit a score from another user")
            return
        
        if await asyncio.to_thread(find_map, score.beatmap_id):
            if await illegal_mod_detection(score, interaction):
                print_to_console(f"User {interaction.user.id}'s score submit request failed because there was an illegal mod")
                return
            if score.pp:
                score_submitted = await asyncio.to_thread(insert_score, score)
                if score_submitted:
                    score_data = get_score(score.id)
                    embed = discord.Embed(title="Score Submitted", description=f"Successfully submitted **{score.beatmapset.title} [{score.beatmap.version}]** +{score_data[4]}", color=discord.Color.green())
                    embed.add_field(name="", value=f"{round(score_data[3],2)}ppp - {score_data[5]}⭐ - {round(score_data[6], 2)}%")
                    embed.set_image(url=score.beatmapset.covers.cover_2x)
                    await interaction.response.send_message(embed=embed)
                    print_to_console(f"User {interaction.user.id}'s score submit request was successful")
                    return
                else:
                    embed = discord.Embed(title="Lower ppp Score", description=f"You already have a score on **{score.beatmapset.title} [{score.beatmap.version}]** with a higher or equal ppp value!", color=discord.Color.orange())
                    await interaction.response.send_message(embed=embed)
                    print_to_console(f"User {interaction.user.id}'s score submit request failed because a higher pp score is in the database")
                    return
                
            else:
                embed = discord.Embed(title="Unranked Score", description="This score is not ranked.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                print_to_console(f"User {interaction.user.id}'s score submit request failed because the score is unranked")
                return
                
        else:
            embed = discord.Embed(title="Invalid Map", description=f"**{score.beatmapset.title} [{score.beatmap.version}]** is not a valid map.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            print_to_console(f"User {interaction.user.id}'s score submit request failed because the map is not in the database")
            return
    
    @submit.error
    async def submit_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed(title="SOMETHING SHIT ITSELF", description=f"SOMETHING BROKE pls @ cloudiees :)\n\n{error}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        print_to_console(f"User {interaction.user.id}'s score submit request errored because {error}")
        return
    
    @app_commands.command(name="autosubmit", description="todo")
    async def autosubmit(self, interaction: discord.Interaction):
        print_to_console(f"User {interaction.user.id} is attempting to auto submit scores")
        user_disc_id = interaction.user.id
        curr_time = time.time()
        if user_disc_id in user_cooldowns:
            last_used = user_cooldowns[user_disc_id]
            if curr_time - last_used < COOLDOWN_SECONDS:
                remaining_seconds = int(COOLDOWN_SECONDS - (curr_time - last_used))                
                hours = remaining_seconds // 3600
                minutes = (remaining_seconds % 3600) // 60
                seconds = remaining_seconds % 60
                resp_str = f"Please wait"
                if hours > 0:
                    resp_str += f" {hours} hour"
                if minutes > 0 or hours > 0:
                    resp_str += f" {minutes} minutes"
                resp_str += f" {seconds} seconds before using this command again!"
                embed = discord.Embed(title="Command on Cooldown", description=resp_str, color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                print(f"{resp_str} + actual seconds: {remaining_seconds}")
                print_to_console(f"User {interaction.user.id}'s auto submit request was denied due to cooldown")
                return
        
        user_db_row = await asyncio.to_thread(search_disc_user, interaction.user.id)
        if user_db_row:
            embed = discord.Embed(title="Auto Submit (0%)", description="Beginning auto submit...", color=discord.Color.yellow())
            user_cooldowns[user_disc_id] = curr_time
            message_log = "Beginning auto submit...\n"
            map_list = get_all_maps()
            await interaction.response.defer(thinking=True)
            map_counter = 0
            map_len = len(map_list)
            embed = discord.Embed(title="Auto Submit (0%)", description="Beginning auto submit...", color=discord.Color.yellow())
            await interaction.edit_original_response(embed=embed)
            for map in map_list:
                if map_counter % 20 == 0 and map_counter > 0:
                    print_to_console(f"User {interaction.user.id}'s auto submit request is sleeping to stop API overload")
                    for i in range(20, 0, -1):
                        embed.title = f"Auto Submit ({int((map_counter/map_len)*100)}%)"
                        embed.description = f"Waiting {i} seconds so the osu!api doesn't get mad..."
                        await interaction.edit_original_response(embed=embed)
                        await asyncio.sleep(1)
                    
                map_counter += 1
                message_log += f"Checking map id {map[0]}...\n"
                embed.description = f"Checking map id {map[0]}..."
                embed.title = f"Auto Submit ({int((map_counter/map_len)*100)}%)"
                await interaction.edit_original_response(embed=embed)
                best_score:Score = None
                best_score_pp = -1
                score_list = await osu_api.beatmap_user_scores(map[0], user_db_row[1])
                if not score_list:
                    continue
                
                for score in score_list:
                    mod_list = illegal_mod_and_clean_mod_list(score)
                    if mod_list:
                        mod_list.remove("CL")
                        pp = calc_pp(map, mod_list, score.accuracy * 100)
                        if pp and pp > best_score_pp:
                            best_score = score
                            best_score_pp = pp
                            
                            
                if best_score:
                    await asyncio.to_thread(insert_score, best_score)
                    message_log += f"Submitted score for map id {map[0]}\n"
                    embed.description = f"Submitted score for map id {map[0]}..."
                    await interaction.edit_original_response(embed=embed)
                
                await asyncio.sleep(1)
            
            message_log += "Auto submission compelete!"
            embed.title = f"Auto Submit (100%)"
            embed.description = "Auto submission complete!"
            embed.color = discord.Color.green()
            print_to_console(f"User {interaction.user.id}'s auto submission request was completed")
            await interaction.edit_original_response(embed=embed)
    
        else:
            embed = discord.Embed(title="Not Yet Linked", description="Please link your account before submitting a score by using `/link <osu_username>`.", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            print_to_console(f"User {interaction.user.id}'s auto submission request failed because their account was not linked")
            return
    
    @autosubmit.error
    async def autosubmit_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed(title="SOMETHING SHIT ITSELF", description=f"SOMETHING BROKE pls @ cloudiees :)\n\n{error}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        print_to_console(f"User {interaction.user.id}'s autosubmit request errored because {error}")
        return
    
    @app_commands.command(name="submit_recent", description="todo")
    async def submit_recent(self, interaction: discord.Interaction):
        user_db_row = await asyncio.to_thread(search_disc_user, interaction.user.id)
        if user_db_row:
            recent_score = (await osu_api.user_scores(user_db_row[1], "recent", include_fails=False, mode="osu", limit=1, legacy_only=True))[0]
            if not recent_score:
                embed = discord.Embed(title="No Scores Found", description="No recent scores found, please try again later", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
            if await asyncio.to_thread(find_map, recent_score.beatmap_id):
                if await illegal_mod_detection(recent_score, interaction):
                    print_to_console(f"User {interaction.user.id}'s recent score submission request failed because an illegal mod was found")
                    return
                
                score_submitted = await asyncio.to_thread(insert_score, recent_score)
                if score_submitted:
                    score_data = get_score(recent_score.id)
                    embed = discord.Embed(title="Score Submitted", description=f"Successfully submitted **{recent_score.beatmapset.title} [{recent_score.beatmap.version}]** +{score_data[4]}", color=discord.Color.green())
                    embed.add_field(name="", value=f"{round(score_data[3],2)}ppp - {score_data[5]}⭐ - {round(score_data[6], 2)}%")
                    embed.set_image(url=recent_score.beatmapset.covers.card_2x)
                    await interaction.response.send_message(embed=embed)
                    print_to_console(f"User {interaction.user.id}'s score submit request was successful")
                    print_to_console(f"User {interaction.user.id}'s recent score submission request was successful")
                else:
                    embed = discord.Embed(title="Lower ppp Score", description=f"You already have a score on **{recent_score.beatmapset.title} [{recent_score.beatmap.version}]** with a higher or equal ppp value!", color=discord.Color.orange())
                    await interaction.response.send_message(embed=embed)
                    print_to_console(f"User {interaction.user.id}'s recent score submission request failed due to lower pp score")
                    
                return
                
            embed = discord.Embed(title="Invalid Map", description=f"**{recent_score.beatmapset.title} [{recent_score.beatmap.version}]** is not a valid map.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            print_to_console(f"User {interaction.user.id}'s recent score submission request failed due to the map not being in the database")
            return
        
        embed = discord.Embed(title="Not Yet Linked", description="Please link your account before submitting a score by using `/link <osu_username>`.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)
        print_to_console(f"User {interaction.user.id}'s recent score submission request failed because their account is not linked")
        return
        
    @submit_recent.error
    async def submit_recent_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed(title="SOMETHING SHIT ITSELF", description=f"SOMETHING BROKE pls @ cloudiees :)\n\n{error}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        print_to_console(f"User {interaction.user.id}'s submit recent request errored because {error}")
        return    
        
async def setup(bot):
    await bot.add_cog(Submit(bot))