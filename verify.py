#!/usr/bin/env python3

# import libraries
import config
import praw
import re

def send_message(username, key, username_discriminator, mex=False):
	if not bool(re.match('^[a-zA-Z0-9\_\-]+$', username)) or len(username) > 20:
		return None
	reddit = praw.Reddit(client_id=config.CLIENT_ID,
		client_secret=config.CLIENT_SECRET,
		password=config.R_PASSWORD,
		username=config.R_USERNAME,
		user_agent=config.USER_AGENT)
	message_title = 'Discord Verification'
	if mex:
		contact = 'u/lukenamop or u/l3dar'
	else:
		contact = 'u/lukenamop or lukenamop#0918'
	message_body = 'Your 6 character verification key: `' + key + '`\n\nA Discord verification was requested for this account by ' + username_discriminator + '.\n\n^(If you didn\'t request this verification, contact ' + contact + ' immediately.)'
	try:
		redditor = reddit.redditor(username)
		redditor.message(message_title, message_body)
	except praw.exceptions.APIException:
		return None
	return redditor.name