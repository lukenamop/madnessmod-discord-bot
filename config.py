#!/usr/bin/env python3

import os

# connect.py stuff
DB_URL = os.environ['DATABASE_URL']

# main.py stuff
TOKEN = os.environ['DISCORD_TOKEN']
MM_GUILD_ID = 581695290986332160 # Meme Madness guild ID
CYCLE = 604800 # 7 days
MATCH_TIME = 1800 # 30 minutes
MATCH_WARN1_TIME = 900 # 15 minutes
MATCH_WARN2_TIME = 1500 # 25 minutes
BASE_POLL_TIME = 7200 # 2 hours

# verify.py stuff
CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
R_PASSWORD = os.environ['REDDIT_PASSWORD']
R_USERNAME = os.environ['REDDIT_USERNAME']
USER_AGENT = 'heroku:madnessmod-discord-bot (by /u/lukenamop)'