#!/usr/bin/env python3

# import libraries
import praw
import re
import time

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
	checks = [0, 0, 0]

	# check to see if a users' account age is less than 30 days
	if redditor.created_utc < (time.time() - (30*24*60*60)):
		checks[0] = 1

	# check to see if a user has less than 1000 total karma
	if (redditor.link_karma + redditor.comment_karma) < 1000:
		checks[1] = 1

	# check to see if the user has verified their email
	if not redditor.has_verified_email:
		checks[2] = 1

	return checks