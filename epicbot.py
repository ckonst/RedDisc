import discord
from discord import Client
from discord.ext.commands import Bot
import praw
from dotenv import load_dotenv
import os

# comment out these two lines if you are not using spyder
# import nest_asyncio
# nest_asyncio.apply()

BOT_PREFIX = ('!')
client = Bot(command_prefix=BOT_PREFIX)
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET')
ID = os.getenv('CLIENT_ID')
topx = ['top{}'.format(i+1) for i in range(10)]
base_url = 'https://www.reddit.com'
reddit = praw.Reddit(client_id=ID,
                     client_secret=SECRET,
                     user_agent='EpicBot for Reddit')


@client.event
async def on_ready():
    """
    Print messages to indicate a successful login.

    Returns
    -------
    None.

    """
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command(name='top',
                brief='Post given number of posts from a subreddit.',
                aliases=topx)
async def top(ctx, *args):
    """
    Post the top x posts from a given subreddit to the channel.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context in which the command is being invoked under.
    *args : list
        The list of transformed arguments that were passed into the command.

    Returns
    -------
    None.

    """
    if not args:
        await ctx.channel.send('Please specify subreddit')
        return
    if ctx.invoked_with not in topx:
        await ctx.channel.send('Invalid command.\
                               Use !help for a list of valid commands.')
        return
    lim = ''.join(c for c in ctx.invoked_with if c.isdigit())
    if not lim:
        lim = 5
    lim = int(lim)

    for submission in reddit.subreddit(args[0]).hot(limit=lim):
        embed = discord.Embed(title=submission.title, color=0xff5700)
        embed.set_author(name='u/'+submission.author.name,
                         icon_url=submission.author.icon_img)
        if not submission.is_self:
            embed.set_image(url=submission.url)
        embed.add_field(name='URL:', value=base_url + submission.permalink)
        embed.add_field(name='Upvotes:', value=submission.score)
        embed.set_thumbnail(url='https://i.imgur.com/5uefD9U.png')
        await ctx.channel.send(embed=embed)

if __name__ == '__main__':
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        print('exiting\n')
        exit(0)
    except:
        pass
