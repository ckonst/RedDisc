import discord
from discord.ext import tasks, commands
import praw
from dotenv import load_dotenv
import os
from prawcore import NotFound
import asyncio
import json

# comment out these two lines if you are not using spyder
#import nest_asyncio
#nest_asyncio.apply()

#%% STARTUP

with open(prefix_file := 'prefixes.json') as f:
    guild_prefixes = json.load(f)
default_prefix = '!'

async def get_prefix(bot, msg):
    """Return this guild's prefix."""
    guild = msg.guild
    if guild:
        id = str(guild.id)
        if id not in guild_prefixes:
            guild_prefixes[id] = default_prefix
            with open(prefix_file, 'w+') as f:
                json.dump(guild_prefixes, f)
        return commands.when_mentioned_or(guild_prefixes[id])(bot, msg)
    else:
        return commands.when_mentioned_or(default_prefix)(bot, msg)

client = commands.Bot(command_prefix=get_prefix)
load_dotenv()
client.remove_command('help')

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET')
ID = os.getenv('CLIENT_ID')
sort = ['hot', 'top', 'new', 'rising', 'search']
aliases = [f'{s}{j}' for j in range(1, 11) for s in sort]
emojis = ['📃','📄', '👤', '💬' ]
search_sorts = ['relevance', 'top', 'new', 'comments']
filters = ['all', 'hour', 'day', 'week', 'month', 'year']
extensions = ['gif', 'jpg', 'png']
base_url = 'https://www.reddit.com'
title_lim = 250
body_lim = 1020
comment_lim = 100
autofeed = None

def is_me(_id):
    """Return whether the given id is the bot's id."""
    return _id == client.user.id

reddit = praw.Reddit(client_id=ID,
                            client_secret=SECRET,
                            user_agent="EpicBot for Reddit")

#%% EVENTS

@client.event
async def on_ready():
    """Print messages to indicate a successful login."""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_raw_reaction_add(payload):
    """
    Event handler for reactions.
    We check reactions in the emojis list to decide what to set the embed to.
    Then edit the embed in the original message which received a reaction.
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

        if payload.emoji.name == '📃' and message.author.id == client.user.id:
            # short submission embed.
            submission = reddit.submission(url=embed.description)
            new_embed = create_submission_embed(submission)
        elif payload.emoji.name == '👤' and message.author.id == client.user.id:
            # profile of original poster.
            if user_exists(reddit.redditor(embed.author.name[2:])):
                new_embed = create_user_embed(reddit.redditor(embed.author.name[2:]), embed.description)
            else:
                new_embed = create_empty_user_embed(reddit.redditor(embed.author.name[2:]), embed.description)
        elif payload.emoji.name == '📄' and message.author.id == client.user.id:
            # extended submission embed.
            submission = reddit.submission(url=embed.description)
            new_embed = create_body_embed(submission)
        elif payload.emoji.name == '💬' and message.author.id == client.user.id:
            # comments on this post.
            submission = reddit.submission(url=embed.description)
            new_embed = create_comment_embed(submission)

        await message.edit(embed=new_embed)

#%% COMMANDS

@client.command()
@commands.guild_only()
async def prefix(ctx, *args):
    """Set the prefix to use for this guild."""
    id = str(ctx.guild.id)
    guild_prefixes[id] = default_prefix if not args else args[0]
    with open(prefix_file, 'w+') as f:
        json.dump(guild_prefixes, f)
    await ctx.send(f'Command prefix set to: *{guild_prefixes[id]}*')

@client.command(name='post',
                brief='Posts given number of posts from a subreddit.',
                aliases = aliases)
async def post(ctx, *args):
    """
    Return a given number of posts, up to 10, sorted by the alias that this was invoked with.
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

    # check for invocation errors
    command = ctx.invoked_with
    if not args:
        await ctx.send(f'Please specify subreddit. Usage: !{command} [subreddit]')
        return

    sub = args[0]
    # extract options from args
    args, options = extract_options(args)

    # extract sort method and retrieval count from command
    sort_by, lim = extract_command_info(command)

    # get the results from our request to Reddit.
    if sort_by == 'search':
        sort_by = 'relevance'
        tf = 'all'
        sub = 'all'
        if options:
            for o in options:
                if o in search_sorts:
                    sort_by = o
                elif o in filters:
                    tf = o
                elif sub_exists(o):
                    sub = o
        results = reddit.subreddit(sub).search(to_query_string(args), sort=sort_by, time_filter=tf, limit=lim)
    else:
        if not sub_exists(sub):
            await ctx.send(f'Specified subreddit {sub} does not exist.')
            return

        # get the number of stickied posts, so we can ignore them.
        num_stickied = len([s for s in getattr(reddit.subreddit(sub), sort_by)(limit=10) if s.stickied])
        results = [s for s in getattr(reddit.subreddit(sub), sort_by)(limit=lim+num_stickied) if not s.stickied]

    # format each submission into embedded messages and send to Discord.
    for submission in results:
        embed = create_submission_embed(submission)
        message = await ctx.send(embed=embed)
        for emoji in emojis:
            await message.add_reaction(emoji)

@client.command(name='user',
                brief='Finds specified Reddit user.')
async def user(ctx, *args):
    """Get a Reddit user's profile and send the embedded info to discord."""
    redditor = reddit.redditor(args[0])
    if user_exists(redditor):
        embed = create_user_embed(redditor)
    else:
        embed = create_empty_user_embed(redditor.name)
    await ctx.send(embed=embed)

@client.command(name='help',
                brief='Help menu.')
async def help(ctx, *args):
    """Custom help command. args contains specific commands."""
    embed = create_help_embed(*args)
    await ctx.send(embed=embed)

@client.command(name='auto',
                brief='toggles auto feed of a subreddit or multisubreddit to this channel.',
                aliases=['feed', 'autofeed'])
async def auto(ctx, *args):
    """Toggle autofeed command. Requires subreddit input."""
    global autofeed
    if autofeed:
        autofeed.cancel()
        autofeed = None
        await ctx.send('autofeed toggled to **[OFF]**')
        return

    if not args:
        await ctx.send('Please specify subreddit. Usage: !auto [subreddit]')
        return

    sub = [s for s in args if sub_exists(s)]
    if not sub:
        await ctx.send(f'Subreddit(s): {args} do not exist.')
        return

    plural = ''
    if len(sub) > 1:
        sub = '+'.join(sub)
        plural = 's'
    else:
        sub = sub[0]
    autofeed = feed.start(ctx, reddit.subreddit(sub))
    await ctx.send(f'autofeed toggled to **[ON]** for subreddit{plural}: *{sub}*')

@tasks.loop()
async def feed(ctx, subreddit):
    """Task for autofeed command. While autofeed is on, this will keep checking for new posts."""
    for submission in subreddit.stream.submissions(pause_after=0, skip_existing=True):
        if submission is None:
            await asyncio.sleep(10) # sleep for 10 seconds, let other tasks run
            continue
        embed = create_submission_embed(submission)
        message = await ctx.send(embed=embed)
        for emoji in emojis:
            await message.add_reaction(emoji)

#%% EMBED CREATION

def create_user_embed(redditor, url=''):
    """
    Return an embed containing the user profile information of redditor.
    Parameters
    ----------
    redditor : praw.models.Redditor
        The user to create the embed for.
    url : string, optional
        The url to the original post (if applicable). The default is ''.
    Returns
    -------
    embed : discord.embeds.Embed
        The embed object to return.
    """
    embed = discord.Embed(title=f'{redditor.name}\'s Profile', color=0x0051b7, description=url)
    embed.set_author(name=f'u/{redditor.name}', icon_url=redditor.icon_img)
    embed.set_thumbnail(url=redditor.icon_img)
    embed.add_field(name='User\'s Karma: ', value=redditor.comment_karma + redditor.link_karma)
    embed.add_field(name='URL to profile: ', value=base_url + '/user/' + redditor.name)

    top_comment = list(redditor.comments.top("all", limit=1))
    if len(top_comment) > 0:
        embed.add_field(name=f'\nTop comment by {redditor.name}: ', value=top_comment[0].body, inline = False)
    else:
        embed.add_field(name=f'Top comment by {redditor.name}: ', value='User has no comments!', inline = False)

    return embed

def create_empty_user_embed(redditor, url=''):
    """Return an embed for a nonexistent redditor."""
    return discord.Embed(title='User does not exist, or has been deleted.', color=0x0051b7, description=url)

def create_submission_embed(submission):
    """
    Return an embed object for a submission.
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
    abridged_title = (submission.title[:title_lim])
    if len(submission.title) > title_lim:
        abridged_title += '...'
    embed = discord.Embed(title=abridged_title, color=0xff5700, description=base_url+url)
    if user_exists(submission.author):
        embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
    else:
        embed.set_author(name='u/deleted', icon_url='https://i.imgur.com/ELSjbx7.png')
    new_url = url_morph(submission.url)
    #print (submission.is_self)
    #print (is_image(new_url))
    #print (new_url)
    if not submission.is_self and is_image(new_url):
        embed.set_image(url=new_url)
    embed.add_field(name='Upvotes:', value=submission.score)
    embed.set_thumbnail(url='https://i.imgur.com/5uefD9U.png')
    return embed

def create_body_embed(submission):
    """
    Return an embed object for the text body (if applicable) of a submission.
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
    abridged_title = (submission.title[:title_lim])
    if len(submission.title) > title_lim:
        abridged_title += '...'
    embed = discord.Embed(title=abridged_title, color=0xff5700, description=base_url + url)

    if user_exists(submission.author):
        embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
    else:
        embed.set_author(name='u/deleted', icon_url='https://i.imgur.com/ELSjbx7.png')

    if submission.is_self:
        abridged_text = (submission.selftext[:body_lim])
        if len(submission.selftext) > body_lim:
            abridged_text += '...'
        embed.add_field(name='Text:', value=abridged_text)
    else:
        embed.add_field(name='No text!', value='This post contains no text body.')
    return embed

def create_comment_embed(submission):
    """
    Return an embed object for the comments of a submission.
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
    abridged_title = (submission.title[:title_lim])
    if len(submission.title) > title_lim:
        abridged_title += '...'
    embed = discord.Embed(title=abridged_title, color=0xff5700, description=base_url + url)
    if user_exists(submission.author):
        embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
    else:
        embed.set_author(name='u/deleted', icon_url='https://i.imgur.com/ELSjbx7.png')

    best_comments = list(submission.comments)

    for i, v in enumerate(best_comments):
        if i == 10:
            break
        abridged_comment = (v.body[:comment_lim])
        if len(v.body) > comment_lim:
            abridged_comment += '...'
        if user_exists(v.author):
            embed.add_field(name=f'{v.author.name} - {v.score} points' , value=abridged_comment, inline = False)
        else:
            embed.add_field(name=f'u/deleted - {v.score} points' , value=abridged_comment, inline = False)

    if not best_comments:
        embed.add_field(name='No comments!', value='This post contains no comments.', inline=False)

    return embed

def create_help_embed(*args):
    """
    Return an embed object for the help function output.
    Returns
    -------
    embed : discord.embeds.Embed
        The embed object to return.
    """

    # check for post command.
    post = [s for s in sort if s != 'search']
    post.append('post')

    # autofeed aliases
    autos = ' | '.join(['auto', 'feed', 'autofeed'])

    # example strings
    auto_ex = ''
    post_ex = ''
    search_ex = ''
    user_ex = ''
    prefix_ex = ''

    embed = discord.Embed(title='HELP MENU', color=0x8A9CFE, description='')
    embed.set_thumbnail(url='https://i.imgur.com/tz7I0OI.jpg')

    if any(arg in args for arg in ['reactions']) or not args:
        embed.add_field(name='Reaction Usage', value=f'\
                        Click on one of these underneath a post to react to it.\n\n\
                        {emojis[0]} : display post\'s summary (default)\n\n\
                        {emojis[1]} : display post\'s body\n\n\
                        {emojis[2]} : display post\'s author profile\n\n\
                        {emojis[3]} : dispay post\'s comments\n', inline=False)

    if any(arg in args for arg in ['auto', 'feed', 'autofeed']) or not args:
        embed.add_field(name='Autofeed Commands', value=f'Requires at least 1 subreddit.\
                        Automatically post new submissions as they are posted to reddit.\n\n\
                        ![{autos}] [subreddit 1] [subreddit 2] [subreddit ...]', inline=False)
        auto_ex = '!auto memes dankmemes MemeEconomy\n'

    if any(arg in args for arg in post) or not args:
        embed.add_field(name='Subreddit Commands', value='Requires a number. \
                        Post up to 10 posts based on your sort preference.\n\n\
                        ![hot | top | new | rising][1-10] [subreddit]', inline=False)
        post_ex = '!top5 pics\n'
    if any(arg in args for arg in ['search']) or not args:
        ss = ' | '.join(search_sorts)
        fs = ' | '.join(filters)
        embed.add_field(name='Search Commands', value=f'Requires a number and search terms.\
                        Post up to 10 posts filtered by your search terms.\
                        Arguments with the \'-\' prefix are optional.\
                        Defaults to r/all.\n\n\
                        !search[1-10] [search terms] -[{ss}] -[{fs}] -[subreddit]', inline=False)
        search_ex = '!search5 Covid-19 -worldnews -top -all\n'
    if any(arg in args for arg in ['user']) or not args:
        embed.add_field(name='User Commands', value='Search for a user\'s profile.\n\n\
                        !user [reddit username]', inline=False)
        user_ex = '!user gallowboob\n'

    if any(arg in args for arg in ['prefix']) or not args:
        embed.add_field(name='Prefix Commands', value='Change EpicBot\'s prefix\
                        If no prefix is provided then it will reset to the default.\
                        Default is !\n\n\
                        [current prefix]prefix [new prefix or nothing to reset to !]')
        prefix_ex = '!prefix ~'
    if not (args and args[0] == 'reactions'):
        embed.add_field(name='Examples', value=f'{auto_ex}\n{post_ex}\n{search_ex}\n{user_ex}\n{prefix_ex}', inline=False)

    return embed

#%% OTHER HELPERS

def sub_exists(subreddit):
    """
    Return whether a given subreddit exists.
    Parameters
    ----------
    subreddit : praw.models.Subreddit
        The subreddit object to check.
    Returns
    -------
    bool
        Whether or not the subreddit exists.
    """
    exists = True
    try:
        reddit.subreddits.search_by_name(subreddit, exact=True)
    except NotFound:
        exists = False
    return exists

def user_exists(user):
    """Return whether a given user exists."""
    try:
        if user is None:
            return False
        if getattr(user, 'is_suspended', False):
            return False
    except NotFound:
        return False
    return True

def to_query_string(args):
    """Return the arguments as a single string."""
    return ' '.join(args)

def is_image(url):
    """Return whether or not the given url links to an image."""
    return any(e in url for e in extensions)

def url_morph(url):
    """
    Return a an image url with the extension edited for the embed.
    Parameters
    ----------
    url : string
        The url to morph.
    Returns
    -------
    url : string
        the url with a proper extension for embedding into disord.
    """
    if 'gifv' in url:
        url = url[:-1]
    if 'imgur'in url and 'jpg' not in url and 'gif' not in url and 'png' not in url:
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
    return sort_by, lim

def extract_options(args):
    """
    extracts the options from args and returns them as a list
    Parameters
    ----------
    args : list
        The argument list.
    Returns
    -------
    args : list
        The args list without any options in it.
    options : list
        The options that the command was invoked with.
    """
    options = []
    for s in args:
        if s[0] == '-':
            options.append(s[1:])
    return [s for s in args if s[1:] not in options], options

#%% MAIN

if __name__ == '__main__':
	try:
		client.run(TOKEN)
	except KeyboardInterrupt:
		print('exiting\n')
		exit(0)
	except:
		pass