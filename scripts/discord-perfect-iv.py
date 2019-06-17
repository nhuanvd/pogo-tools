#!/usr/bin/python3
from time import strftime, localtime
import asyncio
import discord
import re
import os
import json

# Settings
min_iv_filter = 100
min_level_filter = 30
show_notification = True
read_pokemon_name = True
read_pokemon_level = True

# Your Discord token
# How to get toke: https://github.com/FOCI-DEV/Get-Discord-Token
token = "NTY4OTk2NzY0MjY3NTc3MzU0.XOYz6g.bzNmcZUp0a7vKyavFAB01L5-JiQ"

# Filter messages from some channels from https://discord.gg/pokedex100
accept_channels = ['259536527221063683', '261331571028656128', '394344511419056129', '259296509361782784', '259505011686375425']

# The notifier function
def notify(title, message):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(message, title))

def read_pokemon_info(data):
    message = ""
    if read_pokemon_name:
        message = data['name']
    if read_pokemon_level:
        if data['level'] == 35:
            message = "{} max level".format(message)
        else:
            message = "{} evel {}".format(message, data['level'])
    os.system("say {}".format(message))

# Bot
c = discord.Client()

@c.event
async def on_ready():
    welcome = "Logged in as {0.name} - {0.id}\n".format(c.user)
    # Make the log bot appear offline.
    await c.change_presence(status=discord.Status.invisible)
    print(welcome)

@c.event
async def on_message(message):
    channel = "{}".format(message.channel.id)
    if channel in accept_channels:
        parse_message(message)

def parse_message(message):
    data = {}
    for line in message.content.splitlines():
        if line.startswith(':flag_'):
            data = {**data, **parse_info(line)}
            continue
        if line.startswith('Community:'):
            data = {**data, **parse_url(line)}

    if data['iv'] >= min_iv_filter and data['level'] >= min_level_filter:
        print('{}\n'.format(json.dumps(data)))
        if show_notification:
            notify(title = 'New pokemon spawn',
                message = '{} - LV{} IV{} CP{}'.format(data['name'], data['level'], data['iv'], data['cp']))
        if read_pokemon_name:
            read_pokemon_info(data)

# Sample
# :flag_us: **Larvitar** <a:246:396699687710752769>  IV68** CP218 L8** ♂    - *Monte Sereno, California*
# :flag_us: **Anorith** <a:347:396708217440174084>  IV93** CP603 L14** ♂    - *Melrose Park, Cook County* <@&549113260922634240>
def parse_info(message):
    retValue = {}
    search = re.search(':flag_(.+?): .*', message)
    if search:
        retValue['country'] = search.group(1)

    search = re.search('\*\*(.+?)\*\*', message)
    if search:
        retValue['name'] = search.group(1)

    search = re.search('IV(.+?)\*\*', message)
    if search:
        retValue['iv'] = int(search.group(1))

    search = re.search('CP(.+?) L.*', message)
    if search:
        retValue['cp'] = int(search.group(1))

    search = re.search('CP.*L(.+?)\*\*.*', message)
    if search:
        retValue['level'] = int(search.group(1))

    search = re.search('.*- \*(.+?)\*.*', message)
    if search:
        retValue['city'] = search.group(1)

    search = re.search('.* <.*:.*:(.+?)> .*', message)
    if search:
        retValue['icon'] = 'https://cdn.discordapp.com/emojis/{}.gif'.format(search.group(1))

    if 'confirmed by' in message:
        retValue['confirmed'] = True

    return retValue

# Sample
# Community: <http://api.pokedex100.com/discord/free=EwS6Pr5pKMYZbW>
# Community: 16.1,108.12
def parse_url(string):
    data = string.replace('Community:', '').replace('<', '').replace('>', '').strip()
    if 'http' in data:
        return { 'url': data }
    return {}

c.run(token, bot=False)
