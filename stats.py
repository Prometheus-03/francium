import asyncio
import datetime
import random

from discord.ext import commands
import discord
from dbwrapper import DB
from utils import *


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(rate=1,per=7,type=commands.BucketType.user)
    @commands.command()
    async def bal(self,ctx,user:discord.Member=None):
        '''Lets you check your balance'''
        db = DB('users')
        db.set_collection('currency')
        if user is None:
            user = ctx.author
        async with ctx.typing():
            author = await db.find(userid=user.id)
            if author == []:
                await db.insertnorepeat(userid=user.id,money=0,bronze=0,cooldown=0)
                text = (user.mention+" has a balance of 0<:Silver:733335375589933130> 0<:Bronze:733334935091544156>.")
            else:
                author = author[0]
                text = (user.mention+" has a balance of "+str(author['money'])+"<:Silver:733335375589933130> "+str(author['bronze'])+"<:Bronze:733334935091544156>.")
        await ctx.send(text)

    @commands.cooldown(rate=1,per=7,type=commands.BucketType.channel)
    @commands.group()
    async def workers(self,ctx):
        '''Returns worker stats'''
        if ctx.invoked_subcommand is not None:
            return
        emb = discord.Embed(colour=discord.Colour.from_rgb(149, 252, 126))
        emb.set_author(name="Your workers",icon_url=str(ctx.author.avatar_url))
        emb.description = "You can buy more workers using `f!workers buy`"
        async with ctx.typing():
            db = DB("users")
            db.set_collection('workers')
            author = await db.find(userid=ctx.author.id)
            if author == []:
                fishermen = 0
                farmers = 0
                miners = 0
                guild_level = 0
                await db.insert(userid=ctx.author.id,fish=0,chop=0,mine=0,guild_level=0)
            else:
                author = author[0]
                fishermen = author['fish']
                farmers = author['chop']
                miners = author['mine']
                guild_level = author['guild_level']
            income = 500 + (fishermen+farmers+miners)*200
        emb.add_field(name="📈 Guild level",value=str(guild_level))
        emb.add_field(name="⚒ Workers count",value=str(fishermen+farmers+miners))
        emb.add_field(name="💰 Income",value=str(income)+"<:Silver:733335375589933130>")
        emb.add_field(name="🎣 Fishermen",value=str(fishermen))
        emb.add_field(name="👨🏽‍🌾 Farmers",value=str(farmers))
        emb.add_field(name="⛏ Miners",value=str(miners))
        await ctx.send(embed=emb)

    @workers.command()
    async def buy(self,ctx):
        message = ""
        async with ctx.typing():
            db = DB('users')
            db.set_collection('currency')
            user = await db.find(userid=ctx.author.id)
            if user==[]:
                await db.insertnorepeat(userid=ctx.author.id,money=0,bronze=0,cooldown=0)
                message = "You don't have enough silver! (0<:Silver:733335375589933130>)"
            else:
                user = user[0]
                db.set_collection('workers')
                workstats = await db.find(userid=ctx.author.id)
                if workstats == []:
                    await db.insertnorepeat(userid=ctx.author.id,fish=0,chop=0,mine=0,guild_level=0)
                    workstats = await db.find(userid=ctx.author.id)
                workstats = workstats[0]
                workers = (workstats['fish']+workstats['chop']+workstats['mine'])
                if workstats['guild_level']*3==workers:
                    message = ("You have reached the maximum number of workers for your guild level. Type `f!guild upgrade` to upgrade your guild.")
                else:
                    if user['money']<int(workers*4375/24):
                        message = (f"You do not have a sufficient balance ({int(workers*4375/24)}<:Silver:733335375589933130>)")
                    else:
                        user['money']-=int(workers*4375/24)
                        choice = random.randint(0,2)
                        if choice==0:
                            workstats['fish']+=1
                            message = ("You hired a fisherman! (+200<:Silver:733335375589933130>/day)")
                        elif choice==1:
                            workstats['chop']+=1
                            message = ("You hired a farmer (+200<:Silver:733335375589933130>/day)")
                        else:
                            workstats['mine']+=1
                            message = ("You hired a miner (+200<:Silver:733335375589933130>/day)")
                        await db.update(workstats["_id"],fish=workstats['fish'],chop=workstats['chop'],mine=workstats['mine'])
                        db.set_collection('currency')
                        await db.update(user["_id"],money=user['money'])
        await ctx.send(message)

    @commands.group()
    async def guild(self,ctx):
        '''Returns guild stats'''
        if ctx.invoked_subcommand is not None:
            return
        async with ctx.typing():
            db = DB('users')
            db.set_collection('workers')
            m = await db.find(userid=ctx.author.id)
            if m == []:
                await db.insertnorepeat(userid=ctx.author.id,guild_level=0,fish=0,chop=0,mine=0)
                level = 0
            else:
                m = m[0]
                level = m['guild_level']
        embed=discord.Embed(description=f"Level {level}",colour=discord.Colour.from_rgb(134, 255, 94))
        embed.set_author(name="Your guild level",icon_url=str(ctx.author.avatar_url))
        await ctx.send(embed=embed)

    @guild.command()
    async def upgrade(self,ctx):
        async with ctx.typing():
            db = DB('users')
            db.set_collection('workers')
            m = await db.find(userid=ctx.author.id)
            if m == []:
                await db.insertnorepeat(userid=ctx.author.id, guild_level=0, fish=0, chop=0, mine=0)
                level = 0
            else:
                m = m[0]
                level = m['guild_level']
            needed = (2*level+3)*700
            db.set_collection('currency')
            user = await db.find(userid=ctx.author.id)
            if user == []:
                await db.insertnorepeat(userid=ctx.author.id,money=0,bronze=0,cooldown=0)
                message = f"You need {needed}<:Silver:733335375589933130> to upgrade to the next level. Your current balance is 0<:Silver:733335375589933130>."
            else:
                user = user[0]
                if user['money']<needed:
                    message = f"You need {needed}<:Silver:733335375589933130> to upgrade to the next level. Your current balance is {user['money']}<:Silver:733335375589933130>."
                else:
                    m['guild_level']+=1
                    user['money']-=needed
                    message = f"Success! Your guild has been upgraded to **Level {m['guild_level']}**!"
                    await db.update(user["_id"],money=user['money'])
                    db.set_collection('workers')
                    await db.update(m["_id"],guild_level=m['guild_level'])
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Stats(bot))
