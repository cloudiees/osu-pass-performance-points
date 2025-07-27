import asyncio
from discord.ext import commands
from osu_api import osu_api
from db_commands import search_disc_user, search_osu_user, insert_user

def setup(bot):
    @bot.command()
    async def link(ctx, user: str):
        if await asyncio.to_thread(search_disc_user, ctx.author.id):
            await ctx.send("This Discord account is already linked to an osu! account.")
            return

        try:
            osu_user = await asyncio.wait_for(osu_api.user(user), timeout=10)
        except asyncio.TimeoutError:
            await ctx.send("osu! API request timed out, please try again later.")
            return
        except Exception:
            await ctx.send("Something went wrong. Please ensure the username is correct.")
            return

        if osu_user and await asyncio.to_thread(search_osu_user, osu_user.id):
            await ctx.send("This osu! account is already linked.")
            return

        await asyncio.to_thread(insert_user, ctx.author.id, osu_user.id)
        await ctx.send(f"Successfully linked {ctx.author.mention} to {osu_user.username}!")

    @link.error
    async def link_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `!link <osu_username>`")