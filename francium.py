import datetime
import random
import traceback
import discord
from discord.ext import commands
from utils import *
import tracemalloc

bot = commands.Bot(command_prefix = commands.when_mentioned_or("d!", "D!", "d>", "D>", "dun ", "Dun "))

@bot.event
async def on_message_edit(before, after):
    await bot.process_commands(after)


@bot.event
async def on_command_error(ctx, error):
    if type(error) == commands.errors.CommandOnCooldown:
        await ctx.send(
            embed=discord.Embed(title="Woah woah slow down!", description=error.args[0], colour=discord.Colour.red()))
    elif type(error) == commands.MissingPermissions:
        m = "\n".join(error.missing_perms)
        emb = discord.Embed(title="You do not have the needed permissions", description=m, colour=discord.Colour.red())
        await ctx.send(embed=emb)
    else:
        outputres = ""
        for i in (traceback.format_exception(None, error, error.__traceback__)):
            outputres += i
        embed = discord.Embed(title=str(type(error))[8:-2], description=str(error),
                              colour=discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255),
                                                             random.randint(0, 255)))
        await ctx.send("***Roses are red, violets are blue, there is an error when the command is used by you***",
                       embed=embed, delete_after=15)
        if len(outputres)>1900:
            outputres="..."+outputres[-1897:]
        embed.description = f"[[Jump!]]({ctx.message.jump_url})"+"\n"+"```"+outputres+"```"
        webhook = await get_webhook(ctx, 733520795766227026, 733538757289967646)
        await webhook.send(embed=embed)
        print(outputres)


@bot.event
async def on_ready():
    bot.remove_command("help")
    for i in ["info","general","income","stats","transactions","repl"]:
        bot.load_extension(i)
    await bot.get_channel(733520795766227026).send(embed=discord.Embed(title="Bot loaded",description="```"+datetime.datetime.now().strftime("%H:%M:%S, %d/%m/%Y")+"```"))
    print('Bot is ready')

bot.run('NzMyNzU5NjQ1MjMxMjUxNDY2.Xw5XGQ.SOlnyAGFvatJtHad06ag-HbTwvI')