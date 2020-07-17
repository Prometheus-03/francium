import discord
from discord.ext import commands
from discord import utils

async def get_webhook(ctx,channelid,webhookid):
    '''
    Allows you to get webhook
    :param ctx: Context object
    :param channelid: Id of the channel
    :param webhookid: Id of the webhook
    :return: The corresponding Webhook object, None if not found
    '''
    webhook = list(filter(lambda x: x.id == webhookid, (await ctx.guild.get_channel(channelid).webhooks())))
    if webhook == []:
        return None
    return webhook[0]