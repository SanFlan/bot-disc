import os
import csv
import random
from dotenv import load_dotenv
#from datetime import datetime
import asyncio
import discord
#from discord import message
#from discord import client
from discord.ext import commands
#from discord.ext.commands.errors import CommandInvokeError

#from sqlalchemy.sql.elements import Null
#from sqlalchemy.sql.expression import false, true

from db import *


# --- Bot Config and Variables---
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='pp!', description='Pen Pen', intents=intents)

EMOJIS = {
    'eye': '\U0001F441',
    'dice': '\U0001F3B2',
    'speaker': '\U0001F50A'
}


#--- Authorization definition ---
def is_allowed():
    async def __check_role(ctx):
        org_id = 744370996148174890
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.permissions.administrator == True or role.id == org_id :
                return True
        return False

    return commands.check(__check_role)


# --- Commands ---
@bot.command(aliases=['info'])
async def list_commands(ctx):
    embed=discord.Embed(
        title="Lista de comandos",
        color=0x3385ff
        )
    dict_list = {
        'roll': """
            Rollea una serie entre los usuarios del Canal de Voz al que estas unido.Reaccionando con {} se lanza un nuevo roll, mientras que reaccionando \
            con {} marca la serie como vista (limite de 60 segundos para ambas aciones).
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
        """.format(EMOJIS["dice"], EMOJIS["eye"]),
        'rr': """
            Rollea una serie entre todas las disponibles. Reaccionando con {} se lanza un nuevo roll, mientras que reaccionando \
            con {} marca la serie como vista (limite de 60 segundos para ambas aciones).
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
        """.format(EMOJIS["dice"], EMOJIS["eye"]),
        'chd': """
            *(change view date)* Cambia la fecha de visto de una serie. El valor serie y fecha tienen que encontrarse \
            entre comillas dobles o simples, y la fecha en formato DD-MM-YYYY.
            *Ejemplo: chd "Nazo No Kanojo X" "23-01-2020"*
            """,
        'add, aefu': """
            *(add entry for user)* Agrega una serie a la lista.
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
            *Ejemplo: add @Tensz Baccano!*
            """,
        'ldb': "*(list database)* Muestra las series disponibles para ver, el usuario que propuso cada serie, sus tickets correspondientes y la fecha en que salió (o no).",
        'lw, lwatched': "*(list watched)* Muestra las series ya vistas",
        'lnw, lnwatched': "*(list not watched)* Muestra las series no vistas",
        'lda': "*(list adoptables)* Imprime la base de datos de las series adoptables, aka con 5 tickets.",
        'adopt': """
            'Adopta' una serie entre las disponibles en lda y mantiene sus tickets. Es necesario tener un rol con jerarquía correspondiente.",
            *Ejemplo: adopt @Bravelycold Ishuzoku Reviewers*
            """,
        'tick': """
            Suma un ticket a todas las series no vistas en la base de datos. Esta acción no se puede deshacer.
            Es necesario tener un rol con jerarquía correspondiente para utilizar este comando.
            """
    }
    for k, v in dict_list.items():
        embed.add_field(name=k, value=v, inline=False)
    await ctx.send(embed=embed)

# - Lists -
@bot.command(aliases=['ldb'])
async def list_db(ctx):
    entries = get_all_entries()
    if len(entries) == 0:
        return await ctx.send("No hay entradas")

    embed=discord.Embed(title="Lista de series vistas", color=0x85C1E9)
    formated_list = ""
    for entry in entries:
        member = ctx.guild.get_member(entry.user_id)
        formated_list += "**{}** - {} - {} ticket(s) - {}\n".format(
            member.display_name,
            entry.entry_name,
            entry.tickets, 
            entry.view_date.strftime("%d %b %Y") if entry.view_date != None else "No visto"
            )
    embed.add_field(name="\u200b", value=formated_list)
        
    await ctx.send(embed=embed) 

@bot.command(aliases=['lda'])
async def list_adopt(ctx):
    embed=discord.Embed(
        title="Lista de series adoptables",
        color=0xebae34
    )
    formated_list = ""
    entries = get_5_ticks()
    if len(entries) == 0:
        await ctx.send("No hay series adoptables")
        return
    for entry in entries:
        formated_list += "**{}** - {} - {} ticket(s)\n".format(
            bot.get_user(entry.user_id),
            entry.entry_name,
            entry.tickets
            )
    embed.add_field(name="\u200b", value=formated_list)
    await ctx.send(embed=embed)

@bot.command(aliases=['lwatched', 'lw'])
async def list_watched(ctx):
    embed=discord.Embed(
        title="Lista de series vistas",
        color=0x85C1E9
        )
    formated_list = ""
    entries = get_viewed_entries()
    if len(entries) == 0:
        await ctx.send("No hay entradas")
        return
    for entry in entries:
        member = ctx.guild.get_member(entry.user_id)
        formated_list += "**{}** - {} - {}\n".format(
            member.display_name,
            bot.get_user(entry.user_id),
            entry.view_date.strftime("%d %b %Y")
            )
    embed.add_field(name="\u200b", value=formated_list)
    await ctx.send(embed=embed)

@bot.command(aliases=['lnwatched', 'lnw'])
async def list_not_watched(ctx):
    embed=discord.Embed(
        title="Lista de series no vistas",
        color=0x85C1E9
        )
    formated_list = ""
    entries = get_not_viewed_entries()
    if len(entries) == 0:
        await ctx.send("No hay entradas")
        return
    for entry in entries:
        member = ctx.guild.get_member(entry.user_id)
        formated_list += "**{}** - {}\n".format(
            member.display_name,
            bot.get_user(entry.user_id)
            )
    embed.add_field(name="\u200b", value=formated_list)
    await ctx.send(embed=embed)


# - Rolls -
@bot.command(name='roll_reaction', aliases=['rr'])
@is_allowed()
async def roll_reaction(ctx, entries=Null):
    def check_emoji(reaction, user):
        return user == ctx.message.author and (
            str(reaction.emoji) == EMOJIS['eye'] or str(reaction.emoji) == EMOJIS['dice']
        )
    
    if entries == Null:
        entries = get_not_viewed_entries()

    end_loop = False
    while end_loop == False:
        try:
            roll = random.randint(0,len(entries)-1)
            entry = entries[roll]
        except:
            return await ctx.send("No hay series para ver!")

        member = ctx.guild.get_member(entry.user_id)

        m = await ctx.send("**{}** propuesta por **{}**. Prepará el pochoclo que salio tu serie!".format(
            entry.entry_name,
            member.display_name
        ))
        for e in ["eye", "dice"]:
            await m.add_reaction(EMOJIS[e])
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check_emoji)
            if m.id == reaction.message.id:
                if reaction.emoji == EMOJIS["dice"]:
                    continue
                elif reaction.emoji == EMOJIS["eye"]:
                    m = await change_view_date(ctx, entry.entry_name)
                    await m.add_reaction(EMOJIS["dice"])
                    try:
                        reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check_emoji)
                        if m.id == reaction.message.id and reaction.emoji == EMOJIS["dice"]:
                            continue
                    except asyncio.TimeoutError:
                        await m.clear_reactions()
        except asyncio.TimeoutError:
            await m.clear_reactions()

        end_loop = True

@bot.command(name='roll_vc_reaction', aliases=['roll'])
@is_allowed()
async def roll_vc_reaction(ctx):
    entries = []

    try:
        vc = discord.utils.get(ctx.guild.voice_channels, id=ctx.author.voice.channel.id)
        vc_users = vc.members
        for u in vc_users:
            entries.append(get_entry_from_user(u.id))
    except AttributeError:
        return await ctx.send("Debes ingresar a un canal de voz para poder ejecutar este comando")

    await roll_reaction(ctx, entries)


# - DB modifiers -
@bot.command(aliases=['aefu', 'add'])
@is_allowed()
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
    await ctx.send("Se agregó la serie :picardia:")

@bot.command(aliases=['chd'])
@is_allowed()
async def change_view_date(ctx, entry:str, new_date:str=Null):
    set_date_to_entry(entry, new_date)
    entry = get_entry_from_name(entry)
    return await ctx.send("Serie **{}** marcada como vista el {}".format(
        entry.entry_name,
        entry.view_date.strftime("%d-%m-%Y")
    ))

@bot.command(aliases=['tick'])
@is_allowed()
async def add_tickets(ctx):
    for role in ctx.author.roles:
        if str(role) == 'el mas pijudo':
            increment_tickets()
            await ctx.send("Sumando tickets... beep boop...")
            await list_db(ctx) 
            return
    await ctx.send("Privilegios insuficientes")

@bot.command(aliases=['adopt'])
@is_allowed()
async def act_adopt(ctx, user: discord.Member, *, entry:str):
    adoptable = get_5_ticks()
    nombres = []
    for serie in adoptable:
        nombres.append(serie.entry_name.lower())
    if get_entry_from_user(user.id) != None:
        await ctx.send("Usuario ya tiene una propuesta, primero borrarla e intentar de nuevo")
        return
    print(nombres)
    if not(entry.lower() in nombres):
        await ctx.send('Esta serie no es adoptable')
        return
    change_user_id_to_entry(entry, user.id)
    await ctx.send("Se agregó la serie :picardia:")

@bot.command(aliases=['icsv'])
@is_allowed()
async def import_csv(ctx, filename='import.csv', delimiter=';'):
    try:
        csv_file = open(filename)
        csv_records = csv.reader(csv_file, delimiter=delimiter)
    except FileNotFoundError:
        return await ctx.send("El archivo {} no existe".format(filename))
 
    for row in csv_records:
        # Remove @ from username (if any) and get member info
        user_name = row[0].lstrip('@')
        member = ctx.guild.get_member_named(user_name)

        try:
            add_entry(
                member.id,
                row[1],
                row[2]
            )
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'id'":
                m = 'No se pudo agregar la entrada ya que el usuario "{}" no existe.'.format(user_name)
                await ctx.send(m)
                continue
            else:
                return await ctx.send("Error desconocido. Mensaje: {}".format(e))

        await ctx.send("Agregada entrada **{}** de **{}**".format(
            row[1],
            member.display_name
        ))
        
    await ctx.send("**Importación finalizada!**")

# - Error handling -
@roll_reaction.error
@roll_vc_reaction.error
@act_adopt.error
async def permission_error(ctx, error):
    if error.__class__== commands.errors.CheckFailure:
        await ctx.send("No tenes permisos para ejecutar este comando")
    print(error.__class__ , error)

@add_entry_for_user.error
async def add_entry_for_user_error(ctx, error):
    if error.__class__ == commands.MissingRequiredArgument:
        await ctx.send("Faltan argumentos chinchu '{}'".format(error.param))
        return
    if error.__class__ == commands.BadArgument:
        await ctx.send("Pifiaste en algun argumento... {}".format(str(error)))
        return
    if error.__class__ == commands.MemberNotFound:
        await ctx.send("No encontre al user".format(str(error)))
        return
    print(error.__class__ ,error)


bot.run(token)
