import datetime

from discord.ext import commands
import discord
from dbwrapper import DB

class Stats(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def daily(self,ctx):
        '''Get your daily rewards'''
        data = DB("users")
        data.set_collection("currency")
        match = await data.find(userid=ctx.author.id)
        if match:
            user = match[0]
            if 'cooldown' not in user.keys():
                user["money"] = 500
            elif int(datetime.datetime.now().timestamp()) - user['cooldown']>=86400:
                user["money"] += 500
            else:
                conversion = datetime.timedelta(seconds=user['cooldown'])
                converted_time = str(conversion)
                await ctx.send(f"{ctx.author.mention}, you can collect your dailies in {converted_time}.")
            user['cooldown'] = int(datetime.datetime.now().timestamp())
            await data.update(user["_id"],**user)
        else:
            await data.insertnorepeat(userid=ctx.author.id,money=500,cooldown=int(datetime.datetime.now().timestamp()))
        await ctx.send(f"{ctx.author.mention}, you have collected your dailies!")


def setup(bot):
    bot.add_cog(Stats(bot))