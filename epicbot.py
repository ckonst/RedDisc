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
subreddit_aliases = ['hot{}'.format(i+1) for i in range(10)]+\
          ['top{}'.format(i+1) for i in range(10)]+\
          ['new{}'.format(i+1) for i in range(10)]+ \
          ['rising{}'.format(i+1) for i in range(10)]

search_aliases = ['search{}'.format(i+1) for i in range(10)]

#topx = ['top{}'.format(i+1) for i in range(10)]
baseURL = 'https://www.reddit.com'


reddit = praw.Reddit(client_id=ID,
                            client_secret=SECRET,
                            user_agent="EpicBot for Reddit")
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(name='hey',
                brief='The bot says hi',
                aliases = ['hi','greetings','hello'])
async def hey(ctx):
    # we do not want the bot to reply to itself
    if ctx.message.author.id == client.user.id:
        return
    await ctx.send('hey {0.author.mention}'.format(ctx.message))

@client.command(name='Post',
                brief='Posts given number of posts from a subreddit.',
                aliases = subreddit_aliases+search_aliases)
async def hot(ctx, *args):
    if not args:
        if ctx.invoked_with in subreddit_aliases:
            await ctx.channel.send('Please specify subreddit!  Correct usage is: !'+ctx.invoked_with + ' [subreddit]')
        if ctx.invoked_with in search_aliases:
            await ctx.channel.send('Please specify what to search for!  Correct usage is: !' + ctx.invoked_with + ' [word to search]')

        return
    if not sub_exists(args[0]):
        await ctx.channel.send('Specified subreddit "' + args[0] + '" does not exist.')
        return
    if ctx.invoked_with not in subreddit_aliases+search_aliases:
        await ctx.channel.send('Invalid command.  Use !help for a list of valid commands.')
        return
    lim = ''.join(c for c in ctx.invoked_with if c.isdigit())
    if not lim:
        lim = 5
    lim = int(lim)



    command = ''.join(c for c in ctx.invoked_with if not c.isdigit()).lower()


    post_type = None


    if command == 'hot':
        post_type = reddit.subreddit(args[0]).hot(limit=lim)
    elif command == 'top':
        post_type = reddit.subreddit(args[0]).top(limit=lim)
    elif command == 'new':
        post_type = reddit.subreddit(args[0]).rising(limit=lim)
    elif command == 'rising':
        post_type = reddit.subreddit(args[0]).new(limit=lim)
    elif command == 'search':
        post_type = reddit.subreddit("all").search(args_add(args), limit=lim)



    for submission in post_type:
        abridged_title = (submission.title[:250] + '...') if len(submission.title) > 250 else submission.title
        embedVar = discord.Embed(title = abridged_title, color = 0xff5700)
        if user_exists(submission.author.name):
            embedVar.set_author(name="u/"+submission.author.name, icon_url= submission.author.icon_img)
        else:
            embedVar.set_author(name="u/deleted", icon_url = 'https://i.imgur.com/ELSjbx7.png')
        if not submission.is_self:
            embedVar.set_image(url= submission.url)
            #print(submission.url)
        embedVar.add_field(name="URL:", value=baseURL + submission.permalink)
        embedVar.add_field(name="Upvotes:", value=submission.score)
        embedVar.set_thumbnail(
            url='https://i.imgur.com/5uefD9U.png',
                  )
        await ctx.channel.send(embed=embedVar)




def sub_exists(subreddit):
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