#!/usr/bin/env python3

# import libraries
import discord
import asyncio
import time
import datetime
import re
import os
import requests
import random
import string
import urllib
from unidecode import unidecode
from time import gmtime
from time import strftime

# import additional files
import config
import connect
import verify
import functions
import help_cmd
import tourney_manager

# intitialize discord client
client = discord.Client()

# log actions to the command line
async def action_log(reason):
	print(str(datetime.datetime.utcnow()) + ' - ' + reason)

# generate a discord embed with an optional attached image
async def generate_embed(color, title, description, attachment=None):
	# given color string, create color hex
	if color == 'green':
		color = 0x00cc00
	elif color == 'red':
		color = 0xe60000
	elif color == 'yellow':
		color = 0xffff33
	elif color == 'pink':
		color = 0xcc0099
	elif color == 'blue':
		color = 0x3399ff
	elif color == 'orange':
		color = 0xff9900

	# create discord embed
	embed = discord.Embed(
		color=color,
		title=title,
		description=description,
		timestamp=datetime.datetime.now())
	embed.set_footer(text='Developed by lukenamop#0918')
	if attachment is not None:
		embed.set_image(url=attachment)
	return embed

async def start_match(type, competitor1_id, competitor2_id=None):
	return

# client event triggers on any discord message
@client.event
async def on_message(message):
	# ignore bots
	if message.author.bot:
		# except for MadnessMod itself
		if message.author.id == 622139031756734492:
			if message.nonce == 'poll':
				# get base match channel
				base_channel = message.channel

				# add reactions to match poll in match channel
				await message.add_reaction('🇦')
				await message.add_reaction('🇧')
				await action_log('added reactions to poll message')
				vote_pings_role = message.channel.guild.get_role(600356303033860106)
				if not config.TESTING:
					await message.channel.send(vote_pings_role.mention + ' @here')
				else:
					await message.channel.send('This is just a test match, not pinging `Vote Pings` or `here`.')

				# sleep for 2 hours (config.BASE_POLL_TIME)
				await asyncio.sleep(config.BASE_POLL_TIME)
				await action_log('waking back up in match channel')
				await message.delete()

				# check to see who submitted each meme
				query = 'SELECT db_id, u1_id, u2_id, a_meme, u1_image_url, u2_image_url FROM matches WHERE channel_id = ' + str(message.channel.id) + ' AND start_time >= ' + str(time.time() - (config.BASE_POLL_TIME + config.MATCH_TIME + 30))
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				# check how many votes image A got
				query = 'SELECT COUNT(*) FROM votes WHERE match_id = ' + str(result[0]) + ' AND a_vote = True'
				connect.crsr.execute(query)
				a_votes = connect.crsr.fetchone()[0]
				# check how many votes image B got
				query = 'SELECT COUNT(*) FROM votes WHERE match_id = ' + str(result[0]) + ' AND b_vote = True'
				connect.crsr.execute(query)
				b_votes = connect.crsr.fetchone()[0]

				# find winning image
				if a_votes > b_votes:
					winning_image = 'A'
					winning_votes = a_votes
					losing_votes = b_votes
				elif b_votes > a_votes:
					winning_image = 'B'
					winning_votes = b_votes
					losing_votes = a_votes
				elif a_votes == b_votes:
					winning_image = 'tie'
					votes = a_votes

				# alert match channel of poll results
				try:
					if (result[3] == 1 and winning_image == 'A') or (result[3] == 2 and winning_image == 'B'):
						winner = base_channel.guild.get_member(result[1])
						winning_image_url = result[4]
						loser = base_channel.guild.get_member(result[2])
					elif (result[3] == 2 and winning_image == 'A') or (result [3] == 1 and winning_image == 'B'):
						winner = base_channel.guild.get_member(result[2])
						winning_image_url = result[5]
						loser = base_channel.guild.get_member(result[1])
					elif winning_image == 'tie':
						# build tie embed for match channel
						embed_title = 'Voting Results'
						embed_description = 'This match has ended in a ' + str(a_votes) + ' - ' + str(b_votes) + ' tie! Participants, please contact each other and find a time to rematch.'
						embed = await generate_embed('pink', embed_title, embed_description)
						await base_channel.send(embed=embed)
						await action_log('match ended in a tie, results sent in match channel')

						if not config.TESTING:
							# update participant stats in the databsee (tie)
							query = 'UPDATE participants SET total_votes_for = total_votes_for + ' + votes + ' WHERE user_id = ' + str(result[1])
							connect.crsr.execute(query)
							connect.conn.commit()
							query = 'UPDATE participants SET total_votes_for = total_votes_for + ' + votes + ' WHERE user_id = ' + str(result[2])
							connect.crsr.execute(query)
							connect.conn.commit()
							await action_log('participant stats updated')
						return
					else:
						await action_log('winner not found or a_meme not defined in postgresql')
						return
				except AttributeError:
					await action_log('member from existing match was not found in the guild')
					return

				if not config.TESTING:
					# update winner's round role
					i = 0
					while i <= (len(config.ROUND_ROLE_IDS) - 1):
						round_role = message.guild.get_role(config.ROUND_ROLE_IDS[i])
						if round_role in winner.roles:
							# remove previous round role
							await winner.remove_roles(round_role)
							# check to see if winner is a finalist
							if round_role.id == 634853736144961580:
								# add winning role
								await winner.add_roles(message.guild.get_role(config.WINNER_ROLE_ID))
							else:
								# add next round role
								await winner.add_roles(message.guild.get_role(config.ROUND_ROLE_IDS[i + 1]))
							i = len(config.ROUND_ROLE_IDS)
						i += 1
					await action_log('winner round role updated')

					# update participant stats in the database
					query = 'UPDATE participants SET total_matches = total_matches + 1, match_wins = match_wins + 1, total_votes_for = total_votes_for + ' + str(winning_votes) + ' WHERE user_id = ' + str(winner.id)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('winner participant stats updated')
					query = 'UPDATE participants SET total_matches = total_matches + 1, match_losses = match_losses + 1, total_votes_for = total_votes_for + ' + str(losing_votes) + ' WHERE user_id = ' + str(loser.id)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('loser participant stats updated')

				# build notification embed for match channel (win/loss)
				embed_title = 'Voting Results'
				embed_description = 'Congratulations to ' + winner.mention + ', you have won this match with image ' + winning_image + '! Thank you for participating ' + loser.mention + '. The final score was ' + str(a_votes) + ' - ' + str(b_votes) + '.'
				embed = await generate_embed('pink', embed_title, embed_description)
				await base_channel.send(embed=embed)
				await action_log('voting results sent in match channel')

				# build winning image embed for match archive
				embed_title = winner.display_name
				embed_description = datetime.date.today().strftime("%B %d")
				embed_link = winning_image_url
				embed = await generate_embed('pink', embed_title, embed_description, embed_link)
				await client.get_channel(config.ARCHIVE_CHAN_ID).send(embed=embed)
				await action_log('winning image sent to archive channel')
				return
			if message.channel.id == config.TEMPLATE_CHAN_ID and message.nonce == 'template':
				# add reactions to messages in the #templates channel
				await message.add_reaction('👍')
				await message.add_reaction('🤷')
				await message.add_reaction('👎')

				# update signup info with the message_id
				query = 'UPDATE signups SET message_id = ' + str(message.id) + ' WHERE message_id = 0'
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('message_id added to postgresql signup info')
				return
			if message.channel.id == config.TEMPLATE_CHAN_ID and message.nonce == 'voluntary_template':
				# add reactions to messages in the #templates channel
				await message.add_reaction('👍')
				await message.add_reaction('🤷')
				await message.add_reaction('👎')
				return
			if message.channel.id == config.DUELMODS_CHAN_ID and message.nonce is not None:
				if message.nonce.startswith('tempcon'):
					# add reactions to normal template confirmations in #duel-mods
					await message.add_reaction('<:check_mark:637394596472815636>')
					await message.add_reaction('<:x_mark:637394622200676396>')
					return
			if message.channel.id == config.DUELMODS_CHAN_ID and message.nonce is not None:
				if message.nonce.startswith('sptemp'):
					# add reactions to split template confirmations in #duel-mods
					await message.add_reaction('<:check_mark:637394596472815636>')
					await message.add_reaction('<:x_mark:637394622200676396>')
					return
			return
		return

	# process and clean message content
	message_content = unidecode(message.content.casefold().strip())

	# '.donate' command (all channels)
	if message_content == '.donate':
		# build donation embed
		embed_title = 'Donate to MadnessMod'
		embed_description = 'If you\'d like to donate to MadnessMod, please go to https://www.paypal.me/lukenamop\n\n100% of MadnessMod donations will go towards bot upkeep ($8 a month) and other Meme Madness fees.'
		embed = await generate_embed('pink', embed_title, embed_description)
		await message.channel.send(embed=embed)
		await action_log('donation info sent to ' + message.author.name + '#' + message.author.discriminator)
		return

	# '.stats' command (all channels)
	if message_content.startswith('.stats'):
		# check for a mentioned user
		if len(message.mentions) == 1:
			user = message.mentions[0]
		else:
			user = message.author

		# check participants database for the specified user
		query = 'SELECT total_matches, match_wins, match_losses, total_votes_for, avg_final_meme_time, templates_submitted, match_votes FROM participants WHERE user_id = ' + str(user.id)
		connect.crsr.execute(query)
		results = connect.crsr.fetchone()
		if results is not None:
			if results[4] is not None:
				avg_time = strftime("%Mm %Ss", gmtime(results[4]))
			else:
				avg_time = 'N/A'

			# build stats embed
			embed_title = 'Stats for ' + user.display_name
			try:
				embed_description = '**Total matches:** `' + str(results[0]) + '`\n**Match wins/losses:** `' + str(results[1]) + '/' + str(results[2]) + '`\n**Win percentage:** `' + str(round((float(results[1]) / float(results[0])) * 100)) + '%`\n**Total votes for your memes:** `' + str(results[3]) + '`\n**Avg. time per meme:** `' + avg_time + '`\n**Templates submitted:** `' + str(results[5]) + '`\n**Matches voted in:** `' + str(results[6]) + '`'
			except ZeroDivisionError:
				embed_description = '**Total matches:** `' + str(results[0]) + '`\n**Match wins/losses:** `' + str(results[1]) + '/' + str(results[2]) + '`\n**Win percentage:** `N/A`\n**Total votes for your memes:** `' + str(results[3]) + '`\n**Avg. time per meme:** `' + avg_time + '`\n**Templates submitted:** `' + str(results[5]) + '`\n**Matches voted in:** `' + str(results[6]) + '`'
			embed = await generate_embed('pink', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('stats shared to ' + message.author.name + '#' + message.author.discriminator)
			return

		# if no record of specified user, build no-stats embed
		embed_title = 'No Stats Available'
		embed_description = user.display_name + ' needs to sign up for a tournament to start recording stats.'
		embed = await generate_embed('red', embed_title, embed_description)
		await message.channel.send(embed=embed)
		await action_log('stats not able to be shared')
		return

	# verification specific commands
	if message.channel.id == 581705191703838720 or message.channel.id == 607344923481473054:
		# '.verify' command (verification)
		if message_content.startswith('.verify'):
			verified = False
			username_discriminator = message.author.name + '#' + message.author.discriminator
			# check manually which guild the user is verifying to; get "Verified" role from guild
			if message.guild.id == 581695290986332160:
				verification_role = message.guild.get_role(599354132771504128)
			elif message.guild.id == 607342998497525808:
				verification_role = message.guild.get_role(607349686554329094)
			else:
				return

			# save base info for duration of the verification process
			base_member = message.author
			base_message = message

			# build verification begin embed
			embed_title = 'Verification Process Started'
			embed_description = base_member.mention + ', please check your Discord messages for the next steps!'
			embed = await generate_embed('yellow', embed_title, embed_description)
			base_bot_response = await message.channel.send(embed=embed)
			await action_log('verification started by ' + username_discriminator)

			# build verification step 1/2 embed
			user_channel = await base_member.create_dm()
			embed_title = 'Verification Attempt (Step 1/2)'
			embed_description = 'Please send the name of your reddit account here:'
			embed = await generate_embed('yellow', embed_title, embed_description)
			await user_channel.send(embed=embed)

			# asyncio.TimeoutError triggers if client.wait_for(message) times out
			try:
				# define message requirements (DM message from specified user)
				def check(m):
					return m.channel == user_channel and m.author.id == base_member.id
				# wait for a message
				message = await client.wait_for('message', check=check, timeout=120)
				reddit_username = message.content.split('/')[-1].lstrip('@')
				await action_log('verification username shared by ' + username_discriminator)

				# generate random 6 character string excluding unwanted_chars
				unwanted_chars = ["0", "O", "l", "I"]
				char_choices = [char for char in string.ascii_letters if char not in unwanted_chars] + [char for char in string.digits if char not in unwanted_chars]
				verification_string = ''.join(random.choices(char_choices, k=6))

				# check to see which server is hosting the verification and set unique message
				if base_message.guild.id == 607342998497525808:
					# send message via reddit
					reddit_username = verify.send_message(reddit_username, verification_string, username_discriminator, mex=True)
				else:
					# send message via reddit
					reddit_username = verify.send_message(reddit_username, verification_string, username_discriminator)

				# verify that a username was shared
				if reddit_username is not None:
					await action_log('verification reddit message for ' + username_discriminator + ' sent to \'' + reddit_username + '\'')

					# build verification step 2/2 embed
					embed_title = 'Verification Attempt (Step 2/2)'
					embed_description = 'Check your reddit account for a message that I\'ve just sent. To complete verification, send your 6 character verification key here (case sensitive, type carefully):'
					embed = await generate_embed('yellow', embed_title, embed_description)
					await user_channel.send(embed=embed)

					# define message requirements (DM message from specified user)
					def check(m):
						return m.channel == user_channel and m.author.id == base_member.id
					# wait for a message
					message = await client.wait_for('message', check=check, timeout=120)

					# check that message includes specified verification_string
					if message.content == verification_string:
						# discord.errors.Forbidden triggers if discord bot client does not have permission to set nicknames or assign roles
						try:
							# build verification confirmation embed
							embed_title = 'Verification Complete'
							embed_description = 'Your account has been verified! Enjoy the server.'
							embed = await generate_embed('green', embed_title, embed_description)

							# set user nickname and roles
							await base_member.edit(nick=reddit_username)
							await base_member.add_roles(verification_role)
							if base_message.guild.id == 607342998497525808:
								del_role = base_message.guild.get_role(607365580567216130)
								await base_member.remove_roles(del_role)
							verified = True

						except discord.errors.Forbidden:
							# build access error embed
							embed_title = 'Access Error'
							embed_description = 'For some reason I don\'t have permission to assign roles. Please contact lukenamop#0918.'
							embed = await generate_embed('red', embed_title, embed_description)

						# DM embed to user
						await user_channel.send(embed=embed)

						# send a message to the #general channel welcoming the new user
						embed_title = 'New User Has Joined: ' + base_member.display_name

						# check which server is hosting the verification
						if base_message.guild.id == 607342998497525808:
							# build welcome embed
							embed_description = base_member.mention + ', welcome to MEX! Please let a member of the mod team know if you need any help.'
							embed = await generate_embed('green', embed_title, embed_description)
							await client.get_channel(607342999751491585).send(embed=embed)
						elif base_message.guild.id == 581695290986332160:
							# build welcome embed
							embed_description = base_member.mention + ', welcome to Meme Madness! Check out #info and #rules to see how this place is run and let a member of the mod team know if you need any help.'
							embed = await generate_embed('green', embed_title, embed_description)
							await client.get_channel(581695290986332162).send(embed=embed)
						# send welcome embed
						await action_log('verification compeleted by ' + username_discriminator)
					else:
						# build verification failure embed (verification key error)
						embed_title = 'Verification Key Incorrect'
						embed_description = 'To try again, please send `.verify` in #verification.'
						embed = await generate_embed('red', embed_title, embed_description)
						await user_channel.send(embed=embed)
						await action_log('verification key incorrect from ' + username_discriminator)
				else:
					await action_log('verification username error for ' + username_discriminator + ', attempted name: ' + message.content.split('/')[-1])
					# build verification failure embed (username error)
					embed_title = 'Username Error'
					embed_description = 'To try again, please send `.verify` in #verification.'
					embed = await generate_embed('red', embed_title, embed_description)
					await user_channel.send(embed=embed)
			except asyncio.TimeoutError:
				# build verification failure embed (timed out)
				embed_title = 'Verification Attempt Timed Out'
				embed_description = 'To try again, please send `.verify` in #verification.'
				embed = await generate_embed('red', embed_title, embed_description)
				await user_channel.send(embed=embed)
				await action_log('verification timed out for ' + username_discriminator)

			# discord.errors.NotFound triggers if messages set for deletion don't exist
			try:
				# remove verification messages from server
				await base_message.delete()
				await base_bot_response.delete()
			except discord.errors.NotFound:
				await action_log('verification messages already deleted')

			# send Meme Madness suggestion to newly verified users
			if base_message.guild.id == 607342998497525808 and verified:
				# sleep for 3 minutes
				await asyncio.sleep(180)

				# build suggestion embed
				embed_title = 'Other Servers You May Like'
				embed_description = 'Meme Madness (the server I was originally created for) hosts a free-to-enter meme creation tournament. Any aspiring meme-makers are welcome! There\'s a sponsor that even contributes a $40 prize pool to each tournament. Check it out at https://discord.gg/vV4uvQW'
				embed = await generate_embed('pink', embed_title, embed_description)
				await user_channel.send(embed=embed)
				await action_log('meme madness suggestion sent to verified user')
			return
		return

	# DM specific commands
	if isinstance(message.channel, discord.DMChannel):
		# '.signup' command (DM)
		if message_content.startswith('.signup'):
			# get member from Meme Madness server
			member = client.get_guild(config.MM_GUILD_ID).get_member(message.author.id)
			# verify member exists
			if member is None:
				return

			# check tournament settings via database (template requirement)
			query = 'SELECT template_required FROM settings WHERE guild_id = ' + str(config.MM_GUILD_ID)
			connect.crsr.execute(query)
			results = connect.crsr.fetchone()
			template_required = results[0]

			# check to see if templates are required for signups
			if template_required:
				# signup process when a template is required
				# check message for an attachment
				if len(message.attachments) != 1:
					# build signup embed
					embed_title = 'Signup Started'
					embed_description = 'Please send me a blank template to confirm your signup! This signup attempt will expire in 120 seconds.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('signup attempted without attachment by ' + message.author.name + '#' + message.author.discriminator)

					# asyncio.TimeoutError triggers if client.wait_for(message) times out
					try:
						# define message requirements (DM message from specified user)
						def check(m):
							return m.channel.type == message.channel.type and m.author.id == message.author.id and len(m.attachments) == 1
						# wait for a message
						message = await client.wait_for('message', check=check, timeout=120)
						await action_log('signup attachment received from ' + message.author.name + '#' + message.author.discriminator)
					except asyncio.TimeoutError:
						# build signup error embed (timed out)
						embed_title = 'Signup Timed Out'
						embed_description = 'If you\'d like to signup for this week\'s competition, send me another message with `.signup`!'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('signup timed out by ' + message.author.name + '#' + message.author.discriminator)
						return
				else:
					await action_log('signup attachment received from ' + message.author.name + '#' + message.author.discriminator)

					# check to see if user has signed up in the last 7 days (config.CYCLE seconds)
					query = 'SELECT * FROM signups WHERE user_id = ' + str(message.author.id) + ' AND submission_time >= ' + str(time.time() - config.CYCLE)
					connect.crsr.execute(query)
					result = connect.crsr.fetchone()
					# don't create a new signup for previously signed up users
					if result is None:
						# build confirmation embed
						embed_title = 'Template Confirmation'
						embed_description = 'Thank you for submitting your template ' + message.author.mention + '! If there are any issues with your entry you will be contacted.'
						embed = await generate_embed('green', embed_title, embed_description)
						await message.channel.send(embed=embed)

						# send template to #templates
						embed_title = 'Template Submission'
						embed_description = member.mention + ' (' + functions.escape_underscores(member.display_name) + ', ' + str(member.id) + ')'
						embed_link = message.attachments[0].url
						embed = await generate_embed('green', embed_title, embed_description, embed_link)
						template_chan = client.get_channel(config.TEMPLATE_CHAN_ID)
						template_message = await template_chan.send(embed=embed, nonce='template')
						await action_log('signup attachment sent to #templates by ' + message.author.name + '#' + message.author.discriminator)

						# add signup info to postgresql
						query = 'INSERT INTO signups (user_id, message_id, submission_time) VALUES (' + str(message.author.id) + ', 0, ' + str(time.time()) + ')'
						connect.crsr.execute(query)
						connect.conn.commit()
						await action_log('signup info added to postgresql')
					else:
						# build signup error embed (already signed up)
						embed_title = 'Error: Already Signed Up'
						embed_description = 'It looks like you\'ve already signed up for this cycle of Meme Madness! Contact a moderator if this is incorrect.'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('already signed up from ' + message.author.name + '#' + message.author.discriminator)
						return
			else:
				# signup process when no template is required
				# check to see if user has signed up in the last 7 days (config.CYCLE seconds)
				query = 'SELECT * FROM signups WHERE user_id = ' + str(message.author.id) + ' AND submission_time >= ' + str(time.time() - config.CYCLE)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				# don't create a new signup for previously signed up users
				if result is None:
					embed_title = 'Signup Confirmation'
					embed_description = 'Thank you for signing up ' + message.author.mention + '! If there are any issues with your entry you will be contacted.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)

					# send signup to #templates
					embed_title = 'Signup Confirmed'
					embed_description = member.mention + ' (' + functions.escape_underscores(member.display_name) + ', ' + str(member.id) + ')'
					embed = await generate_embed('green', embed_title, embed_description)
					template_chan = client.get_channel(config.SIGNUP_CHAN_ID)
					template_message = await template_chan.send(embed=embed)
					await action_log('signup sent to #templates by ' + message.author.name + '#' + message.author.discriminator)

					# add signup info to postgresql
					query = 'INSERT INTO signups (user_id, message_id, submission_time) VALUES (' + str(message.author.id) + ', 0, ' + str(time.time()) + ')'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('signup info added to postgresql')
				else:
					# build signup error embed (already signed up)
					embed_title = 'Error: Already Signed Up'
					embed_description = 'It looks like you\'ve already signed up for this cycle of Meme Madness! Contact a moderator if this is incorrect.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('already signed up from ' + message.author.name + '#' + message.author.discriminator)
					return

			# check for existing participant in database
			query = 'SELECT * FROM participants WHERE user_id = ' + str(message.author.id)
			connect.crsr.execute(query)
			if connect.crsr.fetchone() is None:
				# create participant if none exists
				query = 'INSERT INTO participants (user_id) VALUES (' + str(message.author.id) + ')'
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('user added to participants table in postgresql')
			return

		# '.submit' command (DM)
		if message_content.startswith('.submit'):
			# check for an active match including the specified user
			query = 'SELECT u1_id, u2_id, u1_submitted, u2_submitted, channel_id, start_time, split_match_template_url FROM matches WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
			connect.crsr.execute(query)
			result = connect.crsr.fetchone()

			# build duplicate submission embed
			embed_title = 'Error: Already Submitted'
			embed_description = 'It looks like you\'ve already submitted for your current match! If this is incorrect, contact a moderator.'
			embed = await generate_embed('red', embed_title, embed_description)

			# check for duplicate submissions
			if result is not None:
				start_time = result[5]
				split_match_template_url = result[6]
				match_channel = client.get_channel(result[4])
				if message.author.id == result[0]:
					if result[2]:
						await message.channel.send(embed=embed)
						await action_log('duplicate submission by ' + message.author.name + '#' + message.author.discriminator)
						return
					u_order = 1
				elif message.author.id == result[1]:
					if result[3]:
						await message.channel.send(embed=embed)
						await action_log('duplicate submission by ' + message.author.name + '#' + message.author.discriminator)
						return
					u_order = 2
				# check for an attachment
				if len(message.attachments) != 1:
					# build submission embed
					embed_title = 'Submission Started'
					embed_description = 'Please send me your final meme to confirm your submission! This submission attempt will expire in 120 seconds.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('submission attempted without attachment by ' + message.author.name + '#' + message.author.discriminator)

					# asyncio.TimeoutError triggers if client.wait_for(message) times out
					try:
						# define message requirements (DM message from specified user)
						def check(m):
							return m.channel.type == message.channel.type and m.author.id == message.author.id and len(m.attachments) == 1
						# wait for a message
						message = await client.wait_for('message', check=check, timeout=120)
						await action_log('submission attachment received from ' + message.author.name + '#' + message.author.discriminator)
					except asyncio.TimeoutError:
						# build submission error embed (timed out)
						embed_title = 'Submission Timed Out'
						embed_description = 'If you\'d like to submit your final meme, send me another message with `.submit`!'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('submission timed out by ' + message.author.name + '#' + message.author.discriminator)
						return
				else:
					await action_log('submission attachment received from ' + message.author.name + '#' + message.author.discriminator)

				# build submission confirmation embed
				embed_title = 'Submission Confirmation'
				embed_description = 'Thank you for submitting your final meme ' + message.author.mention + '! If there are any issues with your submission you will be contacted.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('final meme attachment sent in by ' + message.author.name + '#' + message.author.discriminator)

				if split_match_template_url is not None:
					# build submission confirmation for match channel
					embed_title = 'Solo Match Complete'
					embed_description = message.author.mention + ' has completed their part of the match!'
					embed = await generate_embed('green', embed_title, embed_description)
					await match_channel.send(embed=embed)
					await action_log('match channel notified about splitmatch completion')

				# add submission info to postgresql database
				if u_order == 1:
					query = 'UPDATE matches SET u1_submitted = true, u1_image_url = \'' + message.attachments[0].url + '\' WHERE u1_id = ' + str(message.author.id) + ' AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('match info updated in postgresql')
				if u_order == 2:
					query = 'UPDATE matches SET u2_submitted = true, u2_image_url = \'' + message.attachments[0].url + '\' WHERE u2_id = ' + str(message.author.id) + ' AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('match info updated in postgresql')

				if not config.TESTING:
					# pull participant info from database
					query = 'SELECT avg_final_meme_time, total_matches FROM participants WHERE user_id = ' + str(message.author.id)
					connect.crsr.execute(query)
					results = connect.crsr.fetchone()
					# check to see if avg_final_meme_time exists
					if results[0] is None:
						new_avg_final_meme_time = time.time() - float(start_time)
					else:
						new_avg_final_meme_time = ((float(results[0] * results[1]) + (time.time() - float(start_time))) / float(results[1] + 1))
					# update participant stats in database
					query = 'UPDATE participants SET avg_final_meme_time = ' + str(new_avg_final_meme_time) + ' WHERE user_id = ' + str(message.author.id)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('participant stats updated')

				# pull match info from database
				query = 'SELECT u1_id, u2_id, u1_submitted, u2_submitted, u1_image_url, u2_image_url, channel_id FROM matches WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				# find match_channel and submissions_channel from discord
				match_channel = client.get_channel(result[6])
				submissions_channel = client.get_channel(config.SUBMISSION_CHAN_ID)
				# only execute if both users have submitted final memes
				if result[2] and result[3]:
					if u_order == 1:
						try:
							# set user order
							u1 = match_channel.guild.get_member(result[0])
							u1_mention = u1.mention
							u1_link = result[4]
							u2 = match_channel.guild.get_member(result[1])
							u2_mention = u2.mention
							u2_link = result[5]
						except AttributeError:
							await action_log('final meme submission stopped due to an AttributeError')
							return
						# update match info in database
						query = 'UPDATE matches SET a_meme = 1 WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
						connect.crsr.execute(query)
						connect.conn.commit()
					if u_order == 2:
						try:
							# ser user order
							u1 = match_channel.guild.get_member(result[1])
							u1_mention = u1.mention
							u1_link = result[5]
							u2 = match_channel.guild.get_member(result[0])
							u2_mention = u2.mention
							u2_link = result[4]
						except AttributeError:
							await action_log('final meme submission stopped due to an AttributeError')
							return
						# update match info in database
						query = 'UPDATE matches SET a_meme = 2 WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
						connect.crsr.execute(query)
						connect.conn.commit()

					# send final memes to #submissions channel
					# submission embed for user 1
					embed_title = 'Final Meme Submission'
					embed_description = u1_mention + ' (' + u1.display_name + ', ' + str(result[0]) + ')'
					embed_link = u1_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await submissions_channel.send(embed=embed)
					# submission embed for user 2
					embed_description = u2_mention + ' (' + u2.display_name + ', ' + str(result[1]) + ')'
					embed_link = u2_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await submissions_channel.send(embed=embed)
					await action_log('final memes sent to #submissions')

					# send final memes to match channel
					# submission embed for image A
					embed_description = 'Image A'
					embed_link = u1_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await match_channel.send(embed=embed)
					# submission embed for image B
					embed_description = 'Image B'
					embed_link = u2_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await match_channel.send(embed=embed)

					# build voting embed
					embed_title = 'Match Voting'
					embed_description = '**Vote for your favorite!** Results will be sent to this channel when voting ends in 2 hours.\n🇦 First image\n🇧 Second image'
					embed = await generate_embed('pink', embed_title, embed_description)
					await match_channel.send(embed=embed, nonce='poll')
				return
			else:
				# build submission error embed (no active match)
				embed_title = 'No Active Match'
				embed_description = 'You don\'t appear to have an active match to submit to right now.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('submission attempt without match by ' + message.author.name + '#' + message.author.discriminator)
				return

		# '.template' command (DM)
		if message_content.startswith('.template'):
			# assign base member
			member = client.get_guild(config.MM_GUILD_ID).get_member(message.author.id)

			# check for an attachment
			if len(message.attachments) != 1:
				# build template embed
				embed_title = 'Template Submission Started'
				embed_description = 'If you\'d like to help out by providing a template, please send me a blank image. This template submission attempt will expire in 120 seconds.'
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('template attempted without attachment by ' + message.author.name + '#' + message.author.discriminator)

				# asyncio.TimeoutError triggers if client.wait_for(message) times out
				try:
					# define message requirements (DM message from specified user)
					def check(m):
						return m.channel.type == message.channel.type and m.author.id == message.author.id and len(m.attachments) == 1
					# wait for a message
					message = await client.wait_for('message', check=check, timeout=120)
				except asyncio.TimeoutError:
					# build template error embed (timed out)
					embed_title = 'Template Submission Timed Out'
					embed_description = 'If you\'d like to submit a template to be used in Meme Madness, send me another message with `.template`!'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('template submission timed out by ' + message.author.name + '#' + message.author.discriminator)
					return

			await action_log('template attachment received from ' + message.author.name + '#' + message.author.discriminator)
			# build confirmation embed
			embed_title = 'Template Confirmation'
			embed_description = 'Thank you for submitting your template ' + message.author.mention + '! If there are any issues, you will be contacted.'
			embed = await generate_embed('green', embed_title, embed_description)
			await message.channel.send(embed=embed)

			# send template to #templates
			embed_title = 'Voluntary Template Submission'
			embed_description = member.mention + ' (' + functions.escape_underscores(member.display_name) + ', ' + str(member.id) + ')'
			embed_link = message.attachments[0].url
			embed = await generate_embed('green', embed_title, embed_description, embed_link)
			template_chan = client.get_channel(config.TEMPLATE_CHAN_ID)
			template_message = await template_chan.send(embed=embed, nonce='voluntary_template')
			await action_log('template attachment sent to #templates by ' + message.author.name + '#' + message.author.discriminator)

			if not config.TESTING:
				# check for existing participant in database
				query = 'SELECT templates_submitted FROM participants WHERE user_id = ' + str(message.author.id)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result is None:
					# create participant if none exists
					query = 'INSERT INTO participants (user_id, templates_submitted) VALUES (' + str(message.author.id) + ', 1)'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('no existing user, new user added to participants table in postgresql')
				else:
					# update participant stats if they already exist
					query = 'UPDATE participants SET templates_submitted = ' + str(result[0] + 1) + ' WHERE user_id = ' + str(message.author.id)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('user already existed, participant stats updated in postgresql')
			return

		# '.help' command (DM)
		if message_content.startswith('.help'):
			# build help embed
			embed_title = 'Commands'
			embed_description = help_cmd.dm_help
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('help query sent to ' + message.author.name + '#' + message.author.discriminator)
			return
		return

	# stats-flex specific commands
	if message.channel.id == 631239602736201728:
		# '.help' command (stats-flex)
		if message_content.startswith('.help'):
			# build help embed
			embed_title = 'Commands'
			embed_description = help_cmd.stats_help
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('help query sent to ' + message.author.name + '#' + message.author.discriminator + ' in stats-flex')
			return
		return


	# duel-mods specific commands
	if message.channel.id == 600397545050734612 or message.channel.id == 581728812518080522:
		# '.activematches' command (duel-mods)
		if message_content == '.activematches':
			query = 'SELECT channel_id FROM matches WHERE start_time >= ' + str(time.time() - (config.MATCH_TIME + config.BASE_POLL_TIME))
			connect.crsr.execute(query)
			results = connect.crsr.fetchall()
			embed_title = 'Active Matches'
			# check to make sure there are active matches
			if results is not None:
				# build activematches embed
				embed_description = ''
				total = 0
				for match in results:
					channel = client.get_channel(match[0])
					if channel is not None:
						embed_description += channel.mention + '\n'
						total += 1
				embed_description += '**Total active matches: `' + str(total) + '`**'
			else:
				embed_description = '**Total active matches: `0`**'
			embed = await generate_embed('green', embed_title, embed_description)
			# send activematches embed
			await message.channel.send(embed=embed)
			await action_log('activematches sent to duel-mods')
			return

		# '.reconnect' command (duel-mods)
		if message_content == '.reconnect':
			await action_log('attempting to reconnect to database...')
			success = connect.db_connect()
			if success:
				embed_title = 'Connection Established'
				embed_description = 'The database has been reconnected.'
				embed = await generate_embed('green', embed_title, embed_description)
			else:
				embed_title = 'Connection Attempt Failed'
				embed_description = 'Something went wrong! Please contact lukenamop ASAP.'
				embed = await generate_embed('red', embed_title, embed_description)
			await message.channel.send(embed=embed)
			return

		# '.resignup' command (duel-mods)
		if message_content.startswith('.resignup '):
			await action_log('resignup command in #duel-mods')
			# IndexError triggers if no reason is included in command
			# ValueError triggers if a string is used instead of a number
			try:
				# split message apart and save variables
				message_split = message_content.split(' ', 2)
				user_id = int(message_split[1])
				reason = message_split[2]

				# check signups database for specified user_id
				query = 'SELECT message_id FROM signups WHERE user_id = ' + str(user_id) + ' AND submission_time >= ' + str(time.time() - config.CYCLE)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result is not None:
					# DM user to notify of resignup
					user_channel = client.get_user(user_id).dm_channel
					if user_channel is None:
						user_channel = await client.get_user(user_id).create_dm()

					# build resignup embed
					embed_title = 'Re-signup Required'
					embed_description = 'Your signup was removed for reason: `' + reason + '`. To enter this cycle of Meme Madness please `.signup` with a new template. If you have any questions please contact the moderators. Thank you!'
					embed = await generate_embed('red', embed_title, embed_description)
					await user_channel.send(embed=embed)
					await action_log('DM sent to user')

					# remove template/signup message from the #signups or #templates channel
					message_id = result[0]
					# error triggers if template/signup message does not exist
					try:
						msg = await client.get_channel(config.TEMPLATE_CHAN_ID).fetch_message(message_id)
						print(msg.content)
						await msg.delete()
						await action_log('submission message deleted')
					except:
						await action_log('no submission message to delete')

					# remove signup info from postgresql
					query = 'DELETE FROM signups WHERE user_id = ' + str(user_id) + ' AND submission_time >= ' + str(time.time() - config.CYCLE)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('signup info deleted')

					# build resignup confirmation embed
					embed_title = 'Signup Deleted'
					embed_description = message.guild.get_member(user_id).mention + '\'s signup has been deleted. I have sent them a DM including your reason for removing their signup and told them to `.signup` again if they\'d like to participate.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					return
				else:
					# build resignup error embed (no matching signup)
					embed_title = 'Error: No Matching Signup'
					embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `622139031756734492`).'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('no matching submission error with resignup')
					return
			except IndexError:
				# build resignup error embed (no reason given)
				embed_title = 'Error: No Reason Given'
				embed_description = 'Please include a reason for removing the specified signup! The format is `.resignup <user ID> <reason>`.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('no reason given for resignup')
				return
			except ValueError:
				# build resignup error embed (no matching signup)
				embed_title = 'Error: No Matching Signup'
				embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `622139031756734492`).'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('non-int passed to resignup')
				return

		# '.signuplist' command (duel-mods)
		if message_content.startswith('.signuplist') or message_content.startswith('.signups'):
			# pull all signups from database
			query = 'SELECT user_id FROM signups WHERE submission_time >= ' + str(time.time() - config.CYCLE)
			connect.crsr.execute(query)
			results = connect.crsr.fetchall()
			embed_title = 'Signup List'
			# check to make sure there are signups
			if results is not None:
				# build signuplist embed
				embed_description = ''
				total = 0
				for entry in results:
					member = message.guild.get_member(entry[0])
					if member is not None:
						embed_description += functions.escape_underscores(member.display_name) + '\n'
						total += 1
				embed_description += '**Total signups: `' + str(total) + '`**'
			else:
				embed_description = 'There aren\'t any signups for this cycle in the database yet.'
			embed = await generate_embed('green', embed_title, embed_description)
			# send signuplist embed
			await message.channel.send(embed=embed)
			await action_log('signuplist sent to duel-mods')
			return

		# '.settournamentroles' command (duel-mods)
		if message_content == '.settournamentroles':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# build processing embed
				embed_title = 'Processing...'
				embed_description = 'Setting tournament roles... This could take a few minutes...'
				embed = await generate_embed('yellow', embed_title, embed_description)
				processing_message = await message.channel.send(embed=embed)

				total_removed = 0
				# iterate through all members
				for member in message.guild.members:
					for role in member.roles:
						if role.id in config.ROUND_ROLE_IDS:
							# remove round roles
							await member.remove_roles(role)
							# count up
							total_removed += 1
				await action_log(str(total_removed) + ' roles removed')

				# pull all signups from database
				query = 'SELECT user_id FROM signups WHERE submission_time >= ' + str(time.time() - config.CYCLE)
				connect.crsr.execute(query)
				results = connect.crsr.fetchall()
				# check to make sure there are signups
				if results is not None:
					total_added = 0
					# assign every user to the Round 1 role
					for entry in results:
						member = message.guild.get_member(entry[0])
						if member is not None:
							await member.add_roles(message.guild.get_role(config.ROUND_ROLE_IDS[1]))
							# count up
							total_added += 1
					await processing_message.delete()
					embed_title = 'Tournament Roles Set'
					embed_description = 'Success! ' + str(total_removed) + ' previous tournament roles removed, ' + str(total_added) + ' new tournament roles added.'
					embed = await generate_embed('green', embed_title, embed_description)
					await action_log(str(total_added) + ' roles added')
				else:
					embed_title = 'Start Error'
					embed_description = 'There aren\'t any signups for this cycle in the database yet.'
					embed = await generate_embed('red', embed_title, embed_description)
					await action_log('start error')
				# send signuplist embed
				await message.channel.send(embed=embed)
				await action_log('settournamentroles complete')
				return
			return

		# '.removetournamentroles' command (duel-mods)
		if message_content == '.removetournamentroles':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# build processing embed
				embed_title = 'Processing...'
				embed_description = 'Removing tournament roles... This could take a few minutes...'
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)

				total_removed = 0;
				# iterate through all members
				for member in message.guild.members:
					for role in member.roles:
						if role.id in config.ROUND_ROLE_IDS:
							# remove round roles
							await member.remove_roles(role)
							# count up
							total_removed += 1
				embed_title = 'Tournament Roles Removed'
				embed_description = 'Success! ' + str(total_removed) + ' previous tournament roles removed.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log(str(total_removed) + ' roles removed')
				await action_log('removetournamentroles complete')
				return
			return

		# '.prelim' command (duel-mods)
		if message_content.startswith('.prelim '):
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				await action_log('prelim command in #duel-mods')
				# ValueError triggers if a string is used instead of a number
				try:
					# split message apart and find user from ID
					message_split = message_content.split(' ', 1)
					user_id = int(message_split[1])
					member = client.get_guild(config.MM_GUILD_ID).get_member(user_id)

					passed = False
					if member is not None:
						for role in member.roles:
							if role.id == config.ROUND_ROLE_IDS[1]:
								# remove round 1 role
								await member.remove_roles(role)
								# add prelim role
								await member.add_roles(message.guild.get_role(config.ROUND_ROLE_IDS[0]))
								passed = True
						if passed:
							# build prelim success embed
							embed_title = 'Role Set to Prelim'
							embed_description = 'The tournament role for ' + member.mention + ' has been set to `Preliminary`.'
							embed = await generate_embed('green', embed_title, embed_description)
							await message.channel.send(embed=embed)
							await action_log('prelim set for ' + member.name + '#' + member.discriminator)
						else:
							# build prelim error embed (user did not have tournament role)
							embed_title = 'Error: Specified User Not Valid'
							embed_description = 'The specified user did not have a `Round 1` role.'
							embed = await generate_embed('red', embed_title, embed_description)
							await message.channel.send(embed=embed)
							await action_log('user not valid')
						return
					else:
						# build prelim error embed (no matching signup)
						embed_title = 'Error: No Matching Signup'
						embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `622139031756734492`).'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('no matching submission error with prelim')
						return
				except ValueError:
					# build prelim error embed (no matching signup)
					embed_title = 'Error: No Matching Signup'
					embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `622139031756734492`).'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('non-int passed to prelim')
					return
			return

		# '.toggletemplates' command (duel-mods)
		if message_content == '.toggletemplates':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				await action_log('signup templates toggled')
				# check to see if templates are required
				query = 'SELECT template_required FROM settings WHERE guild_id = ' + str(config.MM_GUILD_ID)
				connect.crsr.execute(query)
				results = connect.crsr.fetchone()
				template_required = results[0]
				if template_required:
					# set templates to no longer be required
					query = 'UPDATE settings SET template_required = False WHERE guild_id = ' + str(config.MM_GUILD_ID)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('templates no longer required')

					# build toggletemplates confirmation embed
					embed_title = 'Templates Disabled'
					embed_description = 'Templates are no longer required with `.signup`'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('template toggle confirmation')
					return
				else:
					# set templates to now be required
					query = 'UPDATE settings SET template_required = True WHERE guild_id = ' + str(config.MM_GUILD_ID)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('templates now required')

					# build toggletemplates confirmation embed
					embed_title = 'Templates Enabled'
					embed_description = 'Templates are now required with `.signup`'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('template toggle confirmation')
					return

		# '.createbracket' command (duel-mods)
		if message_content.startswith('.createbracket '):
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# initialize some important variables
				bracket_number = message_content.split()[1]
				tournament_title = 'Meme Madness ' + bracket_number
				tournament_shortcut = 'mmcycle' + bracket_number

				# send a confirmation embed
				embed_title = 'Creating Bracket...'
				embed_description = 'Creating a Challonge bracket called **' + tournament_title + '**.'
				embed = await generate_embed('yellow', embed_title, embed_description)
				conf_message = await message.channel.send(embed=embed)

				# pull all signups from database
				query = 'SELECT user_id FROM signups WHERE submission_time >= ' + str(time.time() - config.CYCLE)
				connect.crsr.execute(query)
				results = connect.crsr.fetchall()
				# check to make sure there are signups
				if results is not None:
					try:
						# create the tournament on Challonge
						tourney_manager.create_tournament(tournament_title, tournament_shortcut)
					except tourney_manager.challonge.api.ChallongeException:
						embed_title = 'Bracket URL Already Taken'
						embed_description = 'There is an issue with the name you tried to give the tournament. Please try a different tournament reference.'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('createbracket URL already taken')
						await conf_message.delete()
						return
					# iterate through all valid signups
					for entry in results:
						member = message.guild.get_member(entry[0])
						if member is not None:
							tourney_manager.add_participant(tournament_shortcut, member.display_name)
					# shuffle the participants
					tourney_manager.shuffle_seeds(tournament_shortcut)
					# send a final embed
					embed_title = 'Bracket Created'
					embed_description = 'Your bracket **' + tournament_title + '** has been created! Check it out here: https://challonge.com/' + tournament_shortcut
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('bracket created from signups')
				else:
					# send an error embed (no rows in the signups database)
					embed_title = 'Error Creating Bracket'
					embed_description = 'There aren\'t any signups for this cycle in the database yet.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('createbracket error sent to duel-mods')
				# delete the original confirmation embed
				await conf_message.delete()
				return
			return

		# '.creatematchchannels' command (duel-mods)
		if message_content.startswith('.creatematchchannels '):
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				await action_log('attempting to create match channels')
				tournament_shortcut = 'mmcycle' + message_content.split()[1]
				mm_guild = message.guild
				contest_category = mm_guild.get_channel(config.MATCH_CATEGORY_ID)
				category_channel_names = []
				for channel in contest_category.text_channels:
					category_channel_names.append(channel.name)
				await action_log(', '.join(category_channel_names))

				try:
					tournament_index = tourney_manager.index_tournament(tournament_shortcut)
					await action_log('tournament found')
				except urllib.error.HTTPError:
					embed_title = 'Invalid Tournament Reference'
					embed_description = 'I couldn\'t find a tournament matching the reference you provided. Please try again.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('tournament not found')
					return

				# send a confirmation embed
				embed_title = 'Creating Match Channels...'
				embed_description = 'Creating channels for any open matches.'
				embed = await generate_embed('yellow', embed_title, embed_description)
				conf_message = await message.channel.send(embed=embed)

				# iterate through all matches
				total_created = 0
				for match in tournament_index:
					if match['state'] == 'open':
						# if a match is open, create a channel for it
						participant1 = tourney_manager.show_participant(tournament_shortcut, match['player1-id'])['name']
						participant2 = tourney_manager.show_participant(tournament_shortcut, match['player2-id'])['name']
						channel_name = 'match-' + str(match['suggested-play-order']) + '-' + participant1[:5] + '-v-' + participant2[:5]
						unique = True
						for name in category_channel_names:
							if channel_name is name:
								unique = False
								await action_log('nope canceled')
						if unique:
							await mm_guild.create_text_channel(channel_name, category=contest_category)
							total_created += 1

				# check to see if any matches were created
				if total_created > 0:
					embed_title = 'Channel Creation Complete'
					embed_description = 'A total of ' + str(total_created) + ' channels were created!'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('channel creation complete - ' + str(total_created) + ' open matches')
					await conf_message.delete()
				else:
					embed_title = 'No Channels Created'
					embed_description = 'There were no open matches in the specified tournament. Please try again with a different tournament reference.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('no open matches in tournament')
					await conf_message.delete()
			return

		# '.clearparticipantstats' command (duel-mods)
		if message_content == '.clearparticipantstats':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# set participant stats to defaults in database
				query = 'UPDATE participants SET total_matches = DEFAULT, match_wins = DEFAULT, match_losses = DEFAULT, total_votes_for = DEFAULT, avg_final_meme_time = DEFAULT'
				connect.crsr.execute(query)
				connect.conn.commit()

				# build clearparticipantstats confirmation embed
				embed_title = 'Participant Stats Cleared'
				embed_description = 'All participant stats were cleared from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('participant stats cleared by duel-mods')
				return
			return

		# '.clearsignups' command (duel-mods)
		if message_content == '.clearsignups':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# delete all rows from signups database
				query = 'DELETE FROM signups'
				connect.crsr.execute(query)
				connect.conn.commit()

				# build clearsignups confirmation embed
				embed_title = 'Signups Cleared'
				embed_description = 'All signups were cleared from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('signups cleared by duel-mods')
				return
			return

		# '.clearmatches' command (duel-mods)
		if message_content == '.clearmatches':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# delete all rows from matches database
				query = 'DELETE FROM matches'
				connect.crsr.execute(query)
				connect.conn.commit()
				# delete all rows from votes database
				query = 'DELETE FROM votes'
				connect.crsr.execute(query)
				connect.conn.commit()

				# build clearmatches confirmation embed
				embed_title = 'Matches Cleared'
				embed_description = 'All matches and votes were cleared from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('matches and votes cleared by duel-mods')
				return
			return

		# '.help' command (duel-mods)
		if message_content.startswith('.help'):
			# check to see who is asking for help
			if message.author.id in config.ADMIN_IDS:
				# build admin help embed
				embed_title = 'Admin Commands'
				embed_description = help_cmd.admin_help
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('help query sent to duel-mods')
				return
			else:
				# build mod help embed
				embed_title = 'Mod Commands'
				embed_description = help_cmd.mod_help
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('help query sent to duel-mods')
				return

	# contest category specific commands
	if message.channel.category_id == config.MATCH_CATEGORY_ID:
		# '.startmatch' command (contest category)
		if message_content.startswith('.startmatch '):
			if len(message.mentions) == 2:
				# initialize important variables
				member1 = message.mentions[0]
				member2 = message.mentions[1]
				channel_id = message.channel.id

				embed_title = 'Starting Match'
				embed_description = 'Randomly selecting template...'
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)

				template_list = await client.get_channel(config.TEMPLATE_CHAN_ID).history(limit=200).flatten()
				await action_log('list of ' + str(len(template_list)) + ' templates compiled from #templates')
				duelmods_chan = client.get_channel(config.DUELMODS_CHAN_ID)
				if len(template_list) >= 1:
					template_message = random.choice(template_list)
					if len(template_message.embeds) == 1:
						template_url = template_message.embeds[0].image.url
						author_string = template_message.embeds[0].description
					else:
						template_url = template_message.attachments[0].url
						author_string = template_message.author.display_name

					# add match info to postgresql
					query = 'INSERT INTO matches (u1_id, u2_id, channel_id, template_message_id, creation_time) VALUES (' + str(member1.id) + ', ' + str(member2.id) + ', ' + str(channel_id) + ', ' + str(template_message.id) + ', ' + str(time.time()) + ')'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('match added to database')

					# build random template embed
					embed_title = 'Template for #' + message.channel.name
					embed_description = 'Here\'s a random template! This template was submitted by ' + author_string
					embed = await generate_embed('green', embed_title, embed_description, template_url)
					nonce = 'tempcon' + str(channel_id)
					await duelmods_chan.send(embed=embed, nonce=nonce)
					await duelmods_chan.send(message.author.mention)
					await action_log('template confirmation sent to duel-mods')
					return
				else:
					# build startmatch error (no templates)
					embed_title = 'Match Error'
					embed_description = 'No templates in #templates!'
					embed = await generate_embed('red',embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('no templates for .startmatch')
					return
			else:
				# build startmatch error embed (participants not specified)
				embed_title = 'Participants Not Specified'
				embed_description = 'The format to use this command is `.startmatch <@user> <@user>`, please be sure you\'re using it correctly.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('match participants not specified')
			return

		# '.splitmatch' command (contest category)
		if message_content.startswith('.splitmatch '):
			if len(message.mentions) == 2:
				# initialize important variables
				member1 = message.mentions[0]
				u1_id = member1.id
				member2 = message.mentions[1]
				u2_id = member2.id
				channel_id = message.channel.id

				# add match info to postgresql
				query = 'INSERT INTO matches (u1_id, u2_id, channel_id, creation_time) VALUES (' + str(member1.id) + ', ' + str(member2.id) + ', ' + str(channel_id) + ', ' + str(time.time()) + ')'
				connect.crsr.execute(query)
				connect.conn.commit()

				# respond with confirmation embed
				embed_title = 'Match Split'
				embed_description = 'Match between ' + member1.mention + ' and ' + member2.mention + ' has been split. Use `.startsolo @user` to get each user started.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('match split between ' + member1.name + '#' + member1.discriminator + ' and ' + member2.name + '#' + member2.discriminator)
				return
			else:
				embed_title = 'Participants Not Specified'
				embed_description = 'The format to use this command is `.splitmatch <@user> <@user>`, please be sure you\'re using it correctly.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('match participants not specified')
				return
			return

		# '.startsolo ' command (contest category)
		if message_content.startswith('.startsolo '):
			if len(message.mentions) == 1:
				await action_log('starting solo')
				match_user = message.mentions[0]
				match_channel = message.channel
				channel_id = message.channel.id

				query = 'SELECT creation_time, u1_id, u2_id, u1_submitted, u2_submitted, split_match_template_url FROM matches WHERE channel_id = ' + str(channel_id)
				connect.crsr.execute(query)
				results = connect.crsr.fetchall()
				result = None
				failed = False

				if len(results) > 1:
					result = [0, None, None, None, None, None]
					# find the most recent match by creation_time
					for match in results:
						if match[0] > result[0]:
							result = match
				elif len(results) == 1:
					result = results[0]
				else:
					# failed is true if there was never a match created in the active channel
					failed = True

				if not failed:
					# check to see if the mentioned user is "u1" in the database
					if match_user.id == result[1]:
						# check to see if the user has submitted
						if result[3]:
							embed_title = 'User Already Submitted'
							embed_description = 'This user has already submitted to their match in this channel.'
							embed = await generate_embed('red', embed_title, embed_description)
							await message.channel.send(embed=embed)
							return
						# if the user hasn't submitted, continue
						match_udb = 'u1_id'
						user_num = '1'
						await action_log('match and participant found')
					# check to see if the mentioned user is "u2" in the database
					elif match_user.id == result[2]:
						# check to see if the user has submitted
						if result[4]:
							embed_title = 'User Already Submitted'
							embed_description = 'This user has already submitted to their match in this channel.'
							embed = await generate_embed('red', embed_title, embed_description)
							await message.channel.send(embed=embed)
							return
						# if the user hasn't submitted, continue
						match_udb = 'u2_id'
						user_num = '2'
						await action_log('match and participant found')
					else:
						# failed is true if the mentioned user is not "u1" or "u2"
						failed = True

				template_url = result[5]
				u_channel = await match_user.create_dm()

				# verify that an existing match was found
				if not failed:
					# check to see if a template has already been specified
					if template_url is not None and not result[3] and not result[4]:
						embed_title = 'Match In Progress...'
						embed_description = 'Please wait for the other participant to finish their part of the match!'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('split match already in progress')
						return
					if template_url is not None:
						# update match start_time in database
						query = 'UPDATE matches SET start_time = ' + str(time.time()) + ' WHERE channel_id = ' + str(channel_id) + ' AND start_time IS NOT NULL AND template_message_id IS NULL AND split_match_template_url = \'' + template_url + '\''
						connect.crsr.execute(query)
						connect.conn.commit()
						await action_log('match start_time updated in database')

						# send notifying DMs to participant
						embed_title = 'Match Started'
						embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Here is your template:'
						embed = await generate_embed('yellow', embed_title, embed_description, template_url)
						# discord.errors.Forbidden triggers if u_channel.send() is stopped
						try:
							await u_channel.send(embed=embed)
							await action_log('user notified of match')
						except discord.errors.Forbidden:
							# build template confirmation error embed (user has DMs turned off)
							embed_title = 'Match Error'
							embed_description = 'The match participant has DMs disabled! The match could not be started.'
							embed = await generate_embed('red', embed_title, embed_description)
							await match_channel.send(embed=embed)
							await action_log('the participant has DMs turned off')
							return

						# send template to match channel
						embed_title = 'Match Started'
						embed_description = match_user.mention + ' has 30 minutes to hand in their final meme. Good luck!'
						embed = await generate_embed('green', embed_title, embed_description)
						await match_channel.send(embed=embed)
						await action_log('solo match started for ' + match_user.name + '#' + match_user.discriminator)

						# sleep for 15 minutes (config.MATCH_WARN1_TIME seconds)
						await asyncio.sleep(config.MATCH_WARN1_TIME)

						await action_log('checking submission status')
						# check for submissions, remind users to submit if they haven't yet
						query = 'SELECT ' + submitted + ' FROM matches WHERE ' + match_udb + ' = ' + str(match_user.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
						connect.crsr.execute(query)
						result = connect.crsr.fetchone()
						if result is not None:
							if result[0]:
								return
						# build reminder embed
						embed_title = 'Match Reminder'
						embed_description = '15 minutes remaining.'
						embed = await generate_embed('yellow', embed_title, embed_description)
						# executes if member has not submitted
						await u_channel.send(embed=embed)

						# sleep for 10 minutes (config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME seconds)
						await asyncio.sleep(config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME)

						await action_log('checking submission status')
						# check for submissions, remind users to submit if they haven't yet
						query = 'SELECT ' + submitted + ' FROM matches WHERE ' + match_udb + ' = ' + str(match_user.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
						connect.crsr.execute(query)
						result = connect.crsr.fetchone()
						if result is not None:
							if result[0]:
								return
						# build reminder embed
						embed_title = 'Match Reminder'
						embed_description = '5 minutes remaining. Make sure to submit your final meme before the time runs out.'
						embed = await generate_embed('yellow', embed_title, embed_description)
						# executes if member has not submitted
						await u_channel.send(embed=embed)

						# sleep for 5 minutes (config.MATCH_TIME - config.MATCH_WARN2_TIME seconds)
						await asyncio.sleep(config.MATCH_TIME - config.MATCH_WARN2_TIME)

						await action_log('checking submission status')
						# check for submissions, remind users to submit if they haven't yet
						query = 'SELECT ' + submitted + ' FROM matches WHERE ' + match_udb + ' = ' + str(match_user.id) + ' AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 5))
						connect.crsr.execute(query)
						result = connect.crsr.fetchone()
						if result[0]:
							return
						# build match end embed
						embed_title = 'Match Closed'
						embed_description = 'Your match has ended without your submission resulting in your disqualification. Next time, please be sure to submit your final meme before the time runs out!'
						embed1 = await generate_embed('red', embed_title, embed_description)
						await action_log('closing match')
						embed_title = 'Competitor Missed Deadline'
						# executes if member has not submitted
						await u_channel.send(embed=embed1)
						# build missed deadline embed
						embed_description = match_user.mention + ' has missed their submission deadline.'
						embed2 = await generate_embed('red', embed_title, embed_description)
						await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
						return
					else:
						embed_title = 'Starting Match'
						embed_description = 'Randomly selecting template...'
						embed = await generate_embed('yellow', embed_title, embed_description)
						await message.channel.send(embed=embed)

						template_list = await client.get_channel(config.TEMPLATE_CHAN_ID).history(limit=200).flatten()
						await action_log('list of ' + str(len(template_list)) + ' templates compiled from #templates')
						duelmods_chan = client.get_channel(config.DUELMODS_CHAN_ID)
						if len(template_list) >= 1:
							template_message = random.choice(template_list)
							if len(template_message.embeds) == 1:
								template_url = template_message.embeds[0].image.url
								author_string = template_message.embeds[0].description
							else:
								template_url = template_message.attachments[0].url
								author_string = template_message.author.display_name

							# update postgresql
							query = 'UPDATE matches SET template_message_id = ' + str(template_message.id) + ' WHERE ' + match_udb + ' = ' + str(match_user.id) + ' AND channel_id = ' + str(channel_id)
							connect.crsr.execute(query)
							connect.conn.commit()
							await action_log('match updated in database')

							# build random template embed
							embed_title = 'Template for #' + message.channel.name
							embed_description = 'Here\'s a random template! This template was submitted by ' + author_string
							embed = await generate_embed('green', embed_title, embed_description, template_url)
							nonce = 'sptemp' + user_num + str(channel_id)
							await duelmods_chan.send(embed=embed, nonce=nonce)
							await duelmods_chan.send(message.author.mention)
							await action_log('template confirmation sent to duel-mods')
							return
						else:
							# build startmatch error (no templates)
							embed_title = 'Match Error'
							embed_description = 'No templates in #templates!'
							embed = await generate_embed('red',embed_title, embed_description)
							await message.channel.send(embed=embed)
							await action_log('no templates for .startsolo')
							return
					return
				else:
					# inform the match channel that no existing match was found
					embed_title = 'No Active Match'
					embed_description = 'There is no match to start solo. To split this match, use the `.splitmatch @user @user` command.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('no active split match')
					return
			else:
				embed_title = 'Participant Not Specified'
				embed_description = 'The format to use this command is `.startsolo @user`, please be sure you\'re using it correctly.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('match participant not specified')
				return
			return

		########## CURRENTLY IN PROGRESS ##########

		# # '.startfinal' command (contest category)
		# if message_content.startswith('.startfinal '):
		# 	if len(message.mentions) == 2:
		# 		# initialize important variables
		# 		member1 = message.mentions[0]
		# 		u1_channel = await member1.create_dm()
		# 		member2 = message.mentions[1]
		# 		u2_channel = await member2.create_dm()
		# 		start_time = time.time()
		# 		channel_id = message.channel.id

		# 		# add match info to postgresql
		# 		query = 'INSERT INTO matches (u1_id, u2_id, start_time, channel_id) VALUES (' + str(member1.id) + ', ' + str(member2.id) + ', ' + str(start_time) + ', ' + str(channel_id) + ')'
		# 		connect.crsr.execute(query)
		# 		connect.conn.commit()
		# 		# send notifying DMs to participants
		# 		embed_title = 'Match Started'
		# 		if len(message.attachments) == 1:
		# 			# build match start embed with attached image
		# 			embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Here is your template:'
		# 			embed_link = message.attachments[0].url
		# 			embed = await generate_embed('yellow', embed_title, embed_description, embed_link)
		# 		else:
		# 			# build match start embed without attached image
		# 			embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Check the match channel for your template.'
		# 			embed = await generate_embed('yellow', embed_title, embed_description)
		# 		await u1_channel.send(embed=embed)
		# 		await u2_channel.send(embed=embed)
		# 		await action_log('users notified of match')

		# 		# build startmatch confirmation embed for match channel
		# 		embed_title = 'Match Started'
		# 		embed_description = member1.mention + ' and ' + member2.mention + ' have 30 minutes to hand in their final memes. Good luck!'
		# 		embed = await generate_embed('green', embed_title, embed_description)
		# 		await message.channel.send(embed=embed)
		# 		await action_log('match started between ' + member1.name + '#' + member1.discriminator + ' and ' + member2.name + '#' + member2.discriminator)

		# 		# sleep for 15 minutes (config.MATCH_WARN1_TIME seconds)
		# 		await asyncio.sleep(config.MATCH_WARN1_TIME)

		# 		await action_log('checking submission status')
		# 		# check for submissions, remind users to submit if they haven't yet
		# 		query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
		# 		connect.crsr.execute(query)
		# 		result = connect.crsr.fetchone()
		# 		if result is not None:
		# 			if result[0] and result[1]:
		# 				return
		# 		# build reminder embed
		# 		embed_title = 'Match Reminder'
		# 		embed_description = '15 minutes remaining.'
		# 		embed = await generate_embed('yellow', embed_title, embed_description)
		# 		# executes if member1 has not submitted
		# 		if not result[0]:
		# 			await u1_channel.send(embed=embed)
		# 		# executes if member2 has not submitted
		# 		if not result[1]:
		# 			await u2_channel.send(embed=embed)

		# 		# sleep for 10 minutes (config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME seconds)
		# 		await asyncio.sleep(config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME)

		# 		await action_log('checking submission status')
		# 		# check for submissions, remind users to submit if they haven't yet
		# 		query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
		# 		connect.crsr.execute(query)
		# 		result = connect.crsr.fetchone()
		# 		if result is not None:
		# 			if result[0] and result[1]:
		# 				return
		# 		# build reminder embed
		# 		embed_title = 'Match Reminder'
		# 		embed_description = '5 minutes remaining. Make sure to submit your final meme before the time runs out.'
		# 		embed = await generate_embed('yellow', embed_title, embed_description)
		# 		# executes if member1 has not submitted
		# 		if not result[0]:
		# 			await u1_channel.send(embed=embed)
		# 		# executes if member2 has not submitted
		# 		if not result[1]:
		# 			await u2_channel.send(embed=embed)

		# 		# sleep for 5 minutes (config.MATCH_TIME - config.MATCH_WARN2_TIME seconds)
		# 		await asyncio.sleep(config.MATCH_TIME - config.MATCH_WARN2_TIME)

		# 		await action_log('checking submission status')
		# 		# check for submissions, remind users to submit if they haven't yet
		# 		query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 5))
		# 		connect.crsr.execute(query)
		# 		result = connect.crsr.fetchone()
		# 		if result[0] and result[1]:
		# 			return
		# 		# build match end embed
		# 		embed_title = 'Match Closed'
		# 		embed_description = 'Your match has ended without your submission resulting in your disqualification. Next time, please be sure to submit your final meme before the time runs out!'
		# 		embed1 = await generate_embed('red', embed_title, embed_description)
		# 		await action_log('closing match')
		# 		embed_title = 'Competitor Missed Deadline'
		# 		# executes if member1 has not submitted
		# 		if not result[0]:
		# 			await u1_channel.send(embed=embed1)
		# 			# build missed deadline embed
		# 			embed_description = member1.mention + ' has missed their submission deadline.'
		# 			embed2 = await generate_embed('red', embed_title, embed_description)
		# 			await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
		# 		# executes if member2 has not submitted
		# 		if not result[1]:
		# 			await u2_channel.send(embed=embed1)
		# 			# build missed deadline embed
		# 			embed_description = member2.mention + ' has missed their submission deadline.'
		# 			embed2 = await generate_embed('red', embed_title, embed_description)
		# 			await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
		# 	else:
		# 		# build startmatch error embed (participants not specified)
		# 		embed_title = 'Participants Not Specified'
		# 		embed_description = 'The format to use this command is `.startmatch <@user> <@user>`, please be sure you\'re using it correctly.'
		# 		embed = await generate_embed('red', embed_title, embed_description)
		# 		await message.channel.send(embed=embed)
		# 		await action_log('match participants not specified')
		# 	return

		# '.showresults' command (contest category)
		if message_content.startswith('.showresults'):
			await action_log('showresults command in match channel')
			# check to see who submitted each meme
			query = 'SELECT db_id, u1_id, u2_id, a_meme, start_time FROM matches WHERE channel_id = ' + str(message.channel.id)
			connect.crsr.execute(query)
			results = connect.crsr.fetchall()
			if len(results) > 1:
				result = [0, 0, 0, 0, 0]
				# find the most recent match by start_time
				for match in results:
					if match[4] > result[4]:
						result = match
			elif len(results) == 1:
				result = results[0]
			else:
				# build showresults error embed (no previous match)
				embed_title = 'No Previous Match'
				embed_description = 'There is no match to show results from in this channel.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('no previous match')
				return

			# check how many votes image A got
			query = 'SELECT COUNT(*) FROM votes WHERE match_id = ' + str(result[0]) + ' AND a_vote = True'
			connect.crsr.execute(query)
			a_votes = connect.crsr.fetchone()[0]
			# check how many votes image B got
			query = 'SELECT COUNT(*) FROM votes WHERE match_id = ' + str(result[0]) + ' AND b_vote = True'
			connect.crsr.execute(query)
			b_votes = connect.crsr.fetchone()[0]
			# find winning image
			if a_votes > b_votes:
				winning_image = 'A'
			elif b_votes > a_votes:
				winning_image = 'B'
			elif a_votes == b_votes:
				winning_image = 'tie'

			# alert match channel of poll results
			# AttributeError triggers if participant is no longer in the guild
			try:
				if (result[3] == 1 and winning_image == 'A') or (result[3] == 2 and winning_image == 'B'):
					winner = message.channel.guild.get_member(result[1])
					loser = message.channel.guild.get_member(result[2])
				elif (result[3] == 2 and winning_image == 'A') or (result [3] == 1 and winning_image == 'B'):
					winner = message.channel.guild.get_member(result[2])
					loser = message.channel.guild.get_member(result[1])
				elif winning_image == 'tie':
					# build tie embed for match channel
					embed_title = 'Voting Results'
					embed_description = 'This match has ended in a ' + str(a_votes) + ' - ' + str(b_votes) + ' tie! Participants, please contact each other and find a time to rematch.'
					embed = await generate_embed('pink', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('match ended in a tie, results sent in match channel')
					return
				else:
					await action_log('winner not found or a_meme not defined in postgresql')
					return
			except AttributeError:
				await action_log('member from existing match was not found in the guild')
				return

			# build notification embed for match channel
			embed_title = 'Voting Results'
			embed_description = 'Congratulations to ' + winner.mention + ', you have won this match with image ' + winning_image + '! Thank you for participating ' + loser.mention + '. The final score was ' + str(a_votes) + ' - ' + str(b_votes) + '.'
			embed = await generate_embed('pink', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('voting results sent in match channel')
			return
		return

# client event triggers on any discord reaction add
@client.event
async def on_reaction_add(reaction, user):
	# create variable for base message
	message = reaction.message
	# only act on polls
	if message.nonce == 'poll':
		if not user.bot:
			# remove the user's reaction from the bot (anonymous polling)
			await reaction.remove(user)
			await action_log('reaction added to poll by ' + user.name + '#' + user.discriminator)

			#if not config.TESTING:
			# check for existing participant in database
			query = 'SELECT match_votes FROM participants WHERE user_id = ' + str(user.id)
			connect.crsr.execute(query)
			result = connect.crsr.fetchone()
			if result is None:
				# create participant if none exists
				query = 'INSERT INTO participants (user_id) VALUES (' + str(user.id) + ')'
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('no existing user, new user added to participants table in postgresql')
				participant_match_votes = 0
			else:
				participant_match_votes = result[0]

			# find the ID of the active match
			query = 'SELECT db_id FROM matches WHERE channel_id = ' + str(message.channel.id) + ' AND start_time >= ' + str(time.time() - (config.BASE_POLL_TIME + config.MATCH_TIME + 5))
			connect.crsr.execute(query)
			result = connect.crsr.fetchone()
			if result is not None:
				match_id = result[0]
				# create dm channel with the user
				user_channel = await user.create_dm()
				# check postgresql database for an existing vote by the user in the specified match
				query = 'SELECT a_vote, b_vote FROM votes WHERE user_id = ' + str(user.id) + ' AND match_id = ' + str(match_id)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result is not None:
					if result[0] or result[1]:
						# find which image the user originally voted for
						if result[0] and reaction.emoji == '🇦':
							vote_position = 'A'
						elif result[1] and reaction.emoji == '🇧':
							vote_position = 'B'
						else:
							# send the user a warning if their vote broke any rules
							embed_title = 'Invalid Vote'
							embed_description = 'To change your vote, first remove your original vote by reacting with the letter of the image you chose first.'
							embed = await generate_embed('red', embed_title, embed_description)
							# send embed to the user via dm
							await user_channel.send(embed=embed)
							await action_log('invalid vote in match by ' + user.name + '#' + user.discriminator)
							return
						# generate vote removal embed
						embed_title = 'Vote Removal'
						embed_description = 'Your vote for image ' + vote_position + ' has been removed.'
						embed = await generate_embed('yellow', embed_title, embed_description)
						# remove vote from postgresql
						query = 'DELETE FROM votes WHERE user_id = ' + str(user.id) + ' AND match_id = ' + str(match_id)
						connect.crsr.execute(query)
						connect.conn.commit()
						await action_log('vote removed from match by ' + user.name + '#' + user.discriminator)
						if not config.TESTING:
							# update participant stats
							query = 'UPDATE participants SET match_votes = ' + str(participant_match_votes - 1) + ' WHERE user_id = ' + str(user.id)
							connect.crsr.execute(query)
							connect.conn.commit()
							await action_log('participant stats updated')
						# send embed to the user via dm
						await user_channel.send(embed=embed)
						return
					return
				# find which image the user voted for
				if reaction.emoji == '🇦':
					vote_position = 'A'
					query = 'INSERT INTO votes (user_id, match_id, a_vote) VALUES (' + str(user.id) + ', ' + str(match_id) + ', True)'
				elif reaction.emoji == '🇧':
					vote_position = 'B'
					query = 'INSERT INTO votes (user_id, match_id, b_vote) VALUES (' + str(user.id) + ', ' + str(match_id) + ', True)'
				else:
					await action_log('no vote position specified')
					return
				# add vote info to postgresql via the above queries
				connect.crsr.execute(query)
				connect.conn.commit()
				if not config.TESTING:
					# update participant stats
					query = 'UPDATE participants SET match_votes = ' + str(participant_match_votes + 1) + ' WHERE user_id = ' + str(user.id)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('participant stats updated')
				# send vote confirmation to the user via dm
				embed_title = 'Vote Confirmation'
				embed_description = 'Your vote for image ' + vote_position + ' has been confirmed. If you\'d like to change your vote, remove this vote by using the same emoji.'
				embed = await generate_embed('green', embed_title, embed_description)
				await user_channel.send(embed=embed)
				await action_log('vote confirmation sent to user')
		return

	if message.nonce is not None:	
		# act on template confirmations for split matches
		if message.nonce.startswith('sptemp'):
			# don't act on bot reactions
			if not user.bot:
				# find match channel and competing user
				if message.nonce.startswith('sptemp1'):
					match_udb = 'u1_id'
					submitted = 'u1_submitted'
					match_channel = client.get_channel(int(message.nonce.lstrip('sptemp1')))
				elif message.nonce.startswith('sptemp2'):
					match_udb = 'u2_id'
					submitted = 'u2_submitted'
					match_channel = client.get_channel(int(message.nonce.lstrip('sptemp2')))
				else:
					embed_title = 'Unexpected Nonce Error'
					embed_description = 'Please contact lukenamop about this error.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('unexpected nonce error with split match template confirmation')
					return

				# pull match data from database
				query = 'SELECT ' + match_udb + ', template_message_id FROM matches WHERE start_time IS NULL AND template_message_id IS NOT NULL AND channel_id = ' + str(match_channel.id)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				# save match data to variables and start DM channel with participant
				member = message.guild.get_member(result[0])
				u_channel = await member.create_dm()

				# get custom emojis from discord
				check_emoji = client.get_emoji(637394596472815636)
				x_emoji = client.get_emoji(637394622200676396)
				if check_emoji == None or x_emoji == None:
					await action_log('ERROR IN TEMPLATE RANDOMIZATION -- EMOJI NOT FOUND')
					return

				# get url information from the base message
				template_url = message.embeds[0].image.url
				template_message_id = result[1]
				template_message = await client.get_channel(config.TEMPLATE_CHAN_ID).fetch_message(template_message_id)

				#  find which reaction was added
				if reaction.emoji == check_emoji:
					# delete original message
					await message.delete()
					# build template accepted embed
					embed_title = 'Template Accepted'
					embed_description = 'The randomized template was accepted. It has been sent to the competing user and stored in the database.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('randomized template accepted')

					# update match start_time and split_match_template_url in database
					query = 'UPDATE matches SET start_time = ' + str(time.time()) + ', template_message_id = NULL, split_match_template_url = \'' + template_url + '\' WHERE channel_id = ' + str(match_channel.id) + ' AND start_time IS NULL AND template_message_id IS NOT NULL'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('match start_time updated in database')

					# send notifying DMs to participant
					embed_title = 'Match Started'
					embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Here is your template:'
					embed = await generate_embed('yellow', embed_title, embed_description, template_url)
					# discord.errors.Forbidden triggers if u_channel.send() is stopped
					try:
						await u_channel.send(embed=embed)
						await action_log('user notified of match')
					except discord.errors.Forbidden:
						# build template confirmation error embed (user has DMs turned off)
						embed_title = 'Match Error'
						embed_description = 'The match participant has DMs disabled! The match could not be started.'
						embed = await generate_embed('red', embed_title, embed_description)
						await match_channel.send(embed=embed)
						await action_log('the participant has DMs turned off')

						# remove match from database
						query = 'DELETE FROM matches WHERE channel_id = ' + str(match_channel.id) + ' AND start_time IS NOT NULL AND template_message_id IS NOT NULL'
						connect.crsr.execute(query)
						connect.conn.commit()
						await action_log('match removed from database')
						return

					# delete message from match channel
					await match_channel.last_message.delete()
					# send template to match channel
					embed_title = 'Match Started'
					embed_description = member.mention + ' has 30 minutes to hand in their final meme. Good luck!'
					embed = await generate_embed('green', embed_title, embed_description)
					await match_channel.send(embed=embed)
					await action_log('solo match started for ' + member.name + '#' + member.discriminator)

					if not config.TESTING:
						# delete template from #templates channel
						await template_message.delete()
						await action_log('template deleted from templates channel')

					# sleep for 15 minutes (config.MATCH_WARN1_TIME seconds)
					await asyncio.sleep(config.MATCH_WARN1_TIME)

					await action_log('checking submission status')
					# check for submissions, remind users to submit if they haven't yet
					query = 'SELECT ' + submitted + ' FROM matches WHERE ' + match_udb + ' = ' + str(member.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
					connect.crsr.execute(query)
					result = connect.crsr.fetchone()
					if result is not None:
						if result[0]:
							return
					# build reminder embed
					embed_title = 'Match Reminder'
					embed_description = '15 minutes remaining.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					# executes if member has not submitted
					await u_channel.send(embed=embed)

					# sleep for 10 minutes (config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME seconds)
					await asyncio.sleep(config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME)

					await action_log('checking submission status')
					# check for submissions, remind users to submit if they haven't yet
					query = 'SELECT ' + submitted + ' FROM matches WHERE ' + match_udb + ' = ' + str(member.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
					connect.crsr.execute(query)
					result = connect.crsr.fetchone()
					if result is not None:
						if result[0]:
							return
					# build reminder embed
					embed_title = 'Match Reminder'
					embed_description = '5 minutes remaining. Make sure to submit your final meme before the time runs out.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					# executes if member has not submitted
					await u_channel.send(embed=embed)

					# sleep for 5 minutes (config.MATCH_TIME - config.MATCH_WARN2_TIME seconds)
					await asyncio.sleep(config.MATCH_TIME - config.MATCH_WARN2_TIME)

					await action_log('checking submission status')
					# check for submissions, remind users to submit if they haven't yet
					query = 'SELECT ' + submitted + ' FROM matches WHERE ' + match_udb + ' = ' + str(member.id) + ' AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 5))
					connect.crsr.execute(query)
					result = connect.crsr.fetchone()
					if result[0]:
						return
					# build match end embed
					embed_title = 'Match Closed'
					embed_description = 'Your match has ended without your submission resulting in your disqualification. Next time, please be sure to submit your final meme before the time runs out!'
					embed1 = await generate_embed('red', embed_title, embed_description)
					await action_log('closing match')
					embed_title = 'Competitor Missed Deadline'
					# executes if member has not submitted
					await u_channel.send(embed=embed1)
					# build missed deadline embed
					embed_description = member.mention + ' has missed their submission deadline.'
					embed2 = await generate_embed('red', embed_title, embed_description)
					await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
				elif reaction.emoji == x_emoji:
					# delete original message
					await message.delete()
					# build template rejected embed
					embed_title = 'Template Rejected'
					embed_description = 'The randomized template was rejected. Please try `.splitmatch` and `.startsolo` again.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('randomized template rejected')

					# delete message from match channel
					await match_channel.last_message.delete()
					# send embed in match channel
					await match_channel.send(embed=embed)
					await action_log('match channel notified')

					# remove match from database
					query = 'DELETE FROM matches WHERE channel_id = ' + str(match_channel.id) + ' AND start_time IS NULL AND template_message_id IS NOT NULL'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('match removed from database')
			return

		# act on template confirmations for normal matches
		if message.nonce.startswith('tempcon'):
			# don't act on bot reactions
			if not user.bot:
				# find match channel
				match_channel = client.get_channel(int(message.nonce.lstrip('tempcon')))

				# pull match data from database
				query = 'SELECT u1_id, u2_id, template_message_id FROM matches WHERE start_time IS NULL AND template_message_id IS NOT NULL AND channel_id = ' + str(match_channel.id)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				# save match data to variables and start DM channels with participants
				member1 = message.guild.get_member(result[0])
				u1_channel = await member1.create_dm()
				member2 = message.guild.get_member(result[1])
				u2_channel = await member2.create_dm()

				# get custom emojis from discord
				check_emoji = client.get_emoji(637394596472815636)
				x_emoji = client.get_emoji(637394622200676396)
				if check_emoji == None or x_emoji == None:
					await action_log('ERROR IN TEMPLATE RANDOMIZATION -- EMOJI NOT FOUND')
					return

				# get url information from the base message
				template_url = message.embeds[0].image.url
				template_message_id = result[2]
				template_message = await client.get_channel(config.TEMPLATE_CHAN_ID).fetch_message(template_message_id)

				#  find which reaction was added
				if reaction.emoji == check_emoji:
					# delete original message
					await message.delete()
					# build template accepted embed
					embed_title = 'Template Accepted'
					embed_description = 'The randomized template was accepted and sent in the match channel!'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('randomized template accepted')

					# update match start_time in database
					query = 'UPDATE matches SET start_time = ' + str(time.time()) + ', template_message_id = NULL WHERE channel_id = ' + str(match_channel.id) + ' AND start_time IS NULL AND template_message_id IS NOT NULL'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('match start_time updated in database')

					# send notifying DMs to participants
					embed_title = 'Match Started'
					embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Here is your template:'
					embed = await generate_embed('yellow', embed_title, embed_description, template_url)
					# discord.errors.Forbidden triggers if u_channel.send() is stopped
					try:
						await u1_channel.send(embed=embed)
						await u2_channel.send(embed=embed)
						await action_log('users notified of match')
					except discord.errors.Forbidden:
						# build template confirmation error embed (user has DMs turned off)
						embed_title = 'Match Error'
						embed_description = 'One of the match participants has DMs disabled! The match could not be started.'
						embed = await generate_embed('red', embed_title, embed_description)
						await match_channel.send(embed=embed)
						await action_log('one of the participants has DMs turned off')

						# remove match from database
						query = 'DELETE FROM matches WHERE channel_id = ' + str(match_channel.id) + ' AND start_time IS NOT NULL AND template_message_id IS NOT NULL'
						connect.crsr.execute(query)
						connect.conn.commit()
						await action_log('match removed from database')
						return

					# delete message from match channel
					await match_channel.last_message.delete()
					# send template to match channel
					embed_title = 'Match Started'
					embed_description = member1.mention + ' and ' + member2.mention + ' have 30 minutes to hand in their final memes. Good luck! (thanks to ' + template_message.embeds[0].description.split(' (')[0] + ' for the template)'
					embed = await generate_embed('green', embed_title, embed_description, template_url)
					await match_channel.send(embed=embed)
					await action_log('match started between ' + member1.name + '#' + member1.discriminator + ' and ' + member2.name + '#' + member2.discriminator)

					if not config.TESTING:
						# delete template from #templates channel
						await template_message.delete()
						await action_log('template deleted from templates channel')

					# sleep for 15 minutes (config.MATCH_WARN1_TIME seconds)
					await asyncio.sleep(config.MATCH_WARN1_TIME)

					await action_log('checking submission status')
					# check for submissions, remind users to submit if they haven't yet
					query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
					connect.crsr.execute(query)
					result = connect.crsr.fetchone()
					if result is not None:
						if result[0] and result[1]:
							return
					# build reminder embed
					embed_title = 'Match Reminder'
					embed_description = '15 minutes remaining.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					# executes if member1 has not submitted
					if not result[0]:
						await u1_channel.send(embed=embed)
					# executes if member2 has not submitted
					if not result[1]:
						await u2_channel.send(embed=embed)

					# sleep for 10 minutes (config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME seconds)
					await asyncio.sleep(config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME)

					await action_log('checking submission status')
					# check for submissions, remind users to submit if they haven't yet
					query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
					connect.crsr.execute(query)
					result = connect.crsr.fetchone()
					if result is not None:
						if result[0] and result[1]:
							return
					# build reminder embed
					embed_title = 'Match Reminder'
					embed_description = '5 minutes remaining. Make sure to submit your final meme before the time runs out.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					# executes if member1 has not submitted
					if not result[0]:
						await u1_channel.send(embed=embed)
					# executes if member2 has not submitted
					if not result[1]:
						await u2_channel.send(embed=embed)

					# sleep for 5 minutes (config.MATCH_TIME - config.MATCH_WARN2_TIME seconds)
					await asyncio.sleep(config.MATCH_TIME - config.MATCH_WARN2_TIME)

					await action_log('checking submission status')
					# check for submissions, remind users to submit if they haven't yet
					query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 5))
					connect.crsr.execute(query)
					result = connect.crsr.fetchone()
					if result[0] and result[1]:
						return
					# build match end embed
					embed_title = 'Match Closed'
					embed_description = 'Your match has ended without your submission resulting in your disqualification. Next time, please be sure to submit your final meme before the time runs out!'
					embed1 = await generate_embed('red', embed_title, embed_description)
					await action_log('closing match')
					embed_title = 'Competitor Missed Deadline'
					# executes if member1 has not submitted
					if not result[0]:
						await u1_channel.send(embed=embed1)
						# build missed deadline embed
						embed_description = member1.mention + ' has missed their submission deadline.'
						embed2 = await generate_embed('red', embed_title, embed_description)
						await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
					# executes if member2 has not submitted
					if not result[1]:
						await u2_channel.send(embed=embed1)
						# build missed deadline embed
						embed_description = member2.mention + ' has missed their submission deadline.'
						embed2 = await generate_embed('red', embed_title, embed_description)
						await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
				elif reaction.emoji == x_emoji:
					# delete original message
					await message.delete()
					# build template rejected embed
					embed_title = 'Template Rejected'
					embed_description = 'The randomized template was rejected. Please try `.startmatch` again.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('randomized template rejected')

					# delete message from match channel
					await match_channel.last_message.delete()
					# send embed in match channel
					await match_channel.send(embed=embed)
					await action_log('match channel notified')

					# remove match from database
					query = 'DELETE FROM matches WHERE channel_id = ' + str(match_channel.id) + ' AND start_time IS NULL AND template_message_id IS NOT NULL'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('match removed from database')
			return
		return
	return

# client event triggers on any discord channel creation
# @client.event
# async def on_channel_create(channel):
# 	if channel.name.startswith('match'):
# 		return

# client event triggers when discord bot client is fully loaded and ready
@client.event
async def on_ready():
	# change discord bot client presence to 'playing Meme Madness' 
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Meme Madness'))
	# send ready confirmation to command line
	print('Logged in as ' + client.user.name + ' - ' + str(client.user.id))
	if config.TESTING:
		print('Currently in TESTING MODE')
	print('------')

# starts instance of discord bot client
client.run(config.TOKEN)