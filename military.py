import asyncio
from utils import *
from discord.ext import commands
import discord
from dbwrapper import DB

class Military(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def battle(self, ctx, opponent:discord.Member):
        '''Engage in battle with qnother country'''
        mess = await ctx.send(f"{opponent.mention}, you've been challenged by {ctx.author.mention}. Do you accept their request?")
        await mess.add_reaction("\u2705")
        await mess.add_reaction("\u274c")
        try:
            def isopponent(reaction, user):
                return user.id == opponent.id and reaction.message.id == mess.id and reaction.emoji in ["\u2705","\u274c"]
            r,u=await self.bot.wait_for("reaction_add", check=isopponent, timeout=60)
            if r.emoji=="\u274c":
                raise asyncio.TimeoutError
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, I'm sorry but your opponent did not accept your battle request.", delete_after=6)
            await mess.delete()
            return
        await mess.edit(content=str(list(filter(lambda x:x.name=="sword",ctx.guild.emojis))[0])+" Loading")
        db = DB("users")
        db.set_collection("military")
        declarer = await db.find(length=1, userid=ctx.author.id)
        declared = await db.find(length=1, userid=opponent.id)
        if not declarer:
            await db.insert(userid=ctx.author.id, points=0)
            await mess.delete()
            await ctx.send(f"{ctx.author.mention} does not even have a military.", delete_after=5)
            return
        else:
            declarer = declarer[0]
        if not declared:
            await db.insert(userid=ctx.author.id, points=0)
            await mess.delete()
            await ctx.send(f"{opponent.mention} does not even have a military.", delete_after=5)
            return
        else:
            declared = declared[0]
        if declarer["points"]==0:
            await mess.delete()
            await ctx.send(f"{ctx.author.mention} does not even have a military.", delete_after=5)
            return
        if declared["points"]==0:
            await mess.delete()
            await ctx.send(f"{opponent.mention} does not even have a military.", delete_after=5)
            return
        circles= ["⚪","🔴","🔵"]
        await mess.clear_reactions()
        emb = discord.Embed(title="Board", description="\n".join([circles[0]*7]*6), colour=discord.Colour.lighter_grey())
        await mess.edit(embed=emb)
        reactions = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"]
        for i in reactions:
            await mess.add_reaction(i)
        await mess.edit(content="")
        #now for c4 logic
        board = [[0 for k in range(7)] for j in range(6)]
        def strboard(b):
            return "\n".join("".join(circles[i] for i in j) for j in b)
        def checkOWin(board, tile):
            boardHeight = len(board[0])
            boardWidth = len(board)
            # check horizontal spaces
            for y in range(boardHeight):
                for x in range(boardWidth - 3):
                    if board[x][y] == tile and board[x + 1][y] == tile and board[x + 2][y] == tile and board[x + 3][y] == tile:
                        return True

            # check vertical spaces
            for x in range(boardWidth):
                for y in range(boardHeight - 3):
                    if board[x][y] == tile and board[x][y + 1] == tile and board[x][y + 2] == tile and board[x][y + 3] == tile:
                        return True

            # check / diagonal spaces
            for x in range(boardWidth - 3):
                for y in range(3, boardHeight):
                    if board[x][y] == tile and board[x + 1][y - 1] == tile and board[x + 2][y - 2] == tile and board[x + 3][y - 3] == tile:
                        return True

            # check \ diagonal spaces
            for x in range(boardWidth - 3):
                for y in range(boardHeight - 3):
                    if board[x][y] == tile and board[x + 1][y + 1] == tile and board[x + 2][y + 2] == tile and board[x + 3][y + 3] == tile:
                        return True

            return False
        full = []
        for turn in range(42):
            now = [ctx.author, opponent][turn%2]
            emb.title=f"It's {str(now)}'s turn now!"
            emb.colour=[discord.Colour.red(), discord.Colour.blue()][turn%2]
            await mess.edit(embed=emb)
            try:
                def valid(reaction, user):
                    allowed = []
                    for i in reactions:
                        if i not in full:
                            allowed.append(i)
                    return reaction.emoji in allowed and reaction.message.id==mess.id and user.id==now.id
                r, u = await self.bot.wait_for("reaction_add", timeout=60, check=valid)
            except asyncio.TimeoutError:
                emb.colour=[discord.Colour.red(), discord.Colour.blue()][(turn+1)%2]
                now = [ctx.author, opponent][(turn+1)%2]
                emb.title = f"{str(now)} won!"
                await mess.edit(embed=emb)
                loser = turn % 2
                await mess.clear_reactions()
                break
            column = reactions.index(r.emoji)
            for checking in range(5,-1,-1):
                if board[checking][column]==0:
                    board[checking][column] = turn%2+1
                    if checking==0:
                        full.append(r.emoji)
                    break
            emb.description=strboard(board)
            if checkOWin(board, turn%2+1):
                emb.title = f"{str(now)} won!"
                await mess.edit(embed=emb)
                loser = 1-turn%2
                await mess.clear_reactions()
                break
            await mess.edit(embed=emb)
            await r.remove(u)
        else:
            emb.title="It's a draw!"
            emb.colour=discord.Colour.dark_grey()
            await mess.clear_reactions()
            return
        loserobj = [declarer, declared][loser]
        await db.update(objid=loserobj["_id"], points=loserobj["points"]-1)

    @commands.command()
    async def buypoints(self, ctx, number:int):
        """Lets you buy as many points as needed"""
        async with ctx.typing():
            number = abs(number)
            money = number*1000
            db = DB('users')
            db.set_collection('currency')
            author = await db.find(userid=ctx.author.id)
            if author == []:
                message = "⚠ | Your balance is 0<:Silver:733335375589933130>. You cannot deposit money."
                await db.insert(userid=ctx.author.id, money=0)
            elif author[0]['money'] < money:
                message = f"⚠ | You have insufficient funds! Your balance is {author[0]['money']}<:Silver:733335375589933130>."
            else:
                author[0]['money'] -= money
                await db.update(objid=author[0]["_id"], money=author[0]['money'])
                db.set_collection("military")
                mili = (await db.find(userid=ctx.author.id))
                if not mili:
                    await db.insert(userid=ctx.author.id, points=number)
                else:
                    await db.update(objid=mili[0]["_id"], points=mili[0]["points"]+number)
                message = "Success! " + str(
                    number) + " points has been added to your nation!"
                webhook = await get_webhook(self.bot, 733520821619916900, 733530983751483423)
                embed = discord.Embed(title="Military investment", colour=discord.Colour.dark_green())
                embed.description = f"""**Buyer:** {ctx.author.mention}
        **Points:** {number}
        [[Jump to purchase]]({ctx.message.jump_url})"""
                await webhook.send(embed=embed)
            await ctx.send(message)

    @commands.check(lambda ctx:724557530025689108 in list(map(lambda x:x.id, ctx.author.roles)))
    @commands.command()
    async def setpoints(self, ctx, number:int, user:discord.Member=None):
        """Lets Roleplay Masters set military points"""
        if user is None:
            user = ctx.author
        async with ctx.typing():
            number = abs(number)
            db = DB('users')
            db.set_collection('military')
            author = await db.find(userid=user.id)
            if author == []:
                await db.insert(userid=user.id, points=number)
            else:
                mili = (await db.find(userid=user.id))
                await db.update(objid=mili[0]["_id"], points=number)
            message = f"Success! {user} now has {number} points!"
            webhook = await get_webhook(self.bot, 733520821619916900, 733530983751483423)
            embed = discord.Embed(title="Military points set", colour=discord.Colour.dark_green())
            embed.description = f"""**Set for:** {user.mention}
        **Set by:** {ctx.author.mention}
        **Points:** {number}
        [[Jump to purchase]]({ctx.message.jump_url})"""
            await webhook.send(embed=embed)
        await ctx.send(message)

    @commands.command()
    async def getpoints(self, ctx, user:discord.Member=None):
        """Gets military points of a user"""
        if user is None:
            user = ctx.author
        async with ctx.typing():
            db = DB('users')
            db.set_collection('military')
            author = await db.find(userid=user.id)
            if author == []:
                await db.insert(userid=user.id, points=0)
                points = 0
            else:
                mili = (await db.find(userid=user.id))[0]
                points = mili["points"]
            embed = discord.Embed(title=f"{user}'s military points",description=f"{points} points", colour=discord.Colour.dark_green())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Military(bot))