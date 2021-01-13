import discord
from discord.ext import commands
import random

from db import add_entry, get_all_entries, increment_tickets, remove_entry, get_entry_from_name, get_entry_from_user

import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!!', description='entrys', intents=intents)


def is_admin():
    async def check_role(ctx):
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.permissions.administrator == True:
                return True
        return False
    return commands.check(check_role)


@bot.command(name='roll')
async def roll(ctx):
    entries = len(get_all_entries())
    if entries == 0:
        await ctx.send("No hay entradas")
        return
    roll = random.randint(0,entries-1)
    entry = get_all_entries()[roll]
    await ctx.send("{} propuesta por <@{}>".format(entry.entry_name, entry.user_id))
    member = ctx.guild.get_member(entry.user_id)
    if member.voice != None:
        await ctx.send(
                 "Parece que <@{}> está conectade a {}, así que prepará el pochoclo que salio tu serie".format(
                    entry.user_id, member.voice.channel
                    ))
        remove_entry(entry)
        return
    await ctx.send("Parece que <@{}> no esta en vc...".format(
        entry.user_id
        ))


@bot.command()
async def add(ctx, entry: str):
    if get_entry_from_user(ctx.message.author.id) != None:
        await ctx.send("eh loco vos ya propusiste")
        return
    if get_entry_from_name(entry.lower()) != None:
            await ctx.send("esa serie esta repetida")
            return
    add_entry(ctx.author.id, entry)
    await ctx.send("Se agregó la serie :picardia:")


@bot.command(aliases=['aefu'])
async def add_entry_for_user(ctx, user: discord.Member, *, entry:str):
    if get_entry_from_user(user.id) != None:
        await ctx.send("Usuario ya tiene una propuesta")
        return
    exs_entry = get_entry_from_name(entry.lower())
    if exs_entry != None:
        await ctx.send(
            "Esa serie esta repetida, fue propuesta por @{}".format(
                bot.get_user(exs_entry.user_id)
                ))
        return
    add_entry(user.id, entry)
    await ctx.send("Se agregó la serie :picardia:!")


@add_entry_for_user.error
async def add_entry_for_user_error(ctx, error):
    if error.__class__ == commands.errors.MissingRequiredArgument:
        await ctx.send("Faltan argumentos chinchu '{}'".format(error.param))
        return
    if error.__class__ == commands.errors.BadArgument:
        await ctx.send("Pifiaste en algun argumento... {}".format(str(error)))
        return
    if error.__class__ == commands.errors.MemberNotFound:
        await ctx.send("No encontre al user".format(error))
        return
    print(error.__class__ ,error)


@bot.command(aliases=['ldb'])
@is_admin()
async def list_db(ctx):
    embed=discord.Embed(
        title="Lista de series propuestas y sus autores",
        color=0xFF5733
        )
    entries = get_all_entries()
    formated_list = ""
    if len(entries) == 0:
        await ctx.send("No hay entradas")
        return
    for entry in entries:
        formated_list += "**{}** - {} - {} ticket(s)\n".format(bot.get_user(entry.user_id), entry.entry_name, entry.tickets)
    embed.add_field(name="\u200b", value=formated_list)
    await ctx.send(embed=embed)


@list_db.error
async def list_db_error(ctx, error):
    if error.__class__== commands.errors.CheckFailure:
        await ctx.send("No tenes permisos, que hacias queriendo toquetear?")
    print(error.__class__ , error)


@bot.command(aliases=['vchk'])
async def is_in_voice(ctx, user: discord.User):
    print(ctx.guild.get_member(user.id))
    member = ctx.guild.get_member(user.id)
    if member.voice != None:
        await ctx.send("El usuario mencionado esta en el canal {}!".format(member.voice.channel))
        return
    await ctx.send("El usuario mencionado no esta en voice :(")
    return


@bot.command(aliases=['tick'])
#@commands.has_role('el mas pijudo')
#asi funciona bien, queria ver como hacer para que mandara un mensaje de error pero no lo descubri
async def tickets(ctx):
    for role in ctx.author.roles:
        if str(role) == 'el mas pijudo':
            increment_tickets()
            await ctx.send("Sumando tickets... beep boop...")
            return
    await ctx.send("Privilegios insuficientes")


bot.run(token)
