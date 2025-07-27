import discord
from discord.ext import commands
import asyncio
from ossapi import OssapiAsync
import sqlite3
import os

# dont be a dumb dumb and accidently leak your api keys by accidently commiting the files to the repo :)
with open("osuApiKey.txt", "r") as file:
    osuApiKey = file.read()
    file.close()
    
with open("osuApiId.txt", "r") as file:
    osuApiId = int(file.read())
    file.close()
    
osuApi = OssapiAsync(osuApiId, osuApiKey)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def searchDiscUser(discord_id):
    #print("disc search begin")
    conn = sqlite3.connect("osu_pass.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
    result = cursor.fetchone()
    conn.close()
    #print("disc search end")
    return result

def searchOsuUser(osu_user):
    #print("osu search begin")
    conn = sqlite3.connect("osu_pass.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE osu_id = ?", (osu_user.id,))
    result = cursor.fetchone()
    conn.close()
    #print("osu search end")
    return result

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# Test Command
@bot.command()
async def hello(ctx):
    try:
        user = await osuApi.user("cloudiees")
        await ctx.send(f"Hello! I'm a bot! And you are {user.id}")
        
    except Exception as e:
        await ctx.send("Oops! I couldn't fetch the user.")

# Link user
@bot.command()
async def link(ctx, user: str):
    #print("link begin")
    if await asyncio.to_thread(searchDiscUser, ctx.author.id):
        #print("found discord")
        await ctx.send("This discord account is already linked to an osu! account.")
        return
    
    try:
        #print("look up osu info")
        osu_user = await asyncio.wait_for(osuApi.user(user), timeout=10)
        
    except asyncio.TimeoutError:
        await ctx.send("osu! API request timed out, please try again later.")
        return
    
    except Exception as e:
        await ctx.send("Something went wrong. Please ensure the username you are entering is correct or try again later.")
        return
    
    print("done looking up info")
    if osu_user:
        #print("finding osu info in db")
        if await asyncio.to_thread(searchOsuUser,osu_user):
            #print("found osu info in db")
            await ctx.send("This osu! account is already linked to a discord account.")
            return
        
        def insert():
            #print("inserting in db")
            conn = sqlite3.connect("osu_pass.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (discord_id, osu_id) VALUES (?, ?)", (ctx.author.id, osu_user.id)
            )
            conn.commit()
            conn.close()
            #print("done inserting in db")
        
        await asyncio.to_thread(insert)
        await ctx.send(f"Successfully linked @{ctx.author.name} to {osu_user.username}!")
        
@link.error
async def link_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You need to provide an osu! username! Usage: '!link *username*'")

with open("discordBotKey.txt", "r") as file:
    discordBotKey = file.read()
    file.close()
bot.run(discordBotKey)
