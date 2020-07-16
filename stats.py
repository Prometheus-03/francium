import asyncio
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

    @commands.command(aliases=['transfer'])
    async def send(self,ctx,money:int=0,*,recipient:discord.Member):
        '''send money'''
        db = DB('users')
        async with ctx.typing():
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
                    await db.insertnorepeat(userid=receiver.id)
                    receiver = await db.find(userid=receiver.id)[0]
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
                text = ("Your balance is 0<:Silver:733335375589933130>.")
            else:
                author = author[0]
                text = ("Your balance is "+str(author['money'])+"<:Silver:733335375589933130>.")
        await ctx.send(text)

def setup(bot):
    bot.add_cog(Stats(bot))
