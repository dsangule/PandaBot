from discord.ext import commands, tasks
import discord
import os
from dataclasses import dataclass
import datetime
import requests
import json

MAX_SESSION_TIME_MINUTES = 30

@dataclass
class Session:
  is_active: bool = False
  start_time: int = 0

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
session = Session()

@bot.event
async def on_ready():
  print(f'Logged in as {bot.user}')

@tasks.loop(minutes=MAX_SESSION_TIME_MINUTES, count=2)
async def break_reminder():
  if break_reminder.current_loop == 0:
    return
  await timer_channel.send(f"Take a break! You've been studying for {MAX_SESSION_TIME_MINUTES} minutes.")

@bot.command()
async def start(ctx):
  if session.is_active:
    await ctx.send('Session is already active')
    return
  global timer_channel
  timer_channel = ctx.channel
  session.is_active = True
  session.start_time = ctx.message.created_at.timestamp()
  human_readable_time = ctx.message.created_at.strftime('%H:%M:%S')
  break_reminder.start()
  await ctx.send(f'New session started at {human_readable_time}')

@bot.command()
async def stop(ctx):
  if not session.is_active:
    await ctx.send('No session is active')
    return
  session.is_active = False
  end_time = ctx.message.created_at.timestamp()
  duration = end_time - session.start_time
  human_readable_time = ctx.message.created_at.strftime('%H:%M:%S')
  human_readable_duration = str(datetime.timedelta(seconds=duration))
  break_reminder.stop()
  await ctx.send(f'Session ended at {human_readable_time} with a duration of {human_readable_duration}')

@bot.command()
async def github(ctx):
  github_username = ctx.message.content.split(' ')[-1]
  response = requests.get(f'https://api.github.com/users/{github_username}')
  if response.status_code == 200:
    user_data = response.json()
    user_details = f"Username: {user_data['login']}\n"
    repos_response = requests.get(user_data['repos_url'])
    if repos_response.status_code == 200:
      repos_data = repos_response.json()
      user_repos = [repo['name'] for repo in repos_data]
      sep = "\n - "
      await ctx.send(f"```{user_details}\nRepositories:\n - {sep.join(user_repos)}```")
    else:
      await ctx.send('Failed to fetch user repositories')
  else:
    await ctx.send('User not found')

bot.run(os.environ['TOKEN'])