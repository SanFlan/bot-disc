import discord
import io
from discord.ext import commands
from discord.ext.commands.core import command
from tabulate import tabulate
import inspect
from db import *

class ListDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def table_of_entries(self, entries):
        table = []
        for entry in entries:
            if len(entry.entry_name) > 20 :
                table.append([
                    self.bot.get_user(entry.user_id).name,
                    entry.entry_name[0:25] + '...',
                    entry.tickets,
                    entry.view_date.strftime("%d %b %Y") if entry.view_date != None else ' '
                ]) 
            else:
                table.append([
                    self.bot.get_user(entry.user_id).name,
                    entry.entry_name,
                    entry.tickets,
                    entry.view_date.strftime("%d %b %Y") if entry.view_date != None else ' '
                ])
        return tabulate(table, headers=["Autor", "Serie", "Tickets", "Fecha visto"])

    async def table_of_entries_wo_date(self, entries):
        table = []
        total = sum_tickets(entries)
        for entry in entries:
            if len(entry.entry_name) > 20 :
                table.append([
                    self.bot.get_user(entry.user_id).name,
                    entry.entry_name[0:25] + '...',
                    entry.tickets,
                    entry.tickets/total
                ]) 
            else:
                table.append([
                    self.bot.get_user(entry.user_id).name,
                    entry.entry_name,
                    entry.tickets,
                    entry.tickets/total
                ])
        return tabulate(table, headers=["Autor", "Serie", "Tickets", "Probabilidad de salir"])

    async def send_text_as_attachment(self, ctx, text, filename):
        f = io.StringIO(text)
        await ctx.send(
                file=discord.File(f, filename)
            )
        f.close()
        return

    @commands.command(aliases=['ldb','listdatabase','database'])
    async def list_db(self, ctx):
        entries = get_all_entries()
        if len(entries) == 0:
            return await ctx.send("No hay series propuestas")
    
        table = await self.table_of_entries(entries)
        output = "**Lista completa de series**\n```{}```".format(table)
    
        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, filename="Lista de series.txt")
        else:
            await ctx.send(output)

    @commands.command(aliases=['lda','listadopt','adoptables'])
    async def list_adopt(self, ctx):
        entries = get_5_ticks()
        if len(entries) == 0:
            return await ctx.send("No hay series para adoptar")

        table = await self.table_of_entries(entries)
        output = "**Lista de series para adoptar**\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, 'lista_adoptables.txt')
        else:
            await ctx.send(output)

    @commands.command(aliases=['lwatched', 'lw', 'listwatched', 'watched'])
    async def list_watched(self, ctx):
        entries = get_viewed_entries()
        if len(entries) == 0:
            return await ctx.send("No hay series vistas")

        table = await self.table_of_entries(entries)
        output = "**Lista de series vistas**\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, "lista_de_series_vistas.txt")
        else:
            await ctx.send(output)

    @commands.command(aliases=['lnwatched', 'lnw', 'listnotwatched', 'notwatched'])
    async def list_not_watched(self, ctx):
        entries = get_not_viewed_entries()
        if len(entries) == 0:
            return await ctx.send("No hay series sin ver")

        table = await self.table_of_entries(entries)
        output = "**Lista de series sin ver**\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, "lista_de_series_no_vistas.txt")
        else:
            await ctx.send(output)

    @commands.command(aliases=['propuesta'])
    async def propuesta_de(self, ctx, user: discord.Member):
        for e in get_entries_from_user(user.id):
            if e.view_date == None:
                return await ctx.send("{} tiene para ver **{}**".format(
                    user.name,
                    e.entry_name
                ))

    @commands.command(aliases=['presentes'])
    async def list_present(self, ctx):
        entries = []
        try:
            vc = discord.utils.get(ctx.guild.voice_channels, id=ctx.author.voice.channel.id)
            vc_users = vc.members
            for u in vc_users:
                for entr in get_entries_from_user(u.id):
                    if entr.view_date == None:
                        entries.append(entr)
        except AttributeError:
            return await ctx.send("Debes ingresar a un canal de voz para poder ejecutar este comando")

        table = await self.table_of_entries_wo_date(entries)
        output = "**Lista de series**\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, "lista_de_series_de_presentes.txt")
        else:
            await ctx.send(output)

def setup(bot):
    bot.add_cog(ListDB(bot))