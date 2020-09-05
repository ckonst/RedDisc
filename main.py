import discord
from discord import Client
from discord.ext.commands import Bot
import praw

BOT_PREFIX = ('!')
client = Bot(command_prefix=BOT_PREFIX)
reddit = praw.Reddit(client_id="oBMX1JClXgCF0A",
                            client_secret="2V0JrFT97T1iOzMVrcjqNstg1LM",
                            user_agent="EpicBot for Reddit")

@client.command(name='hey',
                brief='The bot says hi',
                aliases = ['hi','greetings','hello'])
async def hey(ctx):
    # we do not want the bot to reply to itself
    if ctx.message.author.id == client.user.id:
        return
    await ctx.send('hey {0.author.mention}'.format(ctx.message))

@client.command(name='title',
                brief='posts the top 5 post titles in a given subreddit')
async def title(ctx, *args):
    if not args:
        await ctx.channel.send('Please specify subreddit')
    for submission in reddit.subreddit(args[0]).hot(limit=5):
        await ctx.channel.send(submission.title)

client.run("NzUxNjgyNzA0NjcxNjM3NTE0.X1MpEg.Wk1noo-DKjXcGLWyyxc4GEd0Gjs")