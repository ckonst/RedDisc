import discord
from discord import Client
from discord.ext.commands import Bot
import praw
from dotenv import load_dotenv
import os

# comment out these two lines if you are not using spyder
#import nest_asyncio
#nest_asyncio.apply()

BOT_PREFIX = ('!')
client = Bot(command_prefix=BOT_PREFIX)
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET')
ID = os.getenv('CLIENT_ID')
topx = ['top{}'.format(i+1) for i in range(10)]
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

@client.command(name='top',
                brief='Posts given number of posts from a subreddit.',
                aliases = topx)
async def top(ctx, *args):
    if not args:
        await ctx.channel.send('Please specify subreddit')
        return
    if ctx.invoked_with not in topx:
        await ctx.channel.send('Invalid command.  Use !help for a list of valid commands.')
        return
    lim = ''.join(c for c in ctx.invoked_with if c.isdigit())
    if not lim:
        lim = 5
    lim = int(lim)


    for submission in reddit.subreddit(args[0]).hot(limit=lim):
        embedVar = discord.Embed(title = submission.title, color = 0xff5700)
        embedVar.set_author(name="u/"+submission.author.name, icon_url= submission.author.icon_img)
        if not submission.is_self:
            embedVar.set_image(url= submission.url)
        embedVar.add_field(name="URL:", value=baseURL + submission.permalink)
        embedVar.add_field(name="Upvotes:", value=submission.score)
        embedVar.set_thumbnail(
            url='https://i.imgur.com/5uefD9U.png',
                  )
        await ctx.channel.send(embed=embedVar)




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