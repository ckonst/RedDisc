import epicbot
from discord.ext import commands
import os

import nest_asyncio
nest_asyncio.apply()

test_bot = commands.Bot(command_prefix='t!')
TOKEN = os.getenv('DISCORD_TOKEN')

post = ['hot', 'top', 'new', 'rising']
commands = {'hot' : True, 'top' : True, 'new' : True, 'rising' : True,
            'search' : True, 'user' : True, 'auto' : True, 'prefix' : True,
            'help' : True}

with open('tests.txt', 'r') as f:
    tests = f.readlines()

tests = [t.strip() for t in tests]
current = ''

@test_bot.command(name='test')
async def test(ctx, *args):
    global current
    for t in tests:
        if current in post:
            current = 'post'
        if t in commands:
            current = t
            continue
        await ctx.invoke(epicbot.client.get_command(current), *(t.split(' ')))
        #await asyncio.sleep(10) # sleep for 10 seconds

@test_bot.event
async def on_ready():
    """Print messages to indicate a successful login."""
    print('TEST BOT Logged in as')
    print(test_bot.user.name)
    print(test_bot.user.id)
    print('------')

try:
	test_bot.run(TOKEN)
except KeyboardInterrupt:
	print('exiting\n')
	exit(0)
except:
	pass