import discord
from discord.ext import commands

client = commands.Bot(command_prefix = 'f!')

@client.event
async def on_ready():
    for i in ["general","stats"]:
        client.load_extension(i)
    print('Bot is ready')

client.run('NzMyNzU5NjQ1MjMxMjUxNDY2.Xw5XGQ.SOlnyAGFvatJtHad06ag-HbTwvI')
