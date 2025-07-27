def read_file(filename):
    with open(filename, "r") as file:
        return file.read()

OSU_API_KEY = read_file("osuApiKey.txt")
OSU_API_ID = int(read_file("osuApiId.txt"))
DISCORD_BOT_KEY = read_file("discordBotKey.txt")