import datetime
import random
import traceback
import discord
from discord.ext import commands
from utils import *
import tracemalloc

client = commands.Bot(command_prefix = commands.when_mentioned_or('f!', "F!", "f !", "F !"))

@client.event
async def on_command_error(ctx, error):
    if type(error) == commands.errors.CommandOnCooldown:
        await ctx.send(
            embed=discord.Embed(title="Woah woah slow down!", description=error.args[0], colour=discord.Colour.red()))
    elif type(error) == commands.MissingPermissions:
        m = "\n".join(error.missing_perms)
        emb = discord.Embed(title="You do not have the needed permissions", description=m, colour=discord.Colour.red())
        await ctx.send(embed=emb)
    else:
        embed = discord.Embed(title=str(type(error))[8:-2], description=str(error),
                              colour=discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255),
                                                             random.randint(0, 255)))
        await ctx.send("***Roses are red, violets are blue, there is an error when the command is used by you***",
                       embed=embed, delete_after=15)
        outputres = ""
        for i in (traceback.format_exception(None, error, error.__traceback__)):
            outputres += i
        webhook = await get_webhook(ctx,733520795766227026,733538757289967646)
        emb = discord.Embed(colour=discord.Colour.red(), description="```"+outputres+"```\n"+f"[Jump]({ctx.message.jump_url})")
        await webhook.send(embed=emb)
        print(outputres)


@client.event
async def on_ready():
    for i in ["general","income","stats","transactions","repl"]:
        client.load_extension(i)
    await client.get_channel(733520795766227026).send(embed=discord.Embed(title="Bot loaded",description="```"+datetime.datetime.now().strftime("%H:%M:%S, %d/%m/%Y")+"```"))
    print('Bot is ready')

client.run('NzMyNzU5NjQ1MjMxMjUxNDY2.Xw5XGQ.SOlnyAGFvatJtHad06ag-HbTwvI')