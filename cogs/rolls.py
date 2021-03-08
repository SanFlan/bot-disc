import discord
import random
import asyncio
from discord.ext import commands
from db import *

EMOJIS = {
    'eye': '\U0001F441',
    'dice': '\U0001F3B2',
}

class Rolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        perm = self.bot.get_cog('Permissions')
        return await perm.check_permissions(ctx)

    async def cog_command_error(self, ctx, error):
        # Prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return
        
        if isinstance(error, commands.CheckFailure):
            return await ctx.send('No tenes permisos suficientes para ejecutar este comando')
        
        if isinstance(error, commands.CommandInvokeError):
            if 'ValueError: empty range for randrange()' in str(error):
                return await ctx.send('No hay series para ver!')
        
        await ctx.send('Error desconocido - Mensaje de error: **{}**'.format(error))

    @commands.command(name='roll_reaction', aliases=['rall'])
    async def roll_reaction(self, ctx, entries=None):
        def check_emoji(reaction, user):
            return user == ctx.message.author and (
                str(reaction.emoji) == EMOJIS['eye'] or str(reaction.emoji) == EMOJIS['dice']
            )

        if entries == None:
            entries = get_not_viewed_entries()

        end_loop = False
        while end_loop == False:
            roll = random.randint(0,len(entries)-1)
            entry = entries[roll]

            member = ctx.guild.get_member(entry.user_id)

            m = await ctx.send("**{}** propuesta por **{}**. Prepará el pochoclo que salio tu serie!".format(
                entry.entry_name,
                member.display_name
            ))
            for e in ["eye", "dice"]:
                await m.add_reaction(EMOJIS[e])
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=120, check=check_emoji)
                if m.id == reaction.message.id:
                    if reaction.emoji == EMOJIS["dice"]:
                        continue
                    elif reaction.emoji == EMOJIS["eye"]:
                        m = await self.change_view_date(ctx, entry.entry_name)
                        #await m.add_reaction(EMOJIS["dice"])
                        #reaction, user = await self.wait_for("reaction_add", timeout=60, check=check_emoji)
                        #if m.id == reaction.message.id and reaction.emoji == EMOJIS["dice"]:
                        #    continue
            except asyncio.TimeoutError:
                await m.clear_reactions()

            end_loop = True

    @commands.command(name='roll_vc_reaction', aliases=['roll'])
    async def roll_vc_reaction(self, ctx):
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

        await self.roll_reaction(ctx, entries)


def setup(bot):
    bot.add_cog(Rolls(bot))