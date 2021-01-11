import discord
from discord.ext import commands
import random

import os
from dotenv import load_dotenv

class Serie:
    def __init__(self, user, serie, ticket):
        self.user = user
        self.serie = serie
        self.ticket = 0

    def __str__(self):
        return 'userid: {} serie: {} tickets: {}'.format(self.user,self.serie,self.ticket)

db = []

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?!', description='series', intents=intents)

@bot.command(name='roll')
async def roll(ctx):
    entries = len(db)
    if entries == 0:
        await ctx.send("No hay series")
        return
    roll = random.randint(0,entries-1)
    serie = db[roll]
    await ctx.send("Salio la serie {} propuesta por <@{}>".format(serie.serie, serie.user))
    db.remove(serie)

@bot.command()
async def add(ctx, serie: str):
    tmp = Serie(ctx.author.id, serie, 0)
    db.append(tmp)
    await ctx.send("Se Agrego La Serie!")

@bot.command(aliases=['ldb'])
async def listdb(ctx):
    for serie in db:
        print(serie)
        print("propuesta por {}".format(bot.get_user(serie.user)))
    await ctx.send("Mira los logs")


bot.run(token)
