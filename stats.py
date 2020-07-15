import datetime

from discord.ext import commands
import discord
from dbwrapper import DB


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def daily(self, ctx):
        '''Get your daily rewards'''
        data = DB("users")
        newdaily = True
        data.set_collection("currency")
        async with ctx.typing():
            match = await data.find(userid=ctx.author.id)
            if match:
                user = match[0]
                if 'cooldown' not in user.keys():
                    user["money"] = 500
                    user['cooldown'] = int(datetime.datetime.now().timestamp())
                elif int(datetime.datetime.now().timestamp()) - user['cooldown'] >= 86400:
                    user["money"] += 500
                    user['cooldown'] = int(datetime.datetime.now().timestamp())
                else:
                    print(int(datetime.datetime.now().timestamp()),user['cooldown'])
                    conversion = datetime.timedelta(
                        seconds=(user['cooldown'] + 86400 - int(datetime.datetime.now().timestamp())))
                    converted_time = str(conversion)
                    await ctx.send(f"{ctx.author.mention}, you can collect your dailies in {converted_time}.")
                    newdaily = False
                await data.update(user["_id"], money=user['money'], cooldown=user['cooldown'])
            else:
                await data.insertnorepeat(userid=ctx.author.id, money=500,
                                          cooldown=int(datetime.datetime.now().timestamp()))
        if newdaily:
            await ctx.send(f"{ctx.author.mention}, you have collected your daily bonus of 500 silver!")


def setup(bot):
    bot.add_cog(Stats(bot))
