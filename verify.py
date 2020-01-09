#!/usr/bin/env python3

# import libraries
import praw
import re

# import additional files
import config

def initialize_reddit():
	reddit = praw.Reddit(client_id=config.R_CLIENT_ID,
		client_secret=config.R_CLIENT_SECRET,
		password=config.R_PASSWORD,
		username=config.R_USERNAME,
		user_agent=config.R_USER_AGENT)
	return reddit

def send_message(username, key, username_discriminator, mex=False):
	if not bool(re.match('^[a-zA-Z0-9\_\-]+$', username)) or len(username) > 20:
		return None
	# initialize a reddit connection
	reddit = initialize_reddit()
	message_title = 'Discord Verification'
	if mex:
		contact = 'u/lukenamop or u/l3dar'
	else:
		contact = 'u/lukenamop or lukenamop#0918'
	message_body = 'Your 6 character verification key: `' + key + '`\n\nA Discord verification was requested for this account by ' + username_discriminator + '.\n\n^(If you didn\'t request this verification, contact ' + contact + ' immediately.)'
	try:
		# find the specified redditor
		redditor = reddit.redditor(username)
		# send a reddit message
		redditor.message(message_title, message_body)
	except praw.exceptions.APIException:
		return None
	return redditor.name

def extra_checks(username):
	# initialize a reddit connection
	reddit = initialize_reddit()
	# find the specified redditor
	redditor = reddit.redditor(username)
	return None