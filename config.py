#!/usr/bin/env python3

import os

##### connect.py stuff
DB_URL = os.environ['DATABASE_URL']


##### main.py stuff
TOKEN = os.environ['DISCORD_TOKEN']
TESTING = False # if set to true, stats will not be recorded to the database
MM_GUILD_ID = 581695290986332160 # Meme Madness guild ID
ADMIN_IDS = [324273473360887808, 380462665358901268] # admin user IDs (lukenamop, eltoch)
CYCLE = 604800 # 7 days

MATCH_TIME = 1800 # 30 minutes
MATCH_WARN1_TIME = 900 # 15 minutes
MATCH_WARN2_TIME = 1500 # 25 minutes

BASE_POLL_TIME = 7200 # 2 hours
THIRD_PLACE_POLL_TIME = 14400 # 4 hours
FINAL_POLL_TIME = 21600 # 6 hours
if TESTING:
	BASE_POLL_TIME = 30

# round role IDs (Preliminary, Round 1, Round 2, Round 3, Semi-Finalist, Finalist)
ROUND_ROLE_IDS = [634855120672391188, 634854136268980244, 634854070309355542, 634853838611939347, 634853782815113216, 634853736144961580]
WINNER_ROLE_ID = 600857122032451594 # Past Winner role ID
ARCHIVE_CHAN_ID = 636263404444844062 # channel ID for archiving winning images
TEMPLATE_CHAN_ID = 599333803407835147 # channel ID for saving templates
SIGNUP_CHAN_ID = 638796625573183488 # channel ID for signup confirmations
DUELMODS_CHAN_ID = 600397545050734612 # channel ID for #duel-mods


##### verify.py stuff
CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
R_PASSWORD = os.environ['REDDIT_PASSWORD']
R_USERNAME = os.environ['REDDIT_USERNAME']
USER_AGENT = 'heroku:madnessmod-discord-bot (by /u/lukenamop)'