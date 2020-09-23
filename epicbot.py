import discord
from discord import Client
from discord.ext.commands import Bot
import praw
from dotenv import load_dotenv
import os
from prawcore import NotFound

# comment out these two lines if you are not using spyder
#import nest_asyncio
#nest_asyncio.apply()

BOT_PREFIX = ('!')
client = Bot(command_prefix=BOT_PREFIX)
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET')
ID = os.getenv('CLIENT_ID')
sort = ['hot', 'top', 'new', 'rising', 'search']
aliases = [f'{s}{j}' for j in range(1, 11) for s in sort] + sort
base_url = 'https://www.reddit.com'


reddit = praw.Reddit(client_id=ID,
                            client_secret=SECRET,
                            user_agent="EpicBot for Reddit")
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

@client.command(name='hot',
                brief='Posts given number of posts from a subreddit.',
                aliases = aliases)
async def hot(ctx, *args):
    """
       Returns a given number of posts, up to 10, sorted by the alias that this was invoked with.
       Parameters
       ----------
       ctx : discord.ext.commands.Context
           The context in which this command was called.
       *args : list
           The arguments that the user passed through.
           If the user does not specify a subreddit, or the given subreddit does not exist, send an error message.
       Returns
       -------
       None.
       """
    command = ctx.invoked_with
    if not args:
        if 'search' in command:
            await ctx.channel.send(f'Please specify what to search for!  Correct usage is: !{command} [search terms]')
        else:
            await ctx.channel.send(f'Please specify subreddit! Correct usage is: !{command} [subreddit]')
        return
    sub = args[0]
    if not sub_exists(sub):
        await ctx.channel.send(f'Specified subreddit {sub} does not exist.')
        return

    # extract sort method and retrieval count from command
    sort_by = ''.join([s for s in sort if s in command]).lower()
    lim = command.replace(sort_by, '')
    if not lim:
        lim = 5
    lim = int(lim)
    results = getattr(reddit.subreddit(sub), sort_by)(limit=lim)


    for submission in results:
        abridged_title = (submission.title[:250])
        if len(submission.title) > 250:
            abridged_title += '...'
        embed = discord.Embed(title = abridged_title, color = 0xff5700)
        if user_exists(submission.author.name):
            embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
        else:
            embed.set_author(name="u/deleted", icon_url = 'https://i.imgur.com/ELSjbx7.png')

        new_url = url_morph(submission.url)
        if not submission.is_self and parse_url(new_url):
            embed.set_image(url= new_url)
        print(submission.url)
        embed.add_field(name="URL:", value=base_url + submission.permalink)
        embed.add_field(name="Upvotes:", value=submission.score)
        embed.set_thumbnail(url='https://i.imgur.com/5uefD9U.png')
        await ctx.channel.send(embed=embed)




def sub_exists(subreddit):
    """
    Return whether a given subreddit exists.
    Parameters
    ----------
    subreddit : praw.models.Subreddit
        The subreddit object to check.
    Returns
    -------
    exists : boolean
        whether or not the subreddit exists.
    """
    exists = True
    try:
        reddit.subreddits.search_by_name(subreddit, exact=True)
    except NotFound:
        exists = False
    return exists

def user_exists(user):
    try:
        if getattr(reddit.redditor(user), 'is_suspended', False):
            return False
    except NotFound:
        return False

    else:
        return True


# account exists

def args_add(args):
    new_args = ' '.join(args)
    return new_args

def parse_url(url):
    extensions = ['gif', 'jpg', 'png']
    chars = set(extensions)
    if any((i in url) for i in extensions):
        return True
    else:
        return False

def url_morph(url):
    if 'gifv' in url:
        url = url[:-1:]
    if ' imgur'in url and 'jpg' not in url:
        url += '.jpg'
    return url



#await ctx.channel.send(submission.title)
#await ctx.channel.send("COMMENT:" + submission.comments[1].body)
#await ctx.channel.send("UPVOTES: {}".format(submission.score))





if __name__ == '__main__':
	try:
		client.run(TOKEN)
	except KeyboardInterrupt:
		print('exiting\n')
		exit(0)
	except:
		pass