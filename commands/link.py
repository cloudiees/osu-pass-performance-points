import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import search_disc_user, search_osu_user, insert_user, delete_user

class Link(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="link", description="links osu! profile to your discord")
    @app_commands.describe(user="Your osu! username")
    async def link(self, interaction: discord.Interaction, user: str):
        # print("trying to execute")
        if await asyncio.to_thread(search_disc_user, interaction.user.id):
            embed = discord.Embed(title="Already Linked", description="This discord account is already linked to an osu! profile.", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            return
        # print("trying to find osu info")
        try:
            osu_user = await asyncio.wait_for(osu_api.user(user), timeout=10)
            # print("got osu info")
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Timeout", description="osu! API request timed out, please try again later.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        except Exception:
            embed = discord.Embed(title="Error", description="Something went wrong. Please ensure the username is correct.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        # print("trying to check if alr linked")
        if osu_user and await asyncio.to_thread(search_osu_user, osu_user.id):
            embed = discord.Embed(title="Already Linked", description="This osu! profile is already linked to a discord account.", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
            return

        await asyncio.to_thread(insert_user, interaction.user.id, osu_user.id, interaction.user.name, user)

        embed = discord.Embed(title="Successful Link", description=f"Successfully linked to {osu_user.username}!", color=discord.Color.green())
        embed.set_image(url=osu_user.avatar_url)
        await interaction.response.send_message(embed=embed)
           
    @app_commands.command(name="unlink", description="todo")
    async def unlink(self, interaction: discord.Interaction):
        # print("trying to execute")
        if await asyncio.to_thread(search_disc_user, interaction.user.id):
            await asyncio.to_thread(delete_user, interaction.user.id)
            embed = discord.Embed(title="Successful Unlink", description=f"Successfully unlinked your discord account.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed)         
            
        embed = discord.Embed(title="No Account to Unlink", description=f"This discord account is not linked to an osu! profile.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)                
    
async def setup(bot):
    await bot.add_cog(Link(bot))