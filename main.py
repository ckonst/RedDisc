import discord
import praw

client = discord.Client()
reddit = praw.Reddit(client_id="oBMX1JClXgCF0A",
                     client_secret="2V0JrFT97T1iOzMVrcjqNstg1LM",
                     user_agent="EpicBot for Reddit")


@client.event
async def on_message(message):
    if (message.content.find("!hey")) != -1:
        for submission in reddit.subreddit("pcmasterrace").hot(limit=5):
            await message.channel.send(submission.title)




client.run("NzUxNjgyNzA0NjcxNjM3NTE0.X1MpEg.Wk1noo-DKjXcGLWyyxc4GEd0Gjs")


