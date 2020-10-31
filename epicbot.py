import discord
from discord.ext.commands import Bot
import praw
from dotenv import load_dotenv
import os
from prawcore import NotFound

# comment out these two lines if you are not using spyder
import nest_asyncio
nest_asyncio.apply()

"""
TODO:
    use_snake_case_you_inbreds
"""
#TODO: make function to let users customize prefix
BOT_PREFIX = ('!')
client = Bot(command_prefix=BOT_PREFIX)
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET')
ID = os.getenv('CLIENT_ID')
sort = ['hot', 'top', 'new', 'rising', 'search']
aliases = [f'{s}{j}' for j in range(1, 11) for s in sort]
emojis = ['📄', '👤']
base_url = 'https://www.reddit.com'

def is_me(_id):
    return _id == client.user.id

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

@client.event
async def on_raw_reaction_add(payload):
    """

    Parameters
    ----------
    payload : discord.RawReactionActionEvent
        Represents the payload for a on_raw_reaction_add() or on_raw_reaction_remove() event.

    Returns
    -------
    None.

    """
    if not is_me(payload.user_id):
        m_id = payload.message_id
        message = await client.get_channel(payload.channel_id).fetch_message(m_id)
        embed = message.embeds[0]
        await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))
        if payload.emoji.name == '📄' and message.author.id == client.user.id:
            submission = reddit.submission(url=embed.description)
            new_embed = create_submission_embed(submission)
        elif payload.emoji.name == '👤' and message.author.id == client.user.id:
            new_embed = create_user_embed(reddit.redditor(embed.author.name[2:]), embed.description)
        await message.edit(embed=new_embed)

#TODO: seperate into functions for readability.
# if invoked with 'post' then search frontpage.
@client.command(name='post',
                brief='Posts given number of posts from a subreddit.',
                aliases = aliases)
async def post(ctx, *args):
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

    #check for invocation errors
    command = ctx.invoked_with

    #TODO: use a default subreddit instead of sending this message.
    if not args:
        await ctx.channel.send(f'Please specify subreddit! Correct usage is: !{command} [subreddit]')
        return
    sub = args[0]
    if not sub_exists(sub):
        await ctx.channel.send(f'Specified subreddit {sub} does not exist.')
        return

    #extract sort method and retrieval count from command
    sort_by, lim = extract_command_info(command)

    #TODO: fucking fix this
    if sort_by == 'search':
        results = reddit.subreddit("all").search(to_query_string(args), limit=lim)
    else:
        #get the number of stickied posts, so we can ignore them.
        num_stickied = len([s for s in getattr(reddit.subreddit(sub), sort_by)(limit=lim) if s.stickied])
        results = [s for s in getattr(reddit.subreddit(sub), sort_by)(limit=lim+num_stickied) if not s.stickied][:lim]

    #make requests for each submission and format them into discord embeds.
    for submission in results:
        embed = create_submission_embed(submission)
        message = await ctx.channel.send(embed=embed)
        for emoji in emojis:
            await message.add_reaction(emoji)

async def user(ctx, *args):
    result = reddit.redditor(args[0])
    embed = create_user_embed(result)
    await ctx.channel.send(embed=embed)

def create_user_embed(redditor, url=''):
    embed = discord.Embed(title=f'{redditor.name}\'s Profile', color=0xff5700, description=base_url+url)
    embed.set_author(name=f'u/{redditor.name}', icon_url=redditor.icon_img)
    embed.add_field(name='Karma: ', value=redditor.comment_karma + redditor.link_karma)
    return embed

def create_submission_embed(submission):
    """
    Return the embed object for a submission.

    Parameters
    ----------
    submission : praw.models.Submission
        A reddit submission.

    Returns
    -------
    embed : discord.embeds.Embed
        The embed object to return.

    """
    url = submission.permalink
    abridged_title = (submission.title[:250])
    if len(submission.title) > 250:
        abridged_title += '...'
    embed = discord.Embed(title=abridged_title, color=0xff5700, description=url)
    if user_exists(submission.author.name):
        embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
    else:
        embed.set_author(name='u/deleted', icon_url='https://i.imgur.com/ELSjbx7.png%27')
    new_url = url_morph(submission.url)
    if not submission.is_self and is_image(new_url):
        embed.set_image(url=new_url)
    embed.add_field(name='URL:', value=base_url+url)
    embed.add_field(name='Upvotes:', value=submission.score)
    embed.set_thumbnail(url='https://i.imgur.com/5uefD9U.png')
    return embed

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
    return True

def to_query_string(args):
    return ' '.join(args)

def is_image(url):
    extensions = ['gif', 'jpg', 'png']
    return any(e in url for e in extensions)

def url_morph(url):
    if 'gifv' in url:
        url = url[:-1]
    if 'imgur'in url and 'jpg' not in url:
        url += '.jpg'
    return url

def extract_command_info(command):
    """
    Return the invocation alias (sort_by) and limit given by the command.

    Parameters
    ----------
    command : string
        The invoked command.

    Returns
    -------
    sort_by : string
        The subreddit sorting method.
    lim : string
        How many submissions to post.

    """
    sort_by = ''.join([s for s in sort if s in command]).lower()
    lim = command.replace(sort_by, '')
    if not lim:
        lim = 5
    lim = int(lim)
    return (sort_by, lim)


if __name__ == '__main__':
	try:
		client.run(TOKEN)
	except KeyboardInterrupt:
		print('exiting\n')
		exit(0)
	except:
		pass
