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
            await interaction.response.send_message("This Discord account is already linked to an osu! account.")
            return
        # print("trying to find osu info")
        try:
            osu_user = await asyncio.wait_for(osu_api.user(user), timeout=10)
            # print("got osu info")
        except asyncio.TimeoutError:
            await interaction.response.send_message("osu! API request timed out, please try again later.")
            return
        except Exception:
            await interaction.response.send_message("Something went wrong. Please ensure the username is correct.")
            return
        # print("trying to check if alr linked")
        if osu_user and await asyncio.to_thread(search_osu_user, osu_user.id):
            await interaction.response.send_message("This osu! account is already linked.")
            return

        await asyncio.to_thread(insert_user, interaction.user.id, osu_user.id, interaction.user.name, user)
        # TODO: Add scores and o!ppp to newly linked profile
        await interaction.response.send_message(f"Successfully linked {interaction.user.mention} to {osu_user.username}!")
           
    @app_commands.command(name="unlink", description="todo")
    async def unlink(self, interaction: discord.Interaction):
        # print("trying to execute")
        if await asyncio.to_thread(search_disc_user, interaction.user.id):
            await asyncio.to_thread(delete_user, interaction.user.id)
            await interaction.response.send_message("Successfully unlinked account!")             
        await interaction.response.send_message("Your account is currently unlinked.")
    
async def setup(bot):
    await bot.add_cog(Link(bot))