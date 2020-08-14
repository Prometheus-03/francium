import asyncio
from discord.ext import commands
import discord
from dbwrapper import DB
import datetime
from utils import get_webhook


class Transactions(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.cooldown(rate=1,per=7)
    @commands.command(aliases=['transfer'])
    async def send(self, ctx, money: int = 0, *, recipient: discord.Member):
        '''send money'''
        if recipient.id == ctx.author.id:
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
                await db.insertnorepeat(userid=0, money=0)
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
                money = max(10, money)
                money = min(money, author['money'])
            mess = await ctx.send(
                f"{ctx.author.mention}, you are going to transfer {money} <:Silver:733335375589933130> to {recipient.mention}. Proceed?")
            await mess.add_reaction("❌")
            await mess.add_reaction("✅")
            try:
                def ch(reaction, user):
                    return user.id == ctx.author.id and reaction.message.id == mess.id

                status = await self.bot.wait_for("reaction_add", timeout=15, check=ch)
                if status[0].emoji == "❌":
                    raise asyncio.TimeoutError
                elif status[0].emoji == "✅":
                    receivercurr += money
                    async with ctx.typing():
                        author['money'] = author['money'] - money
                        await db.update(author["_id"], money=author["money"])
                        await db.update(receiver["_id"], money=receivercurr)
                    await mess.delete()
                await ctx.send(
                    f"Transfer succeeded! {money}<:Silver:733335375589933130> has been transferred to {recipient.mention}")
                webhook = await get_webhook(ctx, 733520821619916900, 733530983751483423)
                emb = discord.Embed(title="Financial transfer", colour=discord.Colour.lighter_grey())
                emb.description = f"""**Sender:** {ctx.author.mention}
        **Receiver: ** {recipient.mention}
        **Amount:** {money}
        [[Jump to transaction]]({ctx.message.jump_url})"""
                await webhook.send(embed=emb)
            except asyncio.TimeoutError:
                await ctx.send("Transfer of money cancelled.")
                await mess.delete()

    @commands.cooldown(rate=1,per=7,type=commands.BucketType.member)
    @commands.command()
    async def deposit(self, ctx, money: int):
        '''Deposits money into the world bank'''
        async with ctx.typing():
            db = DB('users')
            db.set_collection('currency')
            author = await db.find(userid=ctx.author.id)
            money = abs(money)
            if author == []:
                message = "⚠ | Your balance is 0<:Silver:733335375589933130>. You cannot deposit money."
                await db.insert(userid=ctx.author.id, money=0)
            elif author[0]['money'] < money:
                message = f"⚠ | You have insufficient funds! Your balance is {author[0]['money']}<:Silver:733335375589933130>."
            elif money < 10:
                message = f"⚠ | You have to deposit at least 10<:Silver:733335375589933130>, {ctx.author.mention}!"
            else:
                author[0]['money'] -= money
                await db.update(objid=author[0]["_id"], money=author[0]['money'])
                message = "Success! " + str(
                    money) + "<:Silver:733335375589933130> has been deposited into the world bank!"
                webhook = await get_webhook(ctx, 733520821619916900, 733530983751483423)
                embed = discord.Embed(title="Financial deposit", colour=discord.Colour.light_grey())
                embed.description = f"""**Depositor:** {ctx.author.mention}
        **Amount:** {money}
        [[Jump to transaction]]({ctx.message.jump_url})"""
                await webhook.send(embed=embed)
            await ctx.send(message)

def setup(bot):
    bot.add_cog(Transactions(bot))