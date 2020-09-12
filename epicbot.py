import discord
from discord import Client
from discord.ext.commands import Bot
import praw
from dotenv import load_dotenv
import os
from discord.ext import ui

# comment out these two lines if you are not using spyder
import nest_asyncio
nest_asyncio.apply()

BOT_PREFIX = ('!')
client = Bot(command_prefix=BOT_PREFIX)
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SECRET = os.getenv('CLIENT_SECRET')
ID = os.getenv('CLIENT_ID')
topx = ['top{}'.format(i+1) for i in range(10)]

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

@client.command(name='name',
                brief='tell the bot your name')
async def name(ctx):
    name = await ui.prompt(ctx, 'What is your name?')
    await ctx.send(f'Ok, your name is {name}')

@client.command(name='mood',
                brief='does shit idk lol')
async def mood(ctx):
    choices = ['red', 'blue', 'green', 'yellow']
    colour = await ui.select(ctx, 'What is your favo(u)rite colo(u)r?', choices)

    # Want buttons instead of text? No problem.

    choices = [
        ui.Choice('Very Happy', button='😄'),
        ui.Choice('Happy', button='🙂'),
        ui.Choice('Neutral', button='😐'),
        ui.Choice('Sad', button='😦'),
        ui.Choice('Very Sad', button='😢'),
    ]
    feeling = await ui.select(ctx, 'How are you feeling today?', choices)

@client.command(name='page',
                brief='does shit idk lol')
async def page(ctx):
    def some_statements():
        for i in range(20):
            yield f'This is sentence hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh {i}'

    def format_page(page):
        return f'This is a page\n{page}'

    paginator = ui.Paginator(some_statements(), page_formatter=format_page)
    await paginator.start(ctx)

    # And to chunk it:

    def format_chunk(chunk):
        # Formatters can return embeds too
        return discord.Embed(description='\n'.join(chunk))

    paginator = ui.Paginator.chunked(some_statements(), 10, page_formatter=format_chunk)
    await paginator.start(ctx)



@client.command(name='top',
                brief='posts the top 5 post titles in a given subreddit',
                aliases=topx
                )
async def top(ctx, *args):
    if not args:
        await ctx.channel.send('Please specify subreddit')
        return
    lim = ''.join(c for c in ctx.invoked_with if c.isdigit())
    if not lim:
        lim = 5
    lim =int(lim)
    for submission in reddit.subreddit(args[0]).hot(limit=lim):
        await ctx.channel.send(submission.title)

@top.error
async def top_error(ctx, error):
    await ctx.send(error)


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