import os
import json
import discord
from os import path
from discord.ext import commands

# --- Bot Config ---
if path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
else:
    token = os.environ.get('DISCORD_TOKEN')

#load the json as prefixes
async def get_prefix(bot, message):
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        return prefixes[str(message.guild.id)]
    except:
        return 'pp!'

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=(get_prefix), description='Pen Pen', intents=intents)

# -- Main --
@bot.event
async def on_ready():
    print('Bot is online')

# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)