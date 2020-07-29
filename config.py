#!/usr/bin/env python3

# import libraries
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

##### connect.py stuff #####

DB_URL = os.environ['DATABASE_URL']

G_KEY_FILE = 'meme-madness-discord-aca84f70f7a5.json'

google_key_json = {}
google_key_json["type"] = os.environ["G_TYPE"]
google_key_json["project_id"] = os.environ["G_PROJECT_ID"]
google_key_json["private_key_id"] = os.environ["G_PRIVATE_KEY_ID"]
google_key_json["private_key"] = os.environ["G_PRIVATE_KEY"]
google_key_json["client_email"] = os.environ["G_CLIENT_EMAIL"]
google_key_json["client_id"] = os.environ["G_CLIENT_ID"]
google_key_json["auth_uri"] = os.environ["G_AUTH_URI"]
google_key_json["token_uri"] = os.environ["G_TOKEN_URI"]
google_key_json["auth_provider_x509_cert_url"] = os.environ["G_AUTH_PROVIDER_X509_CERT_URL"]
google_key_json["client_x509_cert_url"] = os.environ["G_CLIENT_X509_CERT_URL"]

# outfile = open(G_KEY_FILE, 'w')
# outfile.write(json.dumps(google_key_json))
# outfile.close()

# Google API scope
G_SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# Google API creds
G_CREDS = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=google_key_json, scopes=G_SCOPE)


##### main.py stuff #####

TOKEN = os.environ['DISCORD_TOKEN']
CMD_PREFIX = '.' # the bot's command prefix
TESTING = False # if set to true, stats will not be recorded to the database
DISABLE_BOT = False # if set to true, only lukenamop can use the bot
MM_GUILD_ID = 581695290986332160 # Meme Madness guild ID
ADMIN_IDS = [324273473360887808, 380462665358901268, 583050600984346655] # admin user IDs (lukenamop, eltoch, UncreativeFilth)
CYCLE = 1209600 # 14 days

MATCH_TIME = 1800 # 30 minutes
MATCH_WARN1_TIME = 900 # 15 minutes
MATCH_WARN2_TIME = 1500 # 25 minutes

BASE_POLL_TIME = 7200 # 2 hours
POLL_EXTENSION_TIME = 3600 # 1 hour
MAX_POLL_EXTENSIONS = 4
THIRD_PLACE_POLL_TIME = 14400 # 4 hours
FINAL_POLL_TIME = 21600 # 6 hours
if TESTING:
	BASE_POLL_TIME = 60 # 1 minute
	POLL_EXTENSION_TIME = 60 # 1 minute

VOTE_STREAK_BONUSES = [0, 5, 10, 15, 25, 35, 50]

DUEL_MOD_ROLE_ID = 599996020171997206
ADMIN_ROLE_ID = 581697585354375179
# round role IDs (Preliminary, Round 1, Round 2, Round 3, Round 4, Round 5, Semi-Finalist, Finalist)
ROUND_ROLE_IDS = [634855120672391188, 634854136268980244, 634854070309355542, 634853838611939347, 641436347017461771, 668852447699009546, 634853782815113216, 634853736144961580]
WINNER_ROLE_ID = 600857122032451594 # Past Winner role ID
ARCHIVE_CHAN_ID = 636263404444844062 # channel ID for archiving winning images
TEMPLATE_CHAN_ID = 599333803407835147 # channel ID for saving templates
SUBMISSION_CHAN_ID = 599758863700328459 # channel ID for submitting final memes
SIGNUP_CHAN_ID = 638796625573183488 # channel ID for signup confirmations
MOD_SPAM_CHAN_ID = 600397545050734612 # channel ID for #mod-spam
MATCH_CATEGORY_ID = 639599353526485034 # category ID for #matches
ANNOUNCEMENTS_CHAN_ID = 581696676344102957 # channel ID for #announcements
INFO_CHAN_ID = 599299817608314880 # channel ID for #info
RULES_CHAN_ID = 581706416486744067 # channel ID for #rules
VERIFICATION_CHAN_ID = 581705191703838720 # channel ID for #verification
DEX_VERIFICATION_CHAN_ID = 607344923481473054 # channel ID for #verification in the DEX server
TEMP_ARCHIVE_CHAN_ID = 669305024656048200 # channel ID for #temp-archive
GENERAL_CHAN_ID = 581695290986332162 # channel ID for #general
STATS_CHAN_ID = 631239602736201728 # channel ID for #stats-flex


##### verify.py stuff #####

R_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
R_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
R_PASSWORD = os.environ['REDDIT_PASSWORD']
R_USERNAME = os.environ['REDDIT_USERNAME']
R_USER_AGENT = 'heroku:madnessmod-discord-bot (by /u/lukenamop)'


##### tourney_manager.py stuff #####

C_USERNAME = os.environ['CHALLONGE_USERNAME']
C_API_KEY = os.environ['CHALLONGE_API_KEY']