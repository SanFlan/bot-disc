import os.path
import json
from discord.ext import commands

org_id = [ 
    745289656215797840 
]

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_permissions(self, ctx):
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.permissions.administrator == True or role.id in org_id:
                return True
        return False


def setup(bot):
    bot.add_cog(Permissions(bot))