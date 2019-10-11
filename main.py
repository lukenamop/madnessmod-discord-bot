#!/usr/bin/env python3

import discord
import asyncio
import time
import datetime
import re
import os
import requests
import random
import string
from unidecode import unidecode
from time import gmtime
from time import strftime

import connect
import config
import verify
import functions
import help_cmd

client = discord.Client()

async def action_log(reason):
	print(str(datetime.datetime.utcnow()) + ' - ' + reason)

async def generate_embed(color, title, description, attachment=None):
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
	embed = discord.Embed(
		color=color,
		title=title,
		description=description,
		timestamp=datetime.datetime.now())
	embed.set_footer(text='Developed by lukenamop#0918')
	if attachment is not None:
		embed.set_image(url=attachment)
	return embed

@client.event
async def on_message(message):
	if message.author.bot:
		if message.author.id == 622139031756734492:
			if message.nonce == 'poll_message':
				# get base channel
				base_channel = message.channel
				# add reactions to match poll in match channel
				await message.add_reaction('🇦')
				await message.add_reaction('🇧')
				await action_log('added reactions to poll message')
				vote_pings_role = message.channel.guild.get_role(600356303033860106)
				await message.channel.send(vote_pings_role.mention + ' @here')

				# sleep for 2 hours (config.BASE_POLL_TIME)
				await asyncio.sleep(config.BASE_POLL_TIME)
				await action_log('waking back up in match channel')
				await message.delete()

				# check to see who submitted each meme
				query = 'SELECT db_id, u1_id, u2_id, a_meme FROM matches WHERE channel_id = ' + str(message.channel.id) + ' AND start_time >= ' + str(time.time() - (config.BASE_POLL_TIME + config.MATCH_TIME + 30))
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
						loser = base_channel.guild.get_member(result[2])
					elif (result[3] == 2 and winning_image == 'A') or (result [3] == 1 and winning_image == 'B'):
						winner = base_channel.guild.get_member(result[2])
						loser = base_channel.guild.get_member(result[1])
					elif winning_image == 'tie':
						# build tie embed for match channel
						embed_title = 'Voting Results'
						embed_description = 'This match has ended in a ' + str(a_votes) + ' - ' + str(b_votes) + ' tie! Participants, please contact each other and find a time to rematch.'
						embed = await generate_embed('pink', embed_title, embed_description)
						await base_channel.send(embed=embed)
						await action_log('match ended in a tie, results sent in match channel')
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
				# build notification embed for match channel
				embed_title = 'Voting Results'
				embed_description = 'Congratulations to ' + winner.mention + ', you have won this match with image ' + winning_image + '! Thank you for participating ' + loser.mention + '. The final score was ' + str(a_votes) + ' - ' + str(b_votes) + '.'
				embed = await generate_embed('pink', embed_title, embed_description)
				await base_channel.send(embed=embed)
				await action_log('voting results sent in match channel')
				query = 'UPDATE participants SET total_matches = total_matches + 1, match_wins = match_wins + 1, total_votes_for = total_votes_for + ' + str(winning_votes) + ' WHERE user_id = ' + str(winner.id)
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('winner participant stats updated')
				query = 'UPDATE participants SET total_matches = total_matches + 1, match_losses = match_losses + 1, total_votes_for = total_votes_for + ' + str(losing_votes) + ' WHERE user_id = ' + str(loser.id)
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('loser participant stats updated')
				return
			if message.channel.id == 599333803407835147:
				# add reactions to messages in #signups-and-templates
				await message.add_reaction('👍')
				await message.add_reaction('🤷')
				await message.add_reaction('👎')

				# update signup info with the message_id
				query = 'UPDATE signups SET message_id = ' + str(message.id) + ' WHERE message_id = 0'
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('message_id added to postgresql signup info')
				return
			return
		return

	message_content = unidecode(message.content.casefold().strip())

	# '.donate' command (all channels)
	if message_content == '.donate':
		embed_title = 'Donate to MadnessMod'
		embed_description = 'If you\'d like to donate to MadnessMod, please go to https://www.paypal.me/lukenamop\n\n100% of MadnessMod donations will go towards bot upkeep ($8 a month) and other Meme Madness fees.'
		embed = await generate_embed('pink', embed_title, embed_description)
		await message.channel.send(embed=embed)
		await action_log('donation info sent to ' + message.author.name + '#' + message.author.discriminator)
		return

	# '.stats' command (all channels)
	if message_content.startswith('.stats'):
		if len(message.mentions) == 1:
			user = message.mentions[0]
		else:
			user = message.author
		query = 'SELECT total_matches, match_wins, match_losses, total_votes_for, avg_final_meme_time FROM participants WHERE user_id = ' + str(user.id)
		connect.crsr.execute(query)
		results = connect.crsr.fetchone()
		if results is not None:
			if results[4] is not None:
				embed_title = 'Stats for ' + user.display_name
				embed_description = 'Total matches: ' + str(results[0]) + '\nMatch wins/losses: ' + str(results[1]) + '/' + str(results[2]) + '\nWin percentage: ' + str(round(float(results[1]) / float(results[0]))) + '%\nTotal votes for your memes: ' + str(results[3]) + '\nAvg. time per meme: ' + strftime("%Mm %Ss", gmtime(results[4]))
				embed = await generate_embed('pink', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('stats shared to ' + message.author.name + '#' + message.author.discriminator)
				return
		embed_title = 'No Stats Available'
		embed_description = user.display_name + ' needs to compete in a match to start recording stats.'
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
			if message.guild.id == 581695290986332160:
				verification_role = message.guild.get_role(599354132771504128)
			elif message.guild.id == 607342998497525808:
				verification_role = message.guild.get_role(607349686554329094)
			else:
				return
			base_member = message.author
			base_message = message
			embed_title = 'Verification Process Started'
			embed_description = base_member.mention + ', please check your Discord messages for the next steps!'
			embed = await generate_embed('yellow', embed_title, embed_description)
			base_bot_response = await message.channel.send(embed=embed)
			await action_log('verification started by ' + username_discriminator)
			user_channel = await base_member.create_dm()
			embed_title = 'Verification Attempt (Step 1/2)'
			embed_description = 'Please send the name of your reddit account here:'
			embed = await generate_embed('yellow', embed_title, embed_description)
			await user_channel.send(embed=embed)
			try:
				def check(m):
					return m.channel == user_channel and m.author.id == base_member.id
				message = await client.wait_for('message', check=check, timeout=120)
				reddit_username = message.content.split('/')[-1].lstrip('@')
				await action_log('verification username shared by ' + username_discriminator)
				unwanted_chars = ["0", "O", "l", "I"]
				char_choices = [char for char in string.ascii_letters if char not in unwanted_chars] + [char for char in string.digits if char not in unwanted_chars]
				verification_string = ''.join(random.choices(char_choices, k=6))
				# Checks to see if the command was used in MEX
				if base_message.guild.id == 607342998497525808:
					reddit_username = verify.send_message(reddit_username, verification_string, username_discriminator, mex=True)
				else:
					reddit_username = verify.send_message(reddit_username, verification_string, username_discriminator)
				if reddit_username is not None:
					await action_log('verification reddit message for ' + username_discriminator + ' sent to \'' + reddit_username + '\'')
					embed_title = 'Verification Attempt (Step 2/2)'
					embed_description = 'Check your reddit account for a message that I\'ve just sent. To complete verification, send your 6 character verification key here (case sensitive, type carefully):'
					embed = await generate_embed('yellow', embed_title, embed_description)
					await user_channel.send(embed=embed)
					def check(m):
						return m.channel == user_channel and m.author.id == base_member.id
					message = await client.wait_for('message', check=check, timeout=120)
					if message.content == verification_string:
						try:
							embed_title = 'Verification Complete'
							embed_description = 'Your account has been verified! Enjoy the server.'
							embed = await generate_embed('green', embed_title, embed_description)
							await base_member.edit(nick=reddit_username)
							await base_member.add_roles(verification_role)
							if base_message.guild.id == 607342998497525808:
								del_role = base_message.guild.get_role(607365580567216130)
								await base_member.remove_roles(del_role)
							verified = True
						except discord.errors.Forbidden:
							embed_title = 'Access Error'
							embed_description = 'For some reason I don\'t have permission to assign roles. Please contact lukenamop#0918.'
							embed = await generate_embed('red', embed_title, embed_description)
						await user_channel.send(embed=embed)
						# send a message to #general welcoming the new user
						embed_title = 'New User Has Joined'
						if base_message.guild.id == 607342998497525808:
							embed_description = base_member.mention + ', welcome to MEX! Please let a member of the mod team know if you need any help.'
							embed = await generate_embed('green', embed_title, embed_description)
							await client.get_channel(607342999751491585).send(embed=embed)
						elif base_message.guild.id == 581695290986332160:
							embed_description = base_member.mention + ', welcome to Meme Madness! Check out #info and #rules to see how this place is run and let a member of the mod team know if you need any help.'
							embed = await generate_embed('green', embed_title, embed_description)
							await client.get_channel(581695290986332162).send(embed=embed)
						await action_log('verification compeleted by ' + username_discriminator)
					else:
						embed_title = 'Verification Key Incorrect'
						embed_description = 'To try again, please send `.verify` in #verification.'
						embed = await generate_embed('red', embed_title, embed_description)
						await user_channel.send(embed=embed)
						await action_log('verification key incorrect from ' + username_discriminator)
				else:
					await action_log('verification username error for ' + username_discriminator + ', attempted name: ' + message.content.split('/')[-1])
					embed_title = 'Username Error'
					embed_description = 'To try again, please send `.verify` in #verification.'
					embed = await generate_embed('red', embed_title, embed_description)
					await user_channel.send(embed=embed)
			except asyncio.TimeoutError:
				embed_title = 'Verification Attempt Timed Out'
				embed_description = 'To try again, please send `.verify` in #verification.'
				embed = await generate_embed('red', embed_title, embed_description)
				await user_channel.send(embed=embed)
				await action_log('verification timed out for ' + username_discriminator)
			try:
				await base_message.delete()
				await base_bot_response.delete()
			except discord.errors.NotFound:
				await action_log('verification messages already deleted')
			if base_message.guild.id == 607342998497525808 and verified:
				await asyncio.sleep(180)
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
			member = client.get_guild(config.MM_GUILD_ID).get_member(message.author.id)
			if member is None:
				return
			query = 'SELECT template_required FROM settings WHERE guild_id = ' + str(config.MM_GUILD_ID)
			connect.crsr.execute(query)
			results = connect.crsr.fetchone()
			template_required = results[0]
			if template_required:
				if len(message.attachments) != 1:
					embed_title = 'Signup Started'
					embed_description = 'Please send me a blank template to confirm your signup! This signup attempt will expire in 120 seconds.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('signup attempted without attachment by ' + message.author.name + '#' + message.author.discriminator)
					try:
						def check(m):
							return m.channel.type == message.channel.type and m.author.id == message.author.id and len(m.attachments) == 1
						message = await client.wait_for('message', check=check, timeout=120)
						await action_log('signup attachment received from ' + message.author.name + '#' + message.author.discriminator)
					except asyncio.TimeoutError:
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
					if result is None:
						embed_title = 'Template Confirmation'
						embed_description = 'Thank you for submitting your template ' + message.author.mention + '! If there are any issues with your entry you will be contacted.'
						embed = await generate_embed('green', embed_title, embed_description)
						await message.channel.send(embed=embed)

						# send template to #signups-and-templates
						embed_title = 'Template Submission'
						embed_description = member.mention + ' (' + functions.escape_underscores(member.display_name) + ', ' + str(member.id) + ')'
						# file = discord.File(config.IMAGE_FOLDER + '/' + filename, filename=filename)
						embed_link = message.attachments[0].url
						embed = await generate_embed('green', embed_title, embed_description, embed_link)
						# await client.get_channel(599333803407835147).send(file=file, embed=embed)
						await client.get_channel(599333803407835147).send(embed=embed)
						await action_log('signup attachment sent to #signups-and-templates by ' + message.author.name + '#' + message.author.discriminator)

						# add signup info to postgresql
						query = 'INSERT INTO signups (user_id, message_id, submission_time) VALUES (' + str(message.author.id) + ', 0, ' + str(time.time()) + ')'
						connect.crsr.execute(query)
						connect.conn.commit()
						await action_log('signup info added to postgresql')
					else:
						embed_title = 'Error: Already Signed Up'
						embed_description = 'It looks like you\'ve already signed up for this cycle of Meme Madness! Contact a moderator if this is incorrect.'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('already signed up from ' + message.author.name + '#' + message.author.discriminator)
						return
			else:
				# check to see if user has signed up in the last 7 days (config.CYCLE seconds)
				query = 'SELECT * FROM signups WHERE user_id = ' + str(message.author.id) + ' AND submission_time >= ' + str(time.time() - config.CYCLE)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result is None:
					embed_title = 'Signup Confirmation'
					embed_description = 'Thank you for signing up ' + message.author.mention + '! If there are any issues with your entry you will be contacted.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)

					# send signup to #signups-and-templates
					embed_title = 'Signup Confirmed'
					embed_description = member.mention + ' (' + functions.escape_underscores(member.display_name) + ', ' + str(member.id) + ')'
					embed = await generate_embed('green', embed_title, embed_description)
					await client.get_channel(599333803407835147).send(embed=embed)
					await action_log('signup sent to #signups-and-templates by ' + message.author.name + '#' + message.author.discriminator)

					# add signup info to postgresql
					query = 'INSERT INTO signups (user_id, message_id, submission_time) VALUES (' + str(message.author.id) + ', 0, ' + str(time.time()) + ')'
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('signup info added to postgresql')
				else:
					embed_title = 'Error: Already Signed Up'
					embed_description = 'It looks like you\'ve already signed up for this cycle of Meme Madness! Contact a moderator if this is incorrect.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('already signed up from ' + message.author.name + '#' + message.author.discriminator)
					return
			query = 'SELECT * FROM participants WHERE user_id = ' + str(message.author.id)
			connect.crsr.execute(query)
			if connect.crsr.fetchone() is None:
				query = 'INSERT INTO participants (user_id) VALUES (' + str(message.author.id) + ')'
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('user added to participants table in postgresql')
			return

		# '.submit' command (DM)
		if message_content.startswith('.submit'):
			query = 'SELECT u1_id, u2_id, u1_submitted, u2_submitted, channel_id, start_time FROM matches WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
			connect.crsr.execute(query)
			result = connect.crsr.fetchone()
			# prepare embed for duplicate submissions
			embed_title = 'Error: Already Submitted'
			embed_description = 'It looks like you\'ve already submitted for your current match! If this is incorrect, contact a moderator.'
			embed = await generate_embed('red', embed_title, embed_description)
			# check for duplicate submissions
			if result is not None:
				start_time = result[5]
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
				if len(message.attachments) != 1:
					embed_title = 'Submission Started'
					embed_description = 'Please send me your final meme to confirm your submission! This submission attempt will expire in 120 seconds.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('submission attempted without attachment by ' + message.author.name + '#' + message.author.discriminator)
					try:
						def check(m):
							return m.channel.type == message.channel.type and m.author.id == message.author.id and len(m.attachments) == 1
						message = await client.wait_for('message', check=check, timeout=120)
						await action_log('submission attachment received from ' + message.author.name + '#' + message.author.discriminator)
					except asyncio.TimeoutError:
						embed_title = 'Submission Timed Out'
						embed_description = 'If you\'d like to submit your final meme, send me another message with `.submit`!'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('submission timed out by ' + message.author.name + '#' + message.author.discriminator)
						return
				else:
					await action_log('submission attachment received from ' + message.author.name + '#' + message.author.discriminator)

				embed_title = 'Submission Confirmation'
				embed_description = 'Thank you for submitting your final meme ' + message.author.mention + '! If there are any issues with your submission you will be contacted.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('final meme attachment sent in by ' + message.author.name + '#' + message.author.discriminator)

				# add submission info to postgresql
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
				query = 'SELECT avg_final_meme_time, total_matches FROM participants WHERE user_id = ' + str(message.author.id)
				connect.crsr.execute(query)
				results = connect.crsr.fetchone()
				if results[0] is None:
					new_avg_final_meme_time = time.time() - float(start_time)
				else:
					new_avg_final_meme_time = ((float(results[0] * results[1]) + (time.time() - float(start_time))) / float(results[1] + 1))
				query = 'UPDATE participants SET avg_final_meme_time = ' + str(new_avg_final_meme_time) + ' WHERE user_id = ' + str(message.author.id)
				connect.crsr.execute(query)
				connect.conn.commit()
				await action_log('participant stats updated')
				query = 'SELECT u1_id, u2_id, u1_submitted, u2_submitted, u1_image_url, u2_image_url, channel_id FROM matches WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				match_channel = client.get_channel(result[6])
				submissions_channel = client.get_channel(599758863700328459)
				# only execute if both users have submitted final memes
				if result[2] and result[3]:
					if u_order == 1:
						try:
							u1 = match_channel.guild.get_member(result[0])
							u1_mention = u1.mention
							u1_link = result[4]
							u2 = match_channel.guild.get_member(result[1])
							u2_mention = u2.mention
							u2_link = result[5]
						except AttributeError:
							await action_log('final meme submission stopped due to an AttributeError')
							return
						query = 'UPDATE matches SET a_meme = 1 WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
						connect.crsr.execute(query)
						connect.conn.commit()
					if u_order == 2:
						try:
							u1 = match_channel.guild.get_member(result[1])
							u1_mention = u1.mention
							u1_link = result[5]
							u2 = match_channel.guild.get_member(result[0])
							u2_mention = u2.mention
							u2_link = result[4]
						except AttributeError:
							await action_log('final meme submission stopped due to an AttributeError')
							return
						query = 'UPDATE matches SET a_meme = 2 WHERE (u1_id = ' + str(message.author.id) + ' OR u2_id = ' + str(message.author.id) + ') AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 10))
						connect.crsr.execute(query)
						connect.conn.commit()
					# send final memes to #submissions
					# submission for user 1
					embed_title = 'Final Meme Submission'
					embed_description = u1_mention + ' (' + u1.display_name + ', ' + str(result[0]) + ')'
					embed_link = u1_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await submissions_channel.send(embed=embed)
					# submission for user 2
					embed_description = u2_mention + ' (' + u2.display_name + ', ' + str(result[1]) + ')'
					embed_link = u2_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await submissions_channel.send(embed=embed)
					await action_log('final memes sent to #submissions')
					# send final memes to match channel
					embed_description = 'Image A'
					embed_link = u1_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await match_channel.send(embed=embed)
					embed_description = 'Image B'
					embed_link = u2_link
					embed = await generate_embed('green', embed_title, embed_description, embed_link)
					await match_channel.send(embed=embed)
					embed_title = 'Match Voting'
					embed_description = '**Vote for your favorite!** Results will be sent to this channel when voting ends in 2 hours.\n🇦 First image\n🇧 Second image'
					embed = await generate_embed('pink', embed_title, embed_description)
					await match_channel.send(embed=embed, nonce='poll_message')
				return
			else:
				embed_title = 'No Active Match'
				embed_description = 'You don\'t appear to have an active match to submit to right now.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('submission attempt without match by ' + message.author.name + '#' + message.author.discriminator)
				return

		# '.help' command (DM)
		if message_content.startswith('.help'):
			embed_title = 'Commands'
			embed_description = help_cmd.dm_help
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('help query sent to ' + message.author.name + '#' + message.author.discriminator)
			return
		return

	# duel-mods specific commands
	if message.channel.id == 600397545050734612 or message.channel.id == 581728812518080522:
		# '.resignup' command (duel-mods)
		if message_content.startswith('.resignup '):
			await action_log('resignup command in #duel-mods')
			try:
				message_split = message_content.split(' ', 2)
				user_id = int(message_split[1])
				reason = message_split[2]
				query = 'SELECT message_id FROM signups WHERE user_id = ' + str(user_id) + ' AND submission_time >= ' + str(time.time() - config.CYCLE)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result is not None:
					# DM user to notify of resignup
					user_channel = client.get_user(user_id).dm_channel
					if user_channel is None:
						user_channel = await client.get_user(user_id).create_dm()
					embed_title = 'Re-signup Required'
					embed_description = 'Your signup was removed for reason: `' + reason + '`. To enter this cycle of Meme Madness please `.signup` with a new template. If you have any questions please contact the moderators. Thank you!'
					embed = await generate_embed('red', embed_title, embed_description)
					await user_channel.send(embed=embed)
					await action_log('DM sent to user')

					# remove submission from #signups-and-templates
					message_id = result[0]
					try:
						msg = await client.get_channel(599333803407835147).fetch_message(message_id)
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
					embed_title = 'Signup Deleted'
					embed_description = message.guild.get_member(user_id).mention + '\'s signup has been deleted. I have sent them a DM including your reason for removing their signup and told them to `.signup` again if they\'d like to participate.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					return
				else:
					embed_title = 'Error: No Matching Signup'
					embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `622139031756734492`).'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('no matching submission error with resignup')
					return
			except IndexError:
				embed_title = 'Error: No Reason Given'
				embed_description = 'Please include a reason for removing the specified signup! The format is `.resignup <user ID> <reason>`.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('no reason given for resignup')
				return
			except ValueError:
				embed_title = 'Error: No Matching Signup'
				embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `622139031756734492`).'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('non-int passed to resignup')
				return

		# '.signuplist' command (duel-mods)
		if message_content.startswith('.signuplist'):
			query = 'SELECT user_id FROM signups WHERE submission_time >= ' + str(time.time() - config.CYCLE)
			connect.crsr.execute(query)
			embed_title = 'Signup List'
			if connect.crsr is not None:
				embed_description = ''
				total = 0
				for entry in connect.crsr:
					member = message.guild.get_member(entry[0])
					if member is not None:
						embed_description += functions.escape_underscores(member.display_name) + '\n'
						total += 1
				embed_description += '**Total signups: ' + str(total) + '**'
			else:
				embed_description = 'There aren\'t any signups for this cycle in the database yet.'
			embed = await generate_embed('green', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('signuplist sent to duel-mods')
			return

		# '.toggletemplates' command (duel-mods)
		if message_content == '.toggletemplates':
			if message.author.id == 324273473360887808:
				await action_log('signup templates toggled')
				query = 'SELECT template_required FROM settings WHERE guild_id = ' + str(config.MM_GUILD_ID)
				connect.crsr.execute(query)
				results = connect.crsr.fetchone()
				template_required = results[0]
				if template_required:
					query = 'UPDATE settings SET template_required = False WHERE guild_id = ' + str(config.MM_GUILD_ID)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('templates no longer required')
					embed_title = 'Templates Disabled'
					embed_description = 'Templates are no longer required with `.signup`'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('template toggle confirmation')
					return
				else:
					query = 'UPDATE settings SET template_required = True WHERE guild_id = ' + str(config.MM_GUILD_ID)
					connect.crsr.execute(query)
					connect.conn.commit()
					await action_log('templates now required')
					embed_title = 'Templates Enabled'
					embed_description = 'Templates are now required with `.signup`'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('template toggle confirmation')
					return

		# '.clearparticipantstats' command(duel-mods)
		if message_content == '.clearparticipantstats':
			if message.author.id == 324273473360887808:
				query = 'UPDATE participants SET total_matches = DEFAULT, match_wins = DEFAULT, match_losses = DEFAULT, total_votes_for = DEFAULT, avg_final_meme_time = DEFAULT'
				connect.crsr.execute(query)
				connect.conn.commit()
				embed_title = 'Participant Stats Cleared'
				embed_description = 'All participant stats were cleared from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('participant stats cleared by duel-mods')
				return
			return

		# '.clearsignups' command (duel-mods)
		if message_content == '.clearsignups':
			if message.author.id == 324273473360887808:
				query = 'DELETE FROM signups'
				connect.crsr.execute(query)
				connect.conn.commit()
				embed_title = 'Signups Cleared'
				embed_description = 'All signups were cleared from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('signups cleared by duel-mods')
				return
			return

		# '.clearmatches' command (duel-mods)
		if message_content == '.clearmatches':
			if message.author.id == 324273473360887808:
				query = 'DELETE FROM matches'
				connect.crsr.execute(query)
				connect.conn.commit()
				query = 'DELETE FROM votes'
				connect.crsr.execute(query)
				connect.conn.commit()
				embed_title = 'Matches Cleared'
				embed_description = 'All matches and votes were cleared from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('matches and votes cleared by duel-mods')
				return
			return

		# '.help' command (duel-mods)
		if message_content.startswith('.help'):
			if message.author.id == 324273473360887808:
				embed_title = 'Admin Commands'
				embed_description = help_cmd.admin_help
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('help query sent to duel-mods')
				return
			else:
				embed_title = 'Mod Commands'
				embed_description = help_cmd.mod_help
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('help query sent to duel-mods')
				return

	# contest category specific commands
	if message.channel.category_id == 581876790172319767:
		# '.startmatch' command (contest category)
		if message_content.startswith('.startmatch '):
			if len(message.mentions) == 2:
				# initialize important variables
				member1 = message.mentions[0]
				u1_channel = await member1.create_dm()
				member2 = message.mentions[1]
				u2_channel = await member2.create_dm()
				start_time = time.time()
				channel_id = message.channel.id
				# add match info to postgresql
				query = 'INSERT INTO matches (u1_id, u2_id, start_time, channel_id) VALUES (' + str(member1.id) + ', ' + str(member2.id) + ', ' + str(start_time) + ', ' + str(channel_id) + ')'
				connect.crsr.execute(query)
				connect.conn.commit()
				# send notifying DMs to participants
				embed_title = 'Match Started'
				if len(message.attachments) == 1:
					embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Here is your template:'
					embed_link = message.attachments[0].url
					embed = await generate_embed('yellow', embed_title, embed_description, embed_link)
				else:
					embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Check the match channel for your template.'
					embed = await generate_embed('yellow', embed_title, embed_description)
				await u1_channel.send(embed=embed)
				await u2_channel.send(embed=embed)
				await action_log('users notified of match')
				# respond with confirmation embed
				embed_title = 'Match Started'
				embed_description = member1.mention + ' and ' + member2.mention + ' have 30 minutes to hand in their final memes. Good luck!'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('match started between ' + member1.name + '#' + member1.discriminator + ' and ' + member2.name + '#' + member2.discriminator)

				# sleep for 15 minutes (config.MATCH_WARN1_TIME)
				await asyncio.sleep(config.MATCH_WARN1_TIME)
				# check for submissions, remind users to submit if they haven't yet
				await action_log('checking submission status')
				query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result is not None:
					if result[0] and result[1]:
						return
				embed_title = 'Match Reminder'
				embed_description = '15 minutes remaining.'
				embed = await generate_embed('yellow', embed_title, embed_description)
				# executes if member1 has not submitted
				if not result[0]:
					await u1_channel.send(embed=embed)
				# executes if member2 has not submitted
				if not result[1]:
					await u2_channel.send(embed=embed)

				# sleep for 10 minutes (config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME)
				await asyncio.sleep(config.MATCH_WARN2_TIME - config.MATCH_WARN1_TIME)
				# check for submissions, remind users to submit if they haven't yet
				await action_log('checking submission status')
				query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - config.MATCH_TIME + 5)
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result is not None:
					if result[0] and result[1]:
						return
				embed_title = 'Match Reminder'
				embed_description = '5 minutes remaining. Make sure to submit your final meme before the time runs out.'
				embed = await generate_embed('yellow', embed_title, embed_description)
				# executes if member1 has not submitted
				if not result[0]:
					await u1_channel.send(embed=embed)
				# executes if member2 has not submitted
				if not result[1]:
					await u2_channel.send(embed=embed)

				# sleep for 5 minutes (config.MATCH_TIME - config.MATCH_WARN2_TIME)
				await asyncio.sleep(config.MATCH_TIME - config.MATCH_WARN2_TIME)
				# check for submissions, remind users to submit if they haven't yet
				await action_log('checking submission status')
				query = 'SELECT u1_submitted, u2_submitted FROM matches WHERE u1_id = ' + str(member1.id) + ' AND u2_id = ' + str(member2.id) + ' AND start_time >= ' + str(time.time() - (config.MATCH_TIME + 5))
				connect.crsr.execute(query)
				result = connect.crsr.fetchone()
				if result[0] and result[1]:
					return
				embed_title = 'Match Closed'
				embed_description = 'Your match has ended without your submission resulting in your disqualification. Next time, please be sure to submit your final meme before the time runs out!'
				embed1 = await generate_embed('red', embed_title, embed_description)
				await action_log('closing match')
				embed_title = 'Competitor Missed Deadline'
				# executes if member1 has not submitted
				if not result[0]:
					await u1_channel.send(embed=embed1)
					embed_description = member1.mention + ' has missed their submission deadline.'
					embed2 = await generate_embed('red', embed_title, embed_description)
					await client.get_channel(599758863700328459).send(embed=embed2)
				# executes if member2 has not submitted
				if not result[1]:
					await u2_channel.send(embed=embed1)
					embed_description = member2.mention + ' has missed their submission deadline.'
					embed2 = await generate_embed('red', embed_title, embed_description)
					await client.get_channel(599758863700328459).send(embed=embed2)
			else:
				embed_title = 'Participants Not Specified'
				embed_description = 'The format to use this command is `.startmatch <@user> <@user>`, please be sure you\'re using it correctly.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('match participants not specified')
			return

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
					if match[4] > result[0]:
						result = match
			elif len(results) == 1:
				result = results[0]
			else:
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

@client.event
async def on_reaction_add(reaction, user):
	message = reaction.message
	if message.nonce == 'poll_message':
		if not user.bot:
			# remove the user's reaction from the bot (anonymous polling)
			await reaction.remove(user)
			await action_log('reaction added to poll by ' + user.name + '#' + user.discriminator)

			# find the ID of the active match
			query = 'SELECT db_id FROM matches WHERE channel_id = ' + str(message.channel.id) + ' AND start_time >= ' + str(time.time() - (config.BASE_POLL_TIME + config.MATCH_TIME + 5))
			connect.crsr.execute(query)
			result = connect.crsr.fetchone()
			if result is not None:
				match_id = result[0]
				# create dm channel with the user
				user_channel = await user.create_dm()
				# check postgresql for an existing vote by the user in the specified match
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
						# send embed to the user via dm
						await user_channel.send(embed=embed)
						await action_log('vote removed from match by ' + user.name + '#' + user.discriminator)
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
				# send vote confirmation to the user via dm
				embed_title = 'Vote Confirmation'
				embed_description = 'Your vote for image ' + vote_position + ' has been confirmed. If you\'d like to change your vote, remove this vote by using the same emoji.'
				embed = await generate_embed('green', embed_title, embed_description)
				await user_channel.send(embed=embed)
				await action_log('vote confirmation sent to user')
	return

# @client.event
# async def on_channel_create(channel):
# 	if channel.name.startswith('match'):
# 		return

@client.event
async def on_ready():
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Meme Madness'))
	print('Logged in as ' + client.user.name + ' - ' + str(client.user.id))
	print('------')

client.run(config.TOKEN)