import discord
from discord import Client
from discord.ext.commands import Bot
import praw
from dotenv import load_dotenv
import os

# comment out these two lines if you are not using spyder
import nest_asyncio
nest_asyncio.apply()

BOT_PREFIX = ('!')
client = Bot(command_prefix=BOT_PREFIX)
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET') + 'M'
ID = os.getenv('CLIENT_ID')
print(SECRET)
print(ID)

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

@client.command(name='title',
                brief='posts the top 5 post titles in a given subreddit')
async def title(ctx, *args):
    if not args:
        await ctx.channel.send('Please specify subreddit')
    for submission in reddit.subreddit(args[0]).hot(limit=5):
        print(submission)
        await ctx.channel.send(submission.title)

@client.command(name = 'quit',
				brief = 'closes the bot',
				aliases = ['q', 'e', 'exit'])
async def quit(ctx):
    await ctx.send('*exiting*')
    await client.logout()

if __name__ == '__main__':
	try:
		client.run(TOKEN)
	except KeyboardInterrupt:
		print('exiting\n')
		exit(0)
	except:
		pass