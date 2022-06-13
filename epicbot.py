# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# 
# Created by Christian Konstantinov and Paul Armati
# Version 1.2.4
# Python 3.8.5
#
# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import discord
import json
import os
import praw

from discord.ext import tasks, commands

from dotenv import load_dotenv

from prawcore import NotFound
from praw.exceptions import InvalidURL

from typing import Any, List, Tuple

# comment out these two lines if you are not using Spyder
# hint: don't use Spyder
# import nest_asyncio
# nest_asyncio.apply()

# ------------------------------------------------------------------------------
# Startup
# ------------------------------------------------------------------------------

async def get_prefix(bot, msg) -> str:
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

with open(prefix_file := 'prefixes.json') as f:
    guild_prefixes = json.load(f)
default_prefix = '!'

client = commands.Bot(command_prefix=get_prefix)
load_dotenv()
client.remove_command('help')

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET')
ID = os.getenv('CLIENT_ID')
SORT = ('hot', 'top', 'new', 'rising', 'search')
# don't use a tuple comprehension, it won't work, yes I tried. 
ALIASES = tuple([f'{s}{j}' for j in range(1, 11) for s in SORT])
EMOJIS = ('📃','📄', '👤', '💬')
SEARCH_SORTS = ('relevance', 'top', 'new', 'comments')
FILTERS = ('all', 'hour', 'day', 'week', 'month', 'year')
EXTENSIONS = ('gif', 'jpg', 'png')
BASE_URL = 'https://www.reddit.com'
TITLE_LIM = 250
BODY_LIM = 1020
COMMENT_LIM = 100
autofeed = None

reddit = praw.Reddit(client_id=ID,
                            client_secret=SECRET,
                            user_agent="EpicBot for Reddit")

# ------------------------------------------------------------------------------
# Events
# ------------------------------------------------------------------------------

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Event handler for reactions.

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
    emoji = payload.emoji.name
    if not is_me(payload.user_id) and emoji in EMOJIS:
        m_id = payload.message_id
        message = await client.get_channel(payload.channel_id).fetch_message(m_id)
        embed = message.embeds[0]
        await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))

        if emoji == '📃' and message.author.id == client.user.id:
            # short submission embed.
            submission = reddit.submission(url=embed.description)
            new_embed = create_submission_embed(submission)
        elif emoji == '👤' and message.author.id == client.user.id:
            # profile of original poster.
            if user_exists(reddit.redditor(embed.author.name[2:])):
                new_embed = create_user_embed(reddit.redditor(embed.author.name[2:]), embed.description)
            else:
                new_embed = create_empty_user_embed(reddit.redditor(embed.author.name[2:]), embed.description)
        elif emoji == '📄' and message.author.id == client.user.id:
            # extended submission embed.
            submission = reddit.submission(url=embed.description)
            new_embed = create_body_embed(submission)
        elif emoji == '💬' and message.author.id == client.user.id:
            # comments on this post.
            submission = reddit.submission(url=embed.description)
            new_embed = create_comment_embed(submission)

        await message.edit(embed=new_embed)

@client.event
async def on_ready():
    """Print messages to indicate a successful login."""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# ------------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------------

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

async def do_nothing():
    pass

@tasks.loop()
async def feed(ctx, subreddit):
    """Task for autofeed command. While autofeed is on, this will keep checking for new posts."""
    for submission in subreddit.stream.submissions(pause_after=0, skip_existing=True):
        if submission is None:
            await do_nothing() # return to the event loop to let other coroutines run.
            continue
        embed = create_submission_embed(submission)
        message = await ctx.send(embed=embed)
        for emoji in EMOJIS:
            await message.add_reaction(emoji)

@client.command(name='help',
                brief='Help menu.')
async def help(ctx, *args):
    """Custom help command. args contains specific commands.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context in which this command was called.
    *args : list
        The arguments that the user passed through.
        Specifying a command or commands will output only those specified.
        If no args are passed, information on all commands will be shown.
    
    Returns
    -------
    None.
    """
    embed = create_help_embed(*args)
    await ctx.send(embed=embed)

@client.command(name='post',
                brief='Posts given number of posts from a subreddit.')
async def post(ctx, *args):
    """Post to the Discord channel from a direct Reddit Link.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context in which this command was called.
    *args : list
        The arguments that the user passed through.
        Only the first argument will be checked.
    
    Returns
    -------
    None.
    """
    if len(args) > 0:
        try:
            submission = reddit.submission(url=args[0])
            embed = create_submission_embed(submission)
            message = await ctx.send(embed=embed)
            for emoji in EMOJIS:
                await message.add_reaction(emoji)
        except InvalidURL:
            await ctx.send('Enter a valid reddit post URL.')
        except NotFound:
            await ctx.send('Enter a valid reddit post URL.')
    else:
        await ctx.send('Please specify post URL.  Usage: !post [URL]')

@client.command(name='posts',
                brief='Posts given number of posts from a subreddit.',
                aliases = ALIASES)
async def posts(ctx, *args):
    """Return a given number of posts.

    A maximum of 10 posts is allowed.
    Posts are sorted by the alias that this was invoked with.
    
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
    if command == 'posts':
        return
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
                if o in SEARCH_SORTS:
                    sort_by = o
                elif o in FILTERS:
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
        for emoji in EMOJIS:
            await message.add_reaction(emoji)

@client.command()
@commands.guild_only()
async def prefix(ctx, *, arg):
    """Set the prefix to use for this guild."""
    id = str(ctx.guild.id)
    guild_prefixes[id] = default_prefix if not arg else arg
    with open(prefix_file, 'w+') as f:
        json.dump(guild_prefixes, f)
    await ctx.send(f'Command prefix set to: *{guild_prefixes[id]}*')

@client.command(name='user',
                brief='Finds specified Reddit user.')
async def user(ctx, *, arg):
    """Get a Reddit user's profile and send the embedded info to discord."""
    redditor = reddit.redditor(arg)
    if user_exists(redditor):
        embed = create_user_embed(redditor)
    else:
        embed = create_empty_user_embed(redditor.name)
    await ctx.send(embed=embed)

# ------------------------------------------------------------------------------
# Embed Creation
# ------------------------------------------------------------------------------

def create_body_embed(submission: praw.models.Submission) -> discord.embeds.Embed:
    """Return an embed object for the text body (if applicable) of a submission.
    
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
    abridged_title = (submission.title[:TITLE_LIM])
    if len(submission.title) > TITLE_LIM:
        abridged_title += '...'
    embed = discord.Embed(title=abridged_title, color=0xff5700, description=BASE_URL+url)

    if user_exists(submission.author):
        embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
    else:
        embed.set_author(name='u/deleted', icon_url='https://i.imgur.com/ELSjbx7.png')

    if submission.is_self:
        abridged_text = (submission.selftext[:BODY_LIM])
        if len(submission.selftext) > BODY_LIM:
            abridged_text += '...'
        embed.add_field(name='Text:', value=abridged_text)
    else:
        embed.add_field(name='No text!', value='This post contains no text body.')
    return embed

def create_comment_embed(submission: praw.models.Submission) -> discord.embeds.Embed:
    """Return an embed object for the comments of a submission.
    
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
    abridged_title = (submission.title[:TITLE_LIM])
    if len(submission.title) > TITLE_LIM:
        abridged_title += '...'
    embed = discord.Embed(title=abridged_title, color=0xff5700, description=BASE_URL+url)
    if user_exists(submission.author):
        embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
    else:
        embed.set_author(name='u/deleted', icon_url='https://i.imgur.com/ELSjbx7.png')

    best_comments = list(submission.comments)

    for i, v in enumerate(best_comments):
        if i == 10:
            break
        abridged_comment = (v.body[:COMMENT_LIM])
        if len(v.body) > COMMENT_LIM:
            abridged_comment += '...'
        if user_exists(v.author):
            embed.add_field(name=f'{v.author.name} - {v.score} points' , value=abridged_comment, inline = False)
        else:
            embed.add_field(name=f'u/deleted - {v.score} points' , value=abridged_comment, inline = False)

    if not best_comments:
        embed.add_field(name='No comments!', value='This post contains no comments.', inline=False)

    return embed

def create_help_embed(*args) -> discord.embeds.Embed:
    """Return an embed object for the help function output.
    
    Returns
    -------
    embed : discord.embeds.Embed
        The embed object to return.
    """

    # check for post command.
    posts = [s for s in SORT if s != 'search']
    posts.append('posts')

    # autofeed aliases
    autos = ' | '.join(['auto', 'feed', 'autofeed'])

    # example strings
    auto_ex = ''
    post_ex = ''
    posts_ex = ''
    search_ex = ''
    user_ex = ''
    prefix_ex = ''

    embed = discord.Embed(title='HELP MENU', color=0x8A9CFE, description='')
    embed.set_thumbnail(url='https://i.imgur.com/tz7I0OI.jpg')

    if any(arg in args for arg in ['reactions', 'reaction']) or not args:
        embed.add_field(name='Reaction Usage', value=f'\
                        Click on one of these underneath a post to react to it.\n\n\
                        {EMOJIS[0]} : display post\'s summary (default)\n\n\
                        {EMOJIS[1]} : display post\'s body\n\n\
                        {EMOJIS[2]} : display post\'s author profile\n\n\
                        {EMOJIS[3]} : dispay post\'s comments\n', inline=False)

    if any(arg in args for arg in ['help']) or not args:
        embed.add_field(name='Help Commands', value=f'Shows this message.\
                        Individual Command(s) can be specified to filter the unspecified command(s)..\n\n\
                        !help\n\n\
                        !help [command 1] [command 2] [command ...]', inline=False)
        auto_ex = '!auto memes dankmemes MemeEconomy\n'

    if any(arg in args for arg in ['auto', 'feed', 'autofeed']) or not args:
        embed.add_field(name='Autofeed Commands', value=f'Requires at least 1 subreddit.\
                        Automatically post new submissions as they are posted to reddit.\n\n\
                        ![{autos}] [subreddit 1] [subreddit 2] [subreddit ...]', inline=False)
        auto_ex = '!auto memes dankmemes MemeEconomy\n'

    if any(arg in args for arg in posts) or not args:
        embed.add_field(name='Subreddit Commands', value='Requires a number. \
                        Post up to 10 posts based on your sort preference.\n\n\
                        ![hot | top | new | rising][1-10] [subreddit]', inline=False)
        posts_ex = '!top5 pics\n'
    if any(arg in args for arg in ['post']) or not args:
        embed.add_field(name='Post Command', value='Requires a full post URL. \
                                Find a single post using the full URL of the post.\n\n\
                                !post [URL]', inline=False)
        post_ex = '!post https://www.reddit.com/...\n'
    if any(arg in args for arg in ['search']) or not args:
        ss = ' | '.join(SEARCH_SORTS)
        fs = ' | '.join(FILTERS)
        embed.add_field(name='Search Commands', value=f'Requires a number and search terms.\
                        Post up to 10 posts filtered by your search terms.\
                        Arguments with the \'-\' prefix are optional.\
                        Defaults to r/all.\n\n\
                        !search[1-10] [search terms] -[{ss}] -[{fs}] -[subreddit]', inline=False)
        search_ex = '!search5 Covid-19 -worldnews -top -all\n'
    if any(arg in args for arg in ['user']) or not args:
        embed.add_field(name='User Commands', value='Search for a user\'s profile.\n\n\
                        !user [reddit username]', inline=False)
        user_ex = '!user Holofan4life\n'

    if any(arg in args for arg in ['prefix']) or not args:
        embed.add_field(name='Prefix Commands', value='Change EpicBot\'s prefix\
                        If no prefix is provided then it will reset to the default.\
                        Default is !\n\n\
                        [current prefix]prefix [new prefix or nothing to reset to !]')
        prefix_ex = '!prefix ~'
    if not (len(args) == 1 and 'reactions' in args):
        embed.add_field(name='Examples', value=f'{auto_ex}\n{posts_ex}\n{post_ex}\n\
                           {search_ex}\n{user_ex}\n\
                           {prefix_ex}\n\n!help auto prefix', inline=False)
    return embed

def create_submission_embed(submission: praw.models.Submission) -> discord.embeds.Embed:
    """Return an embed object for a submission.
    
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
    abridged_title = (submission.title[:TITLE_LIM])
    if len(submission.title) > TITLE_LIM:
        abridged_title += '...'
    embed = discord.Embed(title=abridged_title, color=0xff5700, description=BASE_URL+url)
    if user_exists(submission.author):
        embed.set_author(name=f'u/{submission.author.name}', icon_url=submission.author.icon_img)
    else:
        embed.set_author(name='u/deleted', icon_url='https://i.imgur.com/ELSjbx7.png')
    new_url = url_morph(submission.url)
    if not submission.is_self and is_image(new_url):
        embed.set_image(url=new_url)
    embed.add_field(name='Upvotes:', value=submission.score)
    embed.set_thumbnail(url='https://i.imgur.com/5uefD9U.png')
    return embed

def create_user_embed(redditor: praw.models.Redditor, url='') -> discord.embeds.Embed:
    """Return an embed containing the user profile information of redditor.
    
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
    embed.add_field(name='URL to profile: ', value=BASE_URL + '/user/' + redditor.name)

    top_comment = list(redditor.comments.top("all", limit=1))
    if len(top_comment) > 0:
        embed.add_field(name=f'\nTop comment by {redditor.name}: ', value=top_comment[0].body, inline = False)
    else:
        embed.add_field(name=f'Top comment by {redditor.name}: ', value='User has no comments!', inline = False)

    return embed

def create_empty_user_embed(redditor, url='') -> discord.embeds.Embed:
    """Return an embed for a nonexistent redditor."""
    return discord.Embed(title='User does not exist, or has been deleted.', color=0x0051b7, description=url)

# ------------------------------------------------------------------------------
# Other Helpers
# ------------------------------------------------------------------------------

def extract_command_info(command: str) -> Tuple[str, int]:
    """Return the invocation alias (sort_by) and limit given by the command.
    
    Parameters
    ----------
    command : str
        The invoked command.
    
    Returns
    -------
    sort_by : str
        The subreddit sorting method.
    lim : int
        How many submissions to post.
    """
    sort_by = ''.join([s for s in SORT if s in command]).lower()
    lim = command.replace(sort_by, '')
    if not lim:
        lim = 5
    lim = int(lim)
    return sort_by, lim

def extract_options(args: List[str]) -> Tuple[List[str], List[str]]:
    """Extract the options from args and returns them as a list.
    
    Parameters
    ----------
    args : List[str]
        The argument list.
    
    Returns
    -------
    args : List[str]
        The args list without any options in it.
    options : List[str]
        The options that the command was invoked with.
    """
    options = []
    for s in args:
        if s[0] == '-':
            options.append(s[1:])
    return [s for s in args if s[1:] not in options], options

def is_image(url: str) -> bool:
    """Return whether or not the given url links directly to an image."""
    return any(e in url for e in EXTENSIONS)

def is_me(_id):
    """Return whether the given id is the bot's id."""
    return _id == client.user.id

def sub_exists(subreddit: str) -> bool:
    """Return whether a given subreddit exists.
    
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

def to_query_string(args: List[str]) -> str:
    """Return the arguments as a single string."""
    return ' '.join(args)

def url_morph(url: str) -> str:
    """Return a an image url with the extension edited for the embed.
    
    Parameters
    ----------
    url : str
        The url to morph.
    
    Returns
    -------
    url : str
        the url with a proper extension for embedding into discord.
    """
    if 'gifv' in url:
        url = url[:-1]
    if 'imgur' in url and not any(e in url for e in EXTENSIONS):
        url += '.jpg'
    return url

def user_exists(user: praw.models.User) -> bool:
    """Return whether a given user exists."""
    try:
        if user is None:
            return False
        if getattr(user, 'is_suspended', False):
            return False
    except NotFound:
        return False
    return True

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        pass
    finally:
        print('exiting\n')

if __name__ == '__main__':
    main()
