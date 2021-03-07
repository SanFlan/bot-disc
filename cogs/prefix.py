import os.path
import json
from discord.ext import commands

default_prefix = 'pp!'
prefixes_file = 'prefixes.json'

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        org_id = 745289656215797840
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.permissions.administrator == True or role.id == org_id:
                return True
        return False

    @commands.Cog.listener()
    async def on_connect(self):
        if not os.path.exists(prefixes_file):
            with open(prefixes_file, 'w') as f:
                json.dump({}, f)
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open(prefixes_file, 'r+') as f:
            prefixes = json.load(f)
            if not str(guild.id) in prefixes:
                prefixes[str(guild.id)] = default_prefix
                f.seek(0)
                json.dump(prefixes, f, indent=4)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open(prefixes_file, 'r+') as f:
            prefixes = json.load(f)
            prefixes.pop(str(guild.id))
            f.seek(0)
            json.dump(prefixes, f, indent=4)
            f.truncate()

    @commands.command(pass_context=True)
    async def changeprefix(self, ctx, prefix):
        with open(prefixes_file, 'r+') as f:
            prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
            f.seek(0)
            json.dump(prefixes, f, indent=4)

        await ctx.send(f"Prefijo cambiado por: {prefix}")


def setup(bot):
    bot.add_cog(Prefix(bot))