import datetime
import random

from discord.ext import commands
import discord
from dbwrapper import DB

class Income(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.cooldown(rate=1,per=7,type=commands.BucketType.user)
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
                elif int(datetime.datetime.now().timestamp()) - user['cooldown'] >= 43200:
                    data.set_collection("workers")
                    m = await data.find(userid=ctx.author.id)
                    if not m:
                        workers = 0
                        await data.insertnorepeat(userid=ctx.author.id,fish=0,chop=0,mine=0,guild_level=0)
                    else:
                        workers = m[0]['fish']+m[0]['chop']+m[0]['mine']
                    user["money"] += 500+200*workers
                    user['cooldown'] = int(datetime.datetime.now().timestamp())
                else:
                    conversion = datetime.timedelta(
                        seconds=(user['cooldown'] + 43200 - int(datetime.datetime.now().timestamp())))
                    converted_time = str(conversion)
                    await ctx.send(f"{ctx.author.mention}, you can collect your dailies in {converted_time}.")
                    newdaily = False
                data.set_collection('currency')
                await data.update(user["_id"], money=user['money'], cooldown=user['cooldown'])
            else:
                await data.insertnorepeat(userid=ctx.author.id, money=500,bronze=0,
                                          cooldown=int(datetime.datetime.now().timestamp()))
        if newdaily:
            await ctx.send(f"{ctx.author.mention}, you have collected your daily bonus of {500+200*workers} <:Silver:733335375589933130>!")

    @commands.cooldown(rate=1,per=5,type=commands.BucketType.member)
    @commands.command()
    async def fish(self, ctx):
        '''Lets you do fishing'''
        async with ctx.typing():
            db = DB("users")
            db.set_collection('workers')
            user = await db.find(userid=ctx.author.id)
            if user == []:
                await db.insertnorepeat(userid=ctx.author.id,fish=0,chop=0,mine=0,guild_level=0)
                fishermen = 0
            else:
                user = user[0]
                fishermen = user["fish"]
            rewards={
                180:"boot",
                640:"salmon",
                1040:"trout",
                1480:"tuna",
                2560:"swordfish"
            }
            number = random.random()
            satisfy = sum([number >= 0.7, number >= 0.9, number >= 0.97, number >= 0.99])
            reward = list(rewards.keys())[satisfy]
            money = int(reward*(1+0.04*fishermen))
            db.set_collection('currency')
            profile = await db.find(userid=ctx.author.id)
            if profile == []:
                await db.insertnorepeat(userid=ctx.author.id,money=0,bronze=money,cooldown=0)
            else:
                profile = profile[0]
                profile["bronze"] += money
                profile["money"] += money//100
                await db.update(objid=profile["_id"],bronze=profile["bronze"],money=profile["money"])
        await ctx.send(f"🎣| You cast your fishing net and caught a **{rewards[reward]}**, earning **{money//100}<:Silver:733335375589933130>** and **{money}<:Bronze:733334935091544156>**!")

    @commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    @commands.command()
    async def chop(self, ctx):
        '''Lets you chop trees'''
        async with ctx.typing():
            db = DB("users")
            db.set_collection('workers')
            user = await db.find(userid=ctx.author.id)
            if user == []:
                await db.insertnorepeat(userid=ctx.author.id, fish=0, chop=0, mine=0, guild_level=0)
                farmers = 0
            else:
                user = user[0]
                farmers = user["chop"]
            rewards = {
                180: "normal tree",
                640: "oak tree",
                1040: "ash tree",
                1480: "hollow tree",
                2560: "redwood tree"
            }
            number = random.random()
            satisfy = sum([number >= 0.7, number >= 0.9, number >= 0.97, number >= 0.99])
            reward = list(rewards.keys())[satisfy]
            money = int(reward * (1 + 0.04 * farmers))
            db.set_collection('currency')
            profile = await db.find(userid=ctx.author.id)
            if profile == []:
                await db.insertnorepeat(userid=ctx.author.id, money=0, bronze=money, cooldown=0)
            else:
                profile = profile[0]
                profile["bronze"] += money
                profile["money"] += money // 100
                await db.update(objid=profile["_id"], bronze=profile["bronze"], money=profile["money"])
        await ctx.send(
            f"🪓| You swing your axe and chopped a **{rewards[reward]}**, earning **{money//100}<:Silver:733335375589933130>** and **{money}<:Bronze:733334935091544156>**!")

    @commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    @commands.command()
    async def mine(self, ctx):
        '''Lets you do mining'''
        async with ctx.typing():
            db = DB("users")
            db.set_collection('workers')
            user = await db.find(userid=ctx.author.id)
            if user == []:
                await db.insertnorepeat(userid=ctx.author.id, fish=0, chop=0, mine=0, guild_level=0)
                miners = 0
            else:
                user = user[0]
                miners = user["mine"]
            rewards = {
                180: "rock",
                640: "copper",
                1040: "iron",
                1480: "gold",
                2560: "diamond"
            }
            number = random.random()
            satisfy = sum([number >= 0.7, number >= 0.9, number >= 0.97, number >= 0.99])
            reward = list(rewards.keys())[satisfy]
            money = int(reward * (1 + 0.04 * miners))
            db.set_collection('currency')
            profile = await db.find(userid=ctx.author.id)
            if profile == []:
                await db.insertnorepeat(userid=ctx.author.id, money=0, bronze=money, cooldown=0)
            else:
                profile = profile[0]
                profile["bronze"] += money
                profile["money"] += money // 100
                await db.update(objid=profile["_id"], bronze=profile["bronze"], money=profile["money"])
        await ctx.send(
            f"⛏| You swing your pickaxe and hit **{rewards[reward]}**, earning **{money//100}<:Silver:733335375589933130>** and **{money}<:Bronze:733334935091544156>**!")

    @commands.cooldown(rate=1,per=10)
    @commands.command(aliases=["convert"])
    async def exchange(self,ctx):
        '''Exchanges your bronze for silver'''
        async with ctx.typing():
            db = DB("users")
            db.set_collection("currency")
            user = await db.find(userid=ctx.author.id)
            if user == []:
                await db.insertnorepeat(userid=ctx.author.id,money=0,bronze=0,cooldown=0)
                message = f"{ctx.author.mention}, you do not have any bronze to exchange!"
            else:
                user = user[0]
                if user["bronze"]<1000:
                    message = f"{ctx.author.mention}, you do not have enough bronze to exchange!"
                else:
                    silver = user["bronze"]//1000
                    bronze = user["bronze"] - 1000*silver
                    await db.update(objid=user["_id"],money=silver+user["money"],bronze=bronze)
                    message = f"{ctx.author.mention}, you have converted {1000*silver}<:Bronze:733334935091544156> into {silver}<:Silver:733335375589933130>!"
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Income(bot))