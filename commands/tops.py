# TODO: Fetch all users sorted by greatest o!ppp
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import get_leaderboard, get_top, search_disc_user, search_osu_user, get_all_scores, find_map
from console import print_to_console
from ossapi import Beatmap, BeatmapCompact, Beatmapset
from page_view import PageView

class Tops(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="map_leaderboard", description="Displays map leaderboard")
    async def map_leaderboard(self, interaction: discord.Interaction, map_url: str = None, map_id: str = None, sort_by_acc: bool = False, reversed_order: bool = False):
        if not (map_url or map_id):
            print_to_console(f"User {interaction.user.id} is leaderboard request failed because they added neither a url or id")
            embed = discord.Embed(title="Not Enough Arguments", description="Please enter a map id or map link", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        
        if map_url and map_id:
            print_to_console(f"User {interaction.user.id} is leaderboard request failed because they added both a url and id")
            embed = discord.Embed(title="Too Many Arguments", description="Please either use the map id or map link, not both", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        
        map_id2 = None
        if map_url:
            map_id2 = map_url.split("/")[-1]
        else:
            map_id2 = map_id
        
        try:
            map_data = await osu_api.beatmap(beatmap_id=map_id2)
        except Exception as e:
            print_to_console(f"User {interaction.user.id} exception caught during map leaderboard request: {e}")
            embed = discord.Embed(title="Error", description=f"An error occured, make sure the map id or map link are correct!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
            
        if find_map(map_data.id):
            leaderboard_data = get_all_scores(map_data.id, sort_by_pp=(not sort_by_acc), reverse_order=reversed_order)
            map_img = map_data.beatmapset().covers.list
            pages: list[discord.Embed] = []
            for i in range(0, len(leaderboard_data), 10):
                chunk = leaderboard_data[i:i+10]
                lines = [f"{i + j + 1}. **{search_osu_user(entry[1])[4]}**\n\u00A0\u00A0\u00A0\u00A0+{entry[4]} - {round(entry[3], 2)}ppp - {round(entry[6], 2)}%" for j, entry in enumerate(chunk)]
                embed = discord.Embed(
                    title=f"Leaderboard for {map_data.beatmapset().title} [{map_data.version}]",
                    url=map_data.url,
                    description="\n".join(lines),
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=map_img)
                embed.set_footer(text=f"Page {(i // 10) + 1} of {(len(leaderboard_data) - 1) // 10 + 1}")
                pages.append(embed)
                
            if len(pages) == 0:
                embed = discord.Embed(title="No Scores", description="There are no scores to display", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
            else:
                view = PageView(user_id=interaction.user.id, pages=pages)
                await interaction.response.send_message(embed=pages[0], view=view)
            
            print_to_console(f"User {interaction.user.id}'s map leaderboard request was successful")
            return
        else:
            embed = discord.Embed(title="Not a Valid Map", description=f"**{map_data.beatmapset.title} [{map_data.version}]** is not a valid map", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            print_to_console(f"User {interaction.user.id}'s tops request failed because their account is not linked")
            return
    
    @map_leaderboard.error
    async def map_leaderboard_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed(title="SOMETHING SHIT ITSELF", description=f"SOMETHING BROKE pls @ cloudiees :)\n\n{error}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        print_to_console(f"User {interaction.user.id}'s map leaderboard request errored because {error}")
        return
        
    
    @app_commands.command(name="leaderboard", description="Displays global leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        print_to_console(f"User {interaction.user.id} is attempting to access global leaderboard")
        leaderboard_data = await asyncio.to_thread(get_leaderboard)
        pages: list[discord.Embed] = []

        for i in range(0, len(leaderboard_data), 10):
            chunk = leaderboard_data[i:i+10]
            lines = [f"{i + j + 1}. **{entry[0]}** - {round(entry[1],2)}ppp" for j, entry in enumerate(chunk)]
            embed = discord.Embed(
                title="Leaderboard",
                description="\n".join(lines),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Page {(i // 10) + 1} of {(len(leaderboard_data) - 1) // 10 + 1}")
            pages.append(embed)
        if len(pages) == 0:
            embed = discord.Embed(title="No Profiles", description="There are no profiles to display", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
        else:
            view = PageView(user_id=interaction.user.id, pages=pages)
            await interaction.response.send_message(embed=pages[0], view=view)
        print_to_console(f"User {interaction.user.id}'s request was successful")
        return
    
    @leaderboard.error
    async def leaderboard_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed(title="SOMETHING SHIT ITSELF", description=f"SOMETHING BROKE pls @ cloudiees :)\n\n{error}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        print_to_console(f"User {interaction.user.id}'s leaderboard request errored because {error}")
        return
    
    @app_commands.command(name="top", description="Get top plays")
    @app_commands.describe(user="osu! username", sort_by_stars="Sort by stars instead of ppp", sort_reverse="Sort in reverse order")
    async def top(self, interaction: discord.Interaction, user: str = None, sort_by_stars: bool = False, sort_reverse: bool = False):
        print_to_console(f"User {interaction.user.id} is attempting to access their top plays")
        user_osu_id = None
        osu_user_name = None
        osu_user_img = None
        if user is None:
            user_data = (await asyncio.to_thread(search_disc_user, interaction.user.id))
            if user_data is None:
                embed = discord.Embed(title="Not Yet Linked", description="Please link your account before looking at your top plays by using `/link <osu_username>`.", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
                print_to_console(f"User {interaction.user.id}'s tops request failed because their account is not linked")
                return
            osu_user_data = await osu_api.user(user_data[1])
            osu_user_img = osu_user_data.avatar_url
            osu_user_name = user_data[4]
            user_osu_id = user_data[1]
            
        else:
            try:
                osu_user_data = await osu_api.user(user)
            except Exception as e:
                embed = discord.Embed(title="Error", description="Something went wrong. Please make sure you entered the username in correctly.", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
                print_to_console(f"User {interaction.user.id}'s tops request failed because: {e}")
                return
            
            user_data = (await asyncio.to_thread(search_osu_user, osu_user_data.id))
            if user_data:
                osu_user_img = osu_user_data.avatar_url
                osu_user_name = user_data[4]
                user_osu_id = user_data[1]
                
            else:
                embed = discord.Embed(title="User Not Linked", description="This user has not linked their account.", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
                return
        
        top_data = await asyncio.to_thread(get_top, user_osu_id, sort_by_stars, sort_reverse)
        pages: list[discord.Embed] = []

        for i in range(0, len(top_data), 10):
            chunk = top_data[i:i+10]
            lines = [f"{i + j + 1}. **{entry[0]} [{entry[1]}]**\n\u00A0\u00A0\u00A0\u00A0+{entry[3]} {entry[2]}⭐ - {round(entry[4], 2)}ppp - {round(entry[5], 2)}%" for j, entry in enumerate(chunk)]
            embed = discord.Embed(
                title=f"{osu_user_name}'s Top Plays",
                description="\n".join(lines),
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=osu_user_img)
            embed.set_footer(text=f"Page {(i // 10) + 1} of {(len(top_data) - 1) // 10 + 1}")
            pages.append(embed)
        if len(pages) == 0:
            embed = discord.Embed(title="No Scores", description="There are no scores to display", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
        else:
            view = PageView(user_id=interaction.user.id, pages=pages)
            await interaction.response.send_message(embed=pages[0], view=view)
        print_to_console(f"User {interaction.user.id}'s tops request was successful")
        
    @top.error
    async def top_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed(title="SOMETHING SHIT ITSELF", description=f"SOMETHING BROKE pls @ cloudiees :)\n\n{error}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        print_to_console(f"User {interaction.user.id}'s top request errored because {error}")
        return
        
async def setup(bot):
    await bot.add_cog(Tops(bot))