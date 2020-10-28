import datetime

from discord.ext import commands
import discord

class General(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def ping(self,ctx):
        '''Says pong'''
        await ctx.send("Pong!")

    @commands.command()
    async def time(self,ctx):
        '''Gets the current time'''
        timenow = datetime.datetime.utcnow()
        hrs = timenow.hour+1
        if hrs%10 in [1,2,3] and hrs//10!=1:
            hrs = str(hrs)+[0,"st","nd","rd"][hrs%10]
        else:
            hrs = str(hrs)+"th"
        day = ["Mense Quattuor","Mense Quinque","Sex Mensis","Ultima Mensis","Mensis Unius","Duabus Mensis","Tria Mensis"][timenow.weekday()]
        ttof = datetime.datetime.fromtimestamp(1604016000)
        diff = timenow-ttof
        week = diff.days//7
        asorbs= "AS"
        if week < 0:
            week = abs(week)
            asorbs = "BS"
        emb = discord.Embed(title="Time now",colour=discord.Colour.dark_gold())
        emb.add_field(name="Real life", value=datetime.datetime.strftime(timenow, "%d %B %Y, %H:%M:%S UTC"))
        emb.add_field(name="Roleplay", value=f"{hrs} {day}, {week} {asorbs}")
        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(General(bot))