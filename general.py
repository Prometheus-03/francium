from discord.ext import commands
import discord

class General(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def ping(self,ctx):
        '''Says pong'''
        await ctx.send("Pong!")

def setup(bot):
    bot.add_cog(General(bot))