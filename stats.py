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

    @commands.command(aliases=['transfer'])
    async def send(self,ctx,money:int=0,*,recipient:discord.Member):
        '''send money'''
        if recipient.id==ctx.author.id:
            await ctx.send(f"⚠ | {ctx.author.mention}, you may not send money to yourself!")
            return
        if recipient.bot or ctx.author.bot:
            await ctx.send(f"⚠ | {ctx.author.mention}, bots cannot engage in financial transactions.!")
            return
        async with ctx.typing():
            db = DB("users")
            db.set_collection('currency')
            author = await db.find(userid=ctx.author.id)
            receiver = await db.find(userid=recipient.id)
            if author == []:
                await db.insertnorepeat(userid=0,money=0)
                await ctx.send("You do not have any money. Try again!")
                return
            else:
                author = author[0]
                if receiver == []:
                    receivercurr = 0
                    await db.insertnorepeat(userid=recipient.id)
                    receiver = (await db.find(userid=recipient.id))[0]
                else:
                    receiver = receiver[0]
                    receivercurr = receiver['money']
                money = max(10,money)
                money = min(money,author['money'])
            mess = await ctx.send(f"{ctx.author.mention}, you are going to transfer {money} <:Silver:733335375589933130> to {recipient.mention}. Proceed?")
            await mess.add_reaction("❌")
            await mess.add_reaction("✅")
            try:
                def ch(reaction,user):
                    return user.id==ctx.author.id and reaction.message.id==mess.id
                status = await self.bot.wait_for("reaction_add",timeout=15,check=ch)
                if status[0].emoji=="❌":
                    raise asyncio.TimeoutError
                elif status[0].emoji=="✅":
                    receivercurr+=money
                    async with ctx.typing():
                        author['money']=author['money']-money
                        await db.update(author["_id"],money=author["money"])
                        await db.update(receiver["_id"],money=receivercurr)
                    await mess.delete()
                await ctx.send(f"Transfer succeeded! {money}<:Silver:733335375589933130> has been transferred to {recipient.mention}")
                webhook = await get_webhook(ctx, 733520821619916900, 733530983751483423)
                emb = discord.Embed(title="Financial transfer",colour=discord.Colour.lighter_grey())
                emb.description=f"**Sender:** {ctx.author.mention}\n**Receiver: ** {recipient.mention}\n**Amount:** {money}"
                await webhook.send(embed=emb)
            except asyncio.TimeoutError:
                await ctx.send("Transfer of money cancelled.")
                await mess.delete()

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
                await db.insertnorepeat(userid=user.id,money=0)
                text = (user.mention+" has a balance of 0<:Silver:733335375589933130>.")
            else:
                author = author[0]
                text = (user.mention+" has a balance of "+str(author['money'])+"<:Silver:733335375589933130>.")
        await ctx.send(text)

    @commands.command()
    async def deposit(self,ctx,money:int):
        '''Deposits money into the world bank'''
        async with ctx.typing():
            db = DB('users')
            db.set_collection('currency')
            author = await db.find(userid=ctx.author.id)
            money = abs(money)
            if author == []:
                message = "⚠ | Your balance is 0<:Silver:733335375589933130>. You cannot deposit money."
                await db.insert(userid=ctx.author.id,money=0)
            elif author[0]['money']<money:
                message = f"⚠ | You have insufficient funds! Your balance is {author[0]['money']}<:Silver:733335375589933130>."
            elif money<10:
                message = f"⚠ | You have to deposit at least 10<:Silver:733335375589933130>, {ctx.author.mention}!"
            else:
                author[0]['money'] -= money
                await db.update(objid=author[0]["_id"], money=author[0]['money'])
                message = "Success! "+str(money)+"<:Silver:733335375589933130> has been deposited into the world bank!"
                webhook = await get_webhook(ctx,733520821619916900,733530983751483423)
                embed = discord.Embed(title="Financial deposit",colour=discord.Colour.light_grey())
                embed.description=f"**Depositor:** {ctx.author.mention}\n**Amount:** {money}"
                await webhook.send(embed=embed)
            await ctx.send(message)

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
            guild_level = int((fishermen+farmers+miners)/3)
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
                await db.insertnorepeat(userid=ctx.author.id,money=0)
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
                        choice = random.randint(1,3)
                        if choice==0:
                            workstats['fish']+=1
                            message = ("You hired a fisherman! (+200<:Silver:733335375589933130>/day")
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
                await db.insertnorepeat(userid=ctx.author.id,money=0)
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
