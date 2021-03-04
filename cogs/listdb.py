import discord
import io
from discord.ext import commands
from discord.ext.commands.core import command
from tabulate import tabulate
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

    async def send_text_as_attachment(ctx, text, filename="Output.txt"):
        f = io.StringIO(text)
        await ctx.send(
            "El mensaje supera los 2000 caracteres. Adjuntando como archivo de texto",
                file=discord.File(f, filename=filename)
            )
        f.close()

    @commands.command(aliases=['ldb'])
    async def list_db(self, ctx):
        entries = get_all_entries()
        if len(entries) == 0:
            return await ctx.send("No hay series propuestas")

        table = await self.table_of_entries(entries)
        output = "Lista completa de series\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, filename="Lista de series.txt")
        else:
            await ctx.send(output)

    @commands.command(aliases=['lda'])
    async def list_adopt(self, ctx):
        entries = get_5_ticks()
        if len(entries) == 0:
            return await ctx.send("No hay series para adoptar")

        table = await self.table_of_entries(entries)
        output = "Lista de series para adoptar\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, filename="Lista de series.txt")
        else:
            await ctx.send(output)

    @commands.command(aliases=['lwatched', 'lw'])
    async def list_watched(self, ctx):
        entries = get_viewed_entries()
        if len(entries) == 0:
            return await ctx.send("No hay series vistas")

        table = await self.table_of_entries(entries)
        output = "Lista de series vistas\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, filename="Lista de series.txt")
        else:
            await ctx.send(output)

    @commands.command(aliases=['lnwatched', 'lnw'])
    async def list_not_watched(self, ctx):
        entries = get_not_viewed_entries()
        if len(entries) == 0:
            return await ctx.send("No hay series sin ver")

        table = await self.table_of_entries(entries)
        output = "Lista de series sin ver\n```{}```".format(table)

        if len(output) >= 2000:
            await self.send_text_as_attachment(ctx, table, filename="Lista de series.txt")
        else:
            await ctx.send(output)

def setup(bot):
    bot.add_cog(ListDB(bot))