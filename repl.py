from functools import partial
import aiohttp
from discord.ext import commands
import discord
import inspect
import re
import io
import contextlib
import traceback
import urllib.request
import urllib.parse
import math
import random
import textwrap
from contextlib import redirect_stdout
import datetime
import humanfriendly

import utils
from paginator import *
from simplepaginator import SimplePaginator
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageFont
from io import BytesIO

ownerid = 586426079078514700
allowed = [ownerid, 722673814659530784]  # test account


def isowner(ctx):
    return ctx.message.author.id in allowed


class Owner(commands.Cog):
    '''commands that only the bot owner can use'''

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        'Automatically removes code blocks from the code.'
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:(- 1)])
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    @commands.check(isowner)
    @commands.command(name='exec')
    async def _eval(self, ctx, *, body: str):
        '''for bot owner to execute statements'''
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'server': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }
        env.update(globals())
        body = self.cleanup_code(body)
        stdout = io.StringIO()
        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')
        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))
        func = env['func']
        try:
            with redirect_stdout(stdout):
                start = datetime.datetime.now()
                ret = await func()
        except Exception as e:
            end = datetime.datetime.now()
            time_diff = (end - start).microseconds / 1000
            await ctx.message.add_reaction('\u274C')
            value = stdout.getvalue()
            value = ('py\n{}{}\n'.format(value, traceback.format_exc()))
            sendlist = list(map(lambda x: "```" + x + "```", utils.partition(value, 1950)))
            embedlist = []
            for i in range(len(sendlist)):
                embedlist.append(
                    discord.Embed(title="Page {}/{} of error".format(i + 1, len(sendlist)), description=sendlist[i],
                                  colour=discord.Colour.red()).set_footer(text="Executed in {}ms".format(time_diff)))
            await SimplePaginator(extras=embedlist).paginate(ctx)
        else:
            end = datetime.datetime.now()
            time_diff = (end - start).microseconds / 1000
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass
            sendable = ""
            if ret is None:
                if value:
                    sendable = value
            else:
                self._last_result = ret
                sendable = str(value) + str(ret)
            sendlist = list(map(lambda x: "```" + x + "```", utils.partition(sendable, 1950)))
            see = ""
            embedlist = []
            for i in range(len(sendlist)):
                embedlist.append(
                    discord.Embed(title="Page {}/{} of output".format(i + 1, len(sendlist)), description=sendlist[i],
                                  colour=discord.Colour.blurple()).set_footer(
                        text="Executed in {} ms".format(time_diff)))
            await SimplePaginator(extras=embedlist).paginate(ctx)

    @commands.check(isowner)
    @commands.command()
    async def repl(self, ctx):
        '''for bot owner to run series of commands'''
        msg = ctx.message
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': msg,
            'server': msg.guild,
            'channel': msg.channel,
            'author': msg.author,
            '_': None,
        }
        if msg.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return
        self.sessions.add(msg.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')
        while True:
            response = await self.bot.wait_for('message', check=(
                lambda m: m.content.startswith('`') and m.author.id == ownerid and m.channel == ctx.channel))
            cleaned = self.cleanup_code(response.content)
            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(msg.channel.id)
                return
            executor = exec
            if cleaned.count('\n') == 0:
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval
            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue
            variables['message'] = response
            fmt = None
            stdout = io.StringIO()
            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = '```py\n{}{}\n```'.format(value, traceback.format_exc())
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = '```py\n{}{}\n```'.format(value, result)
                    variables['_'] = result
                elif value:
                    fmt = '```py\n{}\n```'.format(value)
            try:
                if fmt is not None:
                    pass
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await msg.channel.send('Unexpected error: `{}`'.format(e))

    @commands.check(isowner)
    @commands.command()
    async def getsource(self, ctx, command):
        '''getting the code for command'''
        a = inspect.getsource(self.bot.get_command(command).callback)
        m = len(a) // 1900
        embedlist = []
        for x in range(m):
            embedlist.append(discord.Embed(title="Page {}/{} of '{}' command".format(x + 1, m + 1, command),
                                           description="```py\n" + a[1900 * x:1900 * (x + 1)] + "```",
                                           colour=discord.Colour.dark_gold()))
        embedlist.append(discord.Embed(title="Page {}/{} of '{}' command".format(m + 1, m + 1, command),
                                       description="```py\n" + a[1900 * m:] + "```",
                                       colour=discord.Colour.dark_gold()))
        await SimplePaginator(extras=embedlist).paginate(ctx)


def setup(bot):
    bot.add_cog(Owner(bot))