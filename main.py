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
from discord.ext import tasks
from unidecode import unidecode
from time import gmtime
from time import strftime
from math import ceil

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
	print(f'{datetime.datetime.utcnow()} - {reason}')

# generate a discord embed with an optional attached image
async def generate_embed(color, title, description, attachment=None, timestamp=None):
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
		color = 0x2691d9
	elif color == 'orange':
		color = 0xff9900

	# given timestamp string, create datetime object
	if timestamp is not None:
		datetime_obj = datetime.datetime.fromtimestamp(timestamp)
	else:
		datetime_obj = datetime.datetime.now()

	# create discord embed
	embed = discord.Embed(
		color=color,
		title=title,
		description=description,
		timestamp=datetime_obj)
	embed.set_footer(text='Developed by lukenamop#0918')
	if attachment is not None:
		embed.set_image(url=attachment)
	return embed

# function to safely execute SQL queries, with error handling for closed connections
async def execute_sql(query, q_args=None, attempt=1):
	reconnect_and_retry = False
	try:
		if q_args is None:
			# execute a basic SQL query
			connect.crsr.execute(query)
		else:
			# find out how many arguments there are
			q_arg_len = len(q_args)
			if q_arg_len == 1:
				connect.crsr.execute(query, (q_args))
			elif q_arg_len > 1:
				connect.crsr.execute(query, q_args)

	except connect.psycopg2.errors.InFailedSqlTransaction as error:
		reconnect_and_retry = True
		await action_log(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')
	except connect.psycopg2.OperationalError as error:
		reconnect_and_retry = True
		await action_log(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')
	except connect.psycopg2.InterfaceError as error:
		reconnect_and_retry = True
		await action_log(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')
	except connect.psycopg2.DatabaseError as error:
		reconnect_and_retry = True
		await action_log(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')

	# reconnect to the database and try to re-execute the SQL query
	if reconnect_and_retry:
		success = connect.db_connect()
		if success:
			await action_log('reconnection was a success')
			# only try 3 times, if it still doesn't work there is some larger issue
			if attempt <= 3:
				await execute_sql(query, q_args=q_args, attempt=(attempt + 1))
		else:
			await action_log('connection failed')
	return

# end_polls task
@tasks.loop()
async def end_polls():
	# find all ended polls
	query = 'SELECT db_id, u1_id, u2_id, a_meme, u1_image_url, u2_image_url, poll_start_time, poll_extensions, poll_message_id, channel_id FROM matches WHERE completed = False AND poll_start_time IS NOT NULL AND poll_start_time <= %s'
	q_args = [int(time.time()) - config.BASE_POLL_TIME]
	await execute_sql(query, q_args)
	results = connect.crsr.fetchall()
	await action_log(f'{len(results)} polls to end')
	if len(results) > 0:
		for result in results:
			# initialize important variables
			db_id, u1_id, u2_id, a_meme, u1_image_url, u2_image_url, poll_start_time, poll_extensions, poll_message_id, channel_id = result
			poll_start_time = int(poll_start_time)
			poll_extensions = int(poll_extensions)
			poll_message_id = int(poll_message_id)
			channel_id = int(channel_id)
			# these two will be used later
			time_now = int(time.time())
			extension_embed_message = None
			
			# # create a poll extension message if there should be one
			# if poll_extensions > 0:
			# 	embed_title = 'Extending Voting Time'
			# 	if poll_extensions == 1:
			# 		embed_description = f'The deadline for this poll has been extended by 1 hour.\n*Voting for this match will be extended until there are 15 or more votes, max {config.MAX_POLL_EXTENSIONS} extensions.*'
			# 	else:
			# 		embed_description = f'The deadline for this poll has been extended by {poll_extensions} hours.\n*Voting for this match will be extended until there are 15 or more votes, max {config.MAX_POLL_EXTENSIONS} extensions.*'
			# 	embed = await generate_embed('pink', embed_title, embed_description)
			# 	extension_embed_message = await message.channel.send(embed=embed)

			# # sleep for time remaining in poll
			# await asyncio.sleep(remaining_poll_time)
			# await action_log('waking back up in match channel and checking vote counts')
			# # check vote count
			# query = 'SELECT COUNT(*) FROM votes WHERE match_id = %s AND a_vote = True'
			# q_args = [db_id]
			# await execute_sql(query, q_args)
			# a_votes = connect.crsr.fetchone()[0]
			# query = 'SELECT COUNT(*) FROM votes WHERE match_id = %s AND b_vote = True'
			# q_args = [db_id]
			# await execute_sql(query, q_args)
			# b_votes = connect.crsr.fetchone()[0]
			# total_votes = a_votes + b_votes

			# while (total_votes < 15 or a_votes == b_votes) and poll_extensions < config.MAX_POLL_EXTENSIONS:
			# 	poll_extensions += 1
			# 	await action_log(f'only {total_votes} votes, extending poll time, this is extension number {poll_extensions}')

			# 	query = 'UPDATE matches SET poll_extensions = %s WHERE db_id = %s'
			#	q_args = [poll_extensions, db_id]
			# 	await execute_sql(query, q_args)
			# 	connect.conn.commit()
			# 	await action_log('poll extensions updated in database')

			# 	embed_title = 'Extending Voting Time'
			# 	if poll_extensions == 1:
			# 		embed_description = f'The deadline for this poll has been extended by 1 hour.\n*Voting for this match will be extended until there are 15 or more votes, max {config.MAX_POLL_EXTENSIONS} extensions.*'
			# 		embed = await generate_embed('pink', embed_title, embed_description)
			# 		extension_embed_message = await message.channel.send(embed=embed)
			# 	else:
			# 		embed_description = f'The deadline for this poll has been extended by {poll_extensions} hours.\n*Voting for this match will be extended until there are 15 or more votes, max {config.MAX_POLL_EXTENSIONS} extensions.*'
			# 		embed = await generate_embed('pink', embed_title, embed_description)
			# 		await extension_embed_message.edit(embed=embed)

			# 	# sleep for 1 hour (config.POLL_EXTENSION_TIME)
			# 	await asyncio.sleep(config.POLL_EXTENSION_TIME)
			# 	await action_log('waking back up in match channel and checking vote counts')
			# 	# check vote count
			# 	query = 'SELECT COUNT(*) FROM votes WHERE match_id = %s'
			#	q_args = [db_id]
			# 	await execute_sql(query, q_args)
			# 	total_votes = connect.crsr.fetchone()[0]

			# get the match channel
			match_channel = client.get_channel(channel_id)

			try:
				# fetch the poll message
				poll_message = await match_channel.fetch_message(poll_message_id)
				# clear poll messages from the channel
				await poll_message.delete()
				if extension_embed_message is not None:
					await extension_embed_message.delete()
			except:
				await action_log('could not find poll message')

			# check how many votes image A got
			query = 'SELECT COUNT(*) FROM votes WHERE match_id = %s AND a_vote = True'
			q_args = [db_id]
			await execute_sql(query, q_args)
			a_votes = connect.crsr.fetchone()[0]
			# check how many votes image B got
			query = 'SELECT COUNT(*) FROM votes WHERE match_id = %s AND b_vote = True'
			q_args = [db_id]
			await execute_sql(query, q_args)
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
				if (a_meme == 1 and winning_image == 'A') or (a_meme == 2 and winning_image == 'B'):
					winner = match_channel.guild.get_member(u1_id)
					winning_image_url = u1_image_url
					loser = match_channel.guild.get_member(u2_id)
				elif (a_meme == 2 and winning_image == 'A') or (a_meme == 1 and winning_image == 'B'):
					winner = match_channel.guild.get_member(u2_id)
					winning_image_url = u2_image_url
					loser = match_channel.guild.get_member(u1_id)
				elif winning_image == 'tie':
					# find participants' images
					if a_meme == 1:
						a_member = match_channel.guild.get_member(u1_id)
						b_member = match_channel.guild.get_member(u2_id)
					elif a_meme == 2:
						a_member = match_channel.guild.get_member(u2_id)
						b_member = match_channel.guild.get_member(u1_id)
					else:
						await action_log('winner not found or a_meme not defined in postgresql')
						return
					# build tie embed for match channel
					embed_title = 'Voting Results'
					embed_description = f'This match has ended in a {a_votes} - {b_votes} tie! {a_member.mention} submitted image A and {b_member.mention} submitted image B. Participants, please contact each other and find a time to rematch.'
					# for swiss-style tournaments:
					# embed_description = f'This match has ended in a {a_votes} - {b_votes} tie! {a_member.mention} submitted image A and {b_member.mention} submitted image B.'
					embed = await generate_embed('pink', embed_title, embed_description)
					await match_channel.send(embed=embed)
					await action_log('match ended in a tie, results sent in match channel')

					if not config.TESTING:
						# update participant stats in the databsee (tie)
						query = 'UPDATE participants SET total_votes_for = total_votes_for + %s, lb_points = lb_points + %s WHERE user_id = %s'
						q_args = [votes, votes * 2, u1_id]
						await execute_sql(query, q_args)
						connect.conn.commit()
						query = 'UPDATE participants SET total_votes_for = total_votes_for + %s, lb_points = lb_points + %s WHERE user_id = %s'
						q_args = [votes, votes * 2, u2_id]
						await execute_sql(query, q_args)
						connect.conn.commit()
						await action_log('participant stats updated')

					# build winner dm
					a_channel = await a_member.create_dm()
					b_channel = await b_member.create_dm()
					embed_title = 'Match Results - Tie'
					embed_description = f'Your match has ended in {match_channel.mention}, you have earned **{votes * 2} points** for the **{votes} votes** for your meme. Please contact your opponent for a rematch!'
					# for swiss-style tournaments:
					# embed_description = f'Your match has ended in {match_channel.mention}, you have earned **{votes * 2} points** for the **{votes} votes** for your meme.'
					embed = await generate_embed('pink', embed_title, embed_description)
					await a_channel.send(embed=embed)
					await action_log('a_member dm sent')
					await b_channel.send(embed=embed)
					await action_log('b_member dm sent')
					return
				else:
					await action_log('winner not found or a_meme not defined in postgresql')
					return
			except AttributeError:
				await action_log('member from existing match was not found in the guild')
				return

			if not config.TESTING:
				# # update winner's round role
				# i = 0
				# while i <= (len(config.ROUND_ROLE_IDS) - 1):
				# 	round_role = match_channel.guild.get_role(config.ROUND_ROLE_IDS[i])
				# 	if round_role in winner.roles:
				# 		# remove previous round role
				# 		await winner.remove_roles(round_role)
				# 		# check to see if winner is a finalist
				# 		if round_role.id == 634853736144961580:
				# 			# add winning role
				# 			await winner.add_roles(match_channel.guild.get_role(config.WINNER_ROLE_ID))
				# 		else:
				# 			# add next round role
				# 			await winner.add_roles(match_channel.guild.get_role(config.ROUND_ROLE_IDS[i + 1]))
				# 		i = len(config.ROUND_ROLE_IDS)
				# 	i += 1
				# await action_log('winner round role updated')

				# update participant stats in the database
				query = 'UPDATE participants SET total_matches = total_matches + 1, match_wins = match_wins + 1, total_votes_for = total_votes_for + %s, lb_points = lb_points + %s WHERE user_id = %s'
				q_args = [winning_votes, (winning_votes * 2) + 100, winner.id]
				await execute_sql(query, q_args)
				connect.conn.commit()
				await action_log('winner participant stats updated')
				query = 'UPDATE participants SET total_matches = total_matches + 1, match_losses = match_losses + 1, total_votes_for = total_votes_for + %s, lb_points = lb_points + %s WHERE user_id = %s'
				q_args = [losing_votes, losing_votes * 2, loser.id]
				await execute_sql(query, q_args)
				connect.conn.commit()
				await action_log('loser participant stats updated')

			# build notification embed for match channel (win/loss)
			embed_title = 'Voting Results'
			embed_description = f'Congratulations to {winner.mention}, you have won this match with image {winning_image}! Thank you for participating {loser.mention}. The final score was {a_votes} - {b_votes}.'
			embed = await generate_embed('pink', embed_title, embed_description)
			await match_channel.send(embed=embed)
			await action_log('voting results sent in match channel')

			if not config.TESTING:
				# build winning image embed for match archive
				embed_title = functions.escape_underscores(winner.display_name)
				embed_description = datetime.date.today().strftime("%B %d")
				embed_link = winning_image_url
				embed = await generate_embed('pink', embed_title, embed_description, attachment=embed_link)
				winning_meme_message = await client.get_channel(config.ARCHIVE_CHAN_ID).send(embed=embed)
				try:
					await winning_meme_message.add_reaction('<:GG:649057795643277342>')
					await winning_meme_message.add_reaction('<:imfine:645785769461547018>')
					await winning_meme_message.add_reaction('🏅')
					await winning_meme_message.add_reaction('🧠')
					await winning_meme_message.add_reaction('🔥')
				except:
					await action_log('winning image emojis broke')
				await action_log('winning image sent to archive channel')

			# check to see if challonge info is in the channel topic
			if match_channel.topic is not None:
				tournament_shortcut = match_channel.topic.split('/')[0]
				match_id = match_channel.topic.split('/')[1]
				player1_id = match_channel.topic.split('/')[2]
				player2_id = match_channel.topic.split('/')[3]

				# find player names from challonge
				player1_name = tourney_manager.show_participant(tournament_shortcut, player1_id)['name']
				player2_name = tourney_manager.show_participant(tournament_shortcut, player2_id)['name']

				# figure out which challonge player won
				if player1_name == winner.display_name:
					# player1 wins, 1-0
					scores_csv = '1-0'
					tourney_manager.set_match_winner(tournament_shortcut, int(match_id), scores_csv, int(player1_id))
					await action_log(f'{player1_name} set as match winner in challonge')
				elif player2_name == winner.display_name:
					# player2 wins, 0-1
					scores_csv = '0-1'
					tourney_manager.set_match_winner(tournament_shortcut, int(match_id), scores_csv, int(player2_id))
					await action_log(f'{player2_name} set as match winner in challonge')

			# build winner dm
			winner_channel = await winner.create_dm()
			embed_title = 'Match Results - Win'
			embed_description = f'Your match has ended in {match_channel.mention}, you have earned **100 points** for winning the match and **{winning_votes * 2} points** for the **{winning_votes} votes** for your meme.'
			embed = await generate_embed('pink', embed_title, embed_description)
			await winner_channel.send(embed=embed)
			await action_log('winner dm sent')

			# build loser dm
			loser_channel = await loser.create_dm()
			embed_title = 'Match Results - Loss'
			embed_description = f'Your match has ended in {match_channel.mention}, you have earned **{losing_votes * 2} points** for the {losing_votes} votes for your meme.'
			embed = await generate_embed('pink', embed_title, embed_description)
			await loser_channel.send(embed=embed)
			await action_log('loser dm sent')
			
			# update the match in the database
			query = 'UPDATE matches SET completed = True WHERE db_id = %s'
			q_args = [db_id]
			await execute_sql(query, q_args)
			connect.conn.commit()

	# check to see when the next poll is supposed to end
	query = 'SELECT poll_start_time FROM matches WHERE completed = False AND poll_start_time IS NOT NULL ORDER BY poll_start_time ASC LIMIT 1'
	await execute_sql(query)
	result = connect.crsr.fetchone()
	if result is None:
		sleep_time = config.BASE_POLL_TIME
	else:
		sleep_time = (int(result[0]) + config.BASE_POLL_TIME) - int(time.time()) + 5
	if sleep_time < 5:
		sleep_time = 5
	# sleep before looping again
	await action_log(f'{len(results)} polls ended, end_polls sleeping for {functions.time_string(sleep_time)}')
	await asyncio.sleep(sleep_time)

# make sure the client is ready before starting the end_polls task
@end_polls.before_loop
async def before_end_polls():
	await client.wait_until_ready()
	await action_log('starting end_polls task')

# client event triggers on any discord message
@client.event
async def on_message(message):
	# ignore bots
	if message.author.bot:
		# check messages from MadnessMod
		if message.author.id == client.user.id:
			if message.nonce == 'poll':
				# add reactions to match poll in match channel
				await message.add_reaction('🇦')
				await message.add_reaction('🇧')
				await action_log('added reactions to poll message')

				# pull the match data
				query = 'SELECT db_id, u1_id, u2_id FROM matches WHERE channel_id = %s ORDER BY db_id DESC'
				q_args = [message.channel.id]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				# initialize important variables
				db_id, u1_id, u2_id = result
				time_now = int(time.time())

				# set poll start time in the match database
				query = 'UPDATE matches SET poll_start_time = %s, poll_message_id = %s WHERE db_id = %s'
				q_args = [time_now, message.id, db_id]
				await execute_sql(query, q_args)
				connect.conn.commit()
				await action_log(f'poll_start_time set in database ({time_now})')

				if not config.TESTING:
					# set participants' unvoted_match_start_time to the current time (if not already set)
					query = 'UPDATE participants SET unvoted_match_start_time = %s WHERE unvoted_match_start_time IS NULL AND user_id != %s AND user_id != %s'
					q_args = [time_now, u1_id, u2_id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('unvoted_match_start_time set for valid participants')
				return

			if message.channel.id == config.TEMPLATE_CHAN_ID and message.nonce == 'template':
				# add reactions to messages in the #templates channel
				await message.add_reaction('👍')
				await message.add_reaction('🤷')
				await message.add_reaction('👎')

				# update signup info with the message_id
				query = 'UPDATE signups SET message_id = %s WHERE message_id = 0'
				q_args = [message.id]
				await execute_sql(query, q_args)
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
				if message.nonce.startswith('spltemp'):
					# add reactions to split template confirmations in #duel-mods
					await message.add_reaction('<:check_mark:637394596472815636>')
					await message.add_reaction('<:x_mark:637394622200676396>')
					return
			if len(message.embeds) == 1:
				if message.embeds[0].title == 'Mod Help Guide':
					await message.add_reaction('⚔️')
					await message.add_reaction('🏆')
					await message.add_reaction('📎')
					await message.add_reaction('↩️')
					return
				if message.embeds[0].title == 'Overall Points Leaderboard':
					await message.add_reaction('⬅️')
					await message.add_reaction('🔅')
					await message.add_reaction('➡️')
					return
			return
		# check messages from YAGPDB.xyz
		if message.author.id == 204255221017214977:
			# check to be sure the message has an embed
			if len(message.embeds) == 1:
				if message.embeds[0] is not None:
					# check to see if the message is from a CAH game
					if message.embeds[0].title == 'Pick the winner':
						# ping the card czar
						user_mention = message.embeds[0].description.split(', pick the best one(s) ')[1].split('! You have `')[0]
						await message.channel.send(f'{user_mention}, pick the winner!')
			return
		return

	# process and clean message content
	message_content = unidecode(message.content.casefold().strip())

	# this custom trigger is designed to remove '-whois' responses after 30 seconds
	if message_content.startswith('-whois') and message.guild.id == config.MM_GUILD_ID:
		# define message requirements (author is YAGPDB.xyz)
		def check(m):
			return m.author.id == 204255221017214977
		# wait for a message
		response_message = await client.wait_for('message', check=check, timeout=30)
		await action_log(f'\'-whois\' used by {message.author.display_name}')

		# sleep for 1 minute
		await asyncio.sleep(60)
		await response_message.delete()
		return

	# this will trigger when a Cards Against Humanity game is started in #off-topic using YAGPDG.xyz
	if message_content.startswith('-cah c') and message.channel.id == 639526660990828564:
		creator = False
		# iterate through all of the author's roles
		for role in message.author.roles:
			# check to see if the user has the CAH Creator role
			if role.id == 666305324244008960:
				creator = True

		if creator:
			# find the CAH Pings role
			cah_pings_role = message.guild.get_role(664238054260736040)
			# mention the CAH Pings role
			await message.channel.send(f'{cah_pings_role.mention} -  If this message didn\'t ping you and you want to get pinged for future CAH games, type `-role cah pings` in this channel!')
			await action_log('CAH Pings role notified')
		return

	# '.donate' command (all channels)
	if message_content == '.donate':
		# build donation embed
		embed_title = 'Donate to MadnessMod'
		embed_description = 'If you\'d like to donate to MadnessMod, please go to https://www.paypal.me/lukenamop\n\n100% of MadnessMod donations will go towards bot upkeep ($8 a month) and other Meme Madness fees.'
		embed = await generate_embed('pink', embed_title, embed_description)
		await message.channel.send(embed=embed)
		await action_log(f'donation info sent to {message.author.display_name}')
		return

	# '.stats' command (all channels)
	if message_content.startswith('.stats'):
		# check for a mentioned user
		if len(message.mentions) == 1:
			user = message.mentions[0]
		elif len(message_content.split()) == 2:
			user = message.guild.get_member_named(message.content.split()[1])
			if user is None:
				embed_title = 'No User Found'
				embed_description = f'\"{message_content.split()[1]}\" does not match the name of any member of this server. Please try again!'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('stats not able to be shared')
				return
		else:
			user = message.author

		# check participants database for the specified user
		query = 'SELECT total_matches, match_wins, match_losses, total_votes_for, avg_final_meme_time, templates_submitted, match_votes, longest_vote_streak FROM participants WHERE user_id = %s'
		q_args = [user.id]
		await execute_sql(query, q_args)
		results = connect.crsr.fetchone()
		if results is not None:
			# format the user's average time per meme
			if results[4] is not None:
				avg_time = strftime("%Mm %Ss", gmtime(results[4]))
			else:
				avg_time = 'N/A'
			# format the user's longest voting streak
			if results[7] == 1:
				voting_streak = '1 day'
			else:
				voting_streak = f'{results[7]} days'

			# build stats embed
			embed_title = f'Stats for {functions.escape_underscores(user.display_name)}'
			try:
				embed_description = f'**Total matches:** `{results[0]}`\n**Match wins/losses:** `{results[1]}/{results[2]}`\n**Win percentage:** `{round((float(results[1]) / float(results[0])) * 100)}%`\n**Total votes for your memes:** `{results[3]:,}`\n**Avg. time per meme:** `{avg_time}`\n**Templates submitted:** `{results[5]:,}`\n**Matches voted in:** `{results[6]:,}`\n**Longest voting streak:** `{voting_streak}`'
			except ZeroDivisionError:
				embed_description = f'**Total matches:** `{results[0]}`\n**Match wins/losses:** `{results[1]}/{results[2]}`\n**Win percentage:** `N/A`\n**Total votes for your memes:** `{results[3]:,}`\n**Avg. time per meme:** `{avg_time}`\n**Templates submitted:** `{results[5]:,}`\n**Matches voted in:** `{results[6]:,}`\n**Longest voting streak:** `{voting_streak}`'
			embed = await generate_embed('blue', embed_title, embed_description)
			nonce = f'stats{message.author.id}'
			await message.channel.send(embed=embed, nonce=nonce)
			await action_log(f'stats shared to {message.author.display_name}')
			return

		# if no record of specified user, build no-stats embed
		embed_title = 'No Stats Available'
		embed_description = f'{functions.escape_underscores(user.display_name)} needs to sign up for a tournament to start recording stats.'
		embed = await generate_embed('red', embed_title, embed_description)
		await message.channel.send(embed=embed)
		await action_log('stats not able to be shared')
		return

	# leaderboard commands (stats-flex channel only)
	if message.channel.id == 631239602736201728 or message.channel.id == 647495194018709534:
		# '.top10' command (stats-flex)
		if message_content.startswith('.top10') or message_content.startswith('.lb') or message_content.startswith('.leaderboard'):
			await action_log(f'{message.author.display_name} called .lb')
			# check for a mentioned user
			if len(message.mentions) == 1:
				user = message.mentions[0]
				await action_log(f'.lb was used on {user.display_name}')
			else:
				user = message.author

			# pull top participants
			query = 'SELECT user_id, lb_points, RANK () OVER (ORDER BY lb_points DESC) lb_rank FROM participants ORDER BY lb_points DESC'
			await execute_sql(query)
			results = connect.crsr.fetchall()
			embed_title = 'Overall Points Leaderboard'
			# check to make sure there are participants
			if results is not None:
				# build lb embed
				embed_description = 'Page 1:\n'
				iteration = 0
				user_found = False
				# iterate through the participants in the database
				for entry in results:
					# initialize variables for the member and their info
					member = message.guild.get_member(entry[0])
					lb_points = entry[1]
					lb_rank = entry[2]
					# check to be sure the member is still in the guild
					if member is not None:
						iteration += 1
						# 10 users printed and the base user was one of them
						if iteration > 10 and user_found:
							break
						# not 10 users printed yet
						elif iteration <= 10:
							if member == user:
								user_found = True
							embed_description += functions.format_lb_entry(1, lb_rank, member.display_name, lb_points)
						# 10 users printed but the base user hasn't been found yet
						else:
							if member == user:
								embed_description += '\nUser\'s rank:\n'
								user_found = True
								# add the user's rank at the bottom
								embed_description += functions.format_lb_entry(1, lb_rank, member.display_name, lb_points)
				# strip any extraneous newlines
				embed_description = embed_description.rstrip('\n')
			else:
				# send this message if no participants were found
				embed_description = 'The leaderboard seems to be empty in the database.'
			embed = await generate_embed('blue', embed_title, embed_description)
			# send signuplist embed
			lb_message = await message.channel.send(embed=embed)
			await action_log('leaderboard sent to stats-flex')
			return

		# '.points' command (stats-flex)
		if message_content == '.points':
			embed_title = 'Meme Madness Point System'
			embed_description = '**What are points?**\nPoints are a scoring system we use that is cumulative and separate from the individual tournaments.\n**How do I get points?**\nYou get 10 points for voting in a match, you get bonus points for voting multiple days in a row, and you get points for competing in matches.\n**What happens when I get lots of points?**\nNothing specific, you just get bragging rights! You can always check where you stand on the leaderboard by using `.leaderboard` or `.lb`. Have fun!'
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('.points used in #stats-flex')
			return

	# verification specific commands
	if message.channel.id == 581705191703838720 or message.channel.id == 607344923481473054:
		# '.verify' command (verification)
		if message_content.startswith('.verify'):
			verified = False
			display_name = message.author.display_name

			# save base info for duration of the verification process
			base_member = message.author
			base_message = message

			# build verification begin embed
			embed_title = 'Verification Process Started'
			embed_description = f'{base_member.mention}, please check your Discord messages for the next steps!'
			embed = await generate_embed('yellow', embed_title, embed_description)
			base_bot_response = await message.channel.send(embed=embed)
			await action_log(f'verification started by {display_name}')

			# build verification step 1/2 embed
			user_channel = await base_member.create_dm()
			embed_title = 'Verification Attempt (Step 1/2)'
			embed_description = 'Please send the name of your reddit account here:'
			embed = await generate_embed('yellow', embed_title, embed_description)
			try:
				await user_channel.send(embed=embed)
			except discord.errors.Forbidden:
				await base_bot_response.delete()
				embed_title = 'Verification Error'
				embed_description = f'{base_member.mention}, I\'m unable to send you DMs! Please check your Discord settings, in `Privacy & Safety`, and enable the `Allow direct messages from server members` option before trying again.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log(f'{display_name} has Discord DMs disabled')
				return

			# asyncio.TimeoutError triggers if client.wait_for(message) times out
			try:
				# define message requirements (DM message from specified user)
				def check(m):
					return m.channel == user_channel and m.author.id == base_member.id
				# wait for a message
				message = await client.wait_for('message', check=check, timeout=120)
				reddit_username = message.content.split('/')[-1].lstrip('@')
				await action_log(f'verification username shared by {display_name}')

				# generate random 6 character string excluding unwanted_chars
				unwanted_chars = ["0", "O", "l", "I"]
				char_choices = [char for char in string.ascii_letters if char not in unwanted_chars] + [char for char in string.digits if char not in unwanted_chars]
				verification_string = ''.join(random.choices(char_choices, k=6))

				# check to see which server is hosting the verification and set unique message
				if base_message.guild.id == 607342998497525808:
					# send message via reddit
					reddit_username = verify.send_message(reddit_username, verification_string, display_name, mex=True)
				elif base_message.guild.id == 581695290986332160:
					# send message via reddit
					reddit_username = verify.send_message(reddit_username, verification_string, display_name)
				else:
					return

				# verify that a username was shared
				if reddit_username is not None:
					await action_log(f'verification reddit message for {display_name} sent to \'{reddit_username}\'')

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
							if base_message.guild.id == 607342998497525808:
								# remove For Review on DEX
								del_role = base_message.guild.get_role(607365580567216130)
								await base_member.remove_roles(del_role)
							else:
								# add Verified on Meme Madness
								verified_role = base_message.guild.get_role(599354132771504128)
								await base_member.add_roles(verified_role)
							verified = True

						except discord.errors.Forbidden:
							# build access error embed
							embed_title = 'Access Error'
							embed_description = 'For some reason I don\'t have permission to assign roles. Please contact lukenamop#0918.'
							embed = await generate_embed('red', embed_title, embed_description)

						# DM embed to user
						await user_channel.send(embed=embed)

						# send a message to the #general channel welcoming the new user
						embed_title = 'New User Has Joined: ' + functions.escape_underscores(base_member.display_name)

						# check which server is hosting the verification
						if base_message.guild.id == 607342998497525808:
							# build welcome embed
							embed_description = f'{base_member.mention}, welcome to DEX! Please let a member of the mod team know if you need any help.'
							embed = await generate_embed('green', embed_title, embed_description)
							await client.get_channel(607342999751491585).send(embed=embed)
						elif base_message.guild.id == 581695290986332160:
							# build welcome embed
							announcements_chan = client.get_channel(config.ANNOUNCEMENTS_CHAN_ID)
							info_chan = client.get_channel(config.INFO_CHAN_ID)
							rules_chan = client.get_channel(config.RULES_CHAN_ID)
							embed_description = f'{base_member.mention}, welcome to Meme Madness! Signup info is always posted in {announcements_chan.mention}. Check out {info_chan.mention} and {rules_chan.mention} to see how this place is run and let a member of the mod team know if you need any help!'
							embed = await generate_embed('green', embed_title, embed_description)
							await client.get_channel(581695290986332162).send(embed=embed)
						# send welcome embed
						await action_log(f'verification compeleted by {display_name}')

						# check specific conditions related to the user's reddit account
						checks = verify.extra_checks(reddit_username)
						if checks[0] == 1 or checks[1] == 1 or checks[2] == 1:
							await action_log('redditor did not pass specific checks, report sending in #modlog')
							embed_title = f'New User {reddit_username} Joined: Low Activity'
							embed_description = f'This newly verified user has been flagged because their reddit account (https://reddit.com/u/{reddit_username}) has not met the following condition(s):\n'
							if checks[0] == 1:
								embed_description += '\n- Their account is less than 30 days old'
							if checks[1] == 1:
								embed_description += '\n- Their account has less than 1000 combined karma'
							if checks[2] == 1:
								embed_description += '\n- Their account does not have a verified email'
							embed = await generate_embed('red', embed_title, embed_description)
							await client.get_channel(581717461309718530).send(embed=embed)
							await action_log('report sent')
					else:
						# build verification failure embed (verification key error)
						embed_title = 'Verification Key Incorrect'
						if base_message.guild.id == 581695290986332160:
							embed_description = f'To try again, please send `.verify` in {client.get_channel(config.VERIFICATION_CHAN_ID).mention}.'
						else:
							embed_description = 'To try again, please send `.verify` in #verification.'
						embed = await generate_embed('red', embed_title, embed_description)
						await user_channel.send(embed=embed)
						await action_log(f'verification key incorrect from {display_name}')
				else:
					attempted_name = message.content.split('/')[-1]
					await action_log(f'verification username error for {display_name}, attempted name: {attempted_name}')
					# build verification failure embed (username error)
					embed_title = 'Username Error'
					if base_message.guild.id == 581695290986332160:
						embed_description = f'To try again, please send `.verify` in {client.get_channel(config.VERIFICATION_CHAN_ID).mention}.'
					else:
						embed_description = 'To try again, please send `.verify` in #verification.'
					embed = await generate_embed('red', embed_title, embed_description)
					await user_channel.send(embed=embed)
			except asyncio.TimeoutError:
				# build verification failure embed (timed out)
				embed_title = 'Verification Attempt Timed Out'
				if base_message.guild.id == 581695290986332160:
					embed_description = f'To try again, please send `.verify` in {client.get_channel(config.VERIFICATION_CHAN_ID).mention}.'
				else:
					embed_description = 'To try again, please send `.verify` in #verification.'
				embed = await generate_embed('red', embed_title, embed_description)
				await user_channel.send(embed=embed)
				await action_log(f'verification timed out for {display_name}')

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
			query = 'SELECT template_required, signups_open FROM settings WHERE guild_id = %s'
			q_args = [config.MM_GUILD_ID]
			await execute_sql(query, q_args)
			results = connect.crsr.fetchone()
			template_required = results[0]
			signups_open = results[1]

			# check to see if signups are open
			if not signups_open:
				embed_title = 'Signups Closed'
				embed_description = f'Signups are closed for the current tournament! Please try again when signups have opened again. To receive a notification when signups open, head to {client.get_channel(600355436033736714).mention} and give yourself the `Sign-Up Pings` role.'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log(f'signups closed, signup rejected from {message.author.display_name}')
				return
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
					await action_log(f'signup attempted without attachment by {message.author.display_name}')

					# asyncio.TimeoutError triggers if client.wait_for(message) times out
					try:
						# define message requirements (DM message from specified user)
						def check(m):
							return m.channel.type == message.channel.type and m.author.id == message.author.id and len(m.attachments) == 1
						# wait for a message
						message = await client.wait_for('message', check=check, timeout=120)
						await action_log(f'signup attachment received from {message.author.display_name}')
					except asyncio.TimeoutError:
						# build signup error embed (timed out)
						embed_title = 'Signup Timed Out'
						embed_description = 'If you\'d like to signup for this week\'s competition, send me another message with `.signup`!'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log(f'signup timed out by {message.author.display_name}')
						return
				else:
					await action_log(f'signup attachment received from {message.author.display_name}')

					# check to see if user has signed up in the last 7 days (config.CYCLE seconds)
					query = 'SELECT * FROM signups WHERE user_id = %s AND submission_time >= %s'
					q_args = [message.author.id, time.time() - config.CYCLE]
					await execute_sql(query, q_args)
					result = connect.crsr.fetchone()
					# don't create a new signup for previously signed up users
					if result is None:
						# build confirmation embed
						embed_title = 'Template Confirmation'
						embed_description = f'Thank you for submitting your template {message.author.mention}! If there are any issues with your entry you will be contacted.'
						embed = await generate_embed('green', embed_title, embed_description)
						await message.channel.send(embed=embed)

						# send template to #templates
						embed_title = 'Template Submission'
						embed_description = f'{member.mention} ({functions.escape_underscores(member.display_name)}, {member.id})'
						embed_link = message.attachments[0].url
						embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
						template_chan = client.get_channel(config.TEMPLATE_CHAN_ID)
						template_message = await template_chan.send(embed=embed, nonce='template')
						await action_log(f'signup attachment sent to #templates by {message.author.display_name}')

						# add signup info to postgresql
						query = 'INSERT INTO signups (user_id, message_id, submission_time) VALUES (%s, 0, %s)'
						q_args = [message.author.id, time.time()]
						await execute_sql(query, q_args)
						connect.conn.commit()
						await action_log('signup info added to postgresql')
					else:
						# build signup error embed (already signed up)
						embed_title = 'Error: Already Signed Up'
						embed_description = 'It looks like you\'ve already signed up for this cycle of Meme Madness! Contact a moderator if this is incorrect.'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log(f'already signed up from {message.author.display_name}')
						return
			else:
				# signup process when no template is required
				# check to see if user has signed up in the last 7 days (config.CYCLE seconds)
				query = 'SELECT * FROM signups WHERE user_id = %s AND submission_time >= %s'
				q_args = [message.author.id, time.time() - config.CYCLE]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				# don't create a new signup for previously signed up users
				if result is None:
					embed_title = 'Signup Confirmation'
					embed_description = f'Thank you for signing up {message.author.mention}! If there are any issues with your entry you will be contacted.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)

					# send signup to #templates
					embed_title = 'Signup Confirmed'
					embed_description = f'{member.mention} ({functions.escape_underscores(member.display_name)}, {member.id})'
					embed = await generate_embed('green', embed_title, embed_description)
					template_chan = client.get_channel(config.SIGNUP_CHAN_ID)
					template_message = await template_chan.send(embed=embed)
					await action_log(f'signup sent to #templates by {message.author.display_name}')

					# add signup info to postgresql
					query = 'INSERT INTO signups (user_id, message_id, submission_time) VALUES (%s, 0, %s)'
					q_args = [message.author.id, time.time()]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('signup info added to postgresql')
				else:
					# build signup error embed (already signed up)
					embed_title = 'Error: Already Signed Up'
					embed_description = 'It looks like you\'ve already signed up for this cycle of Meme Madness! Contact a moderator if this is incorrect.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log(f'already signed up from {message.author.display_name}')
					return

			# check for existing participant in database
			query = 'SELECT * FROM participants WHERE user_id = %s'
			q_args = [message.author.id]
			await execute_sql(query, q_args)
			if connect.crsr.fetchone() is None:
				# create participant if none exists
				query = 'INSERT INTO participants (user_id) VALUES (%s)'
				q_args = [message.author.id]
				await execute_sql(query, q_args)
				connect.conn.commit()
				await action_log('user added to participants table in postgresql')
			return

		# '.submit' command (DM)
		if message_content.startswith('.submit'):
			# check for an active match including the specified user
			query = 'SELECT u1_id, u2_id, u1_submitted, u2_submitted, channel_id, start_time, template_url, creation_time, db_id, template_author_id, cancelled FROM matches WHERE (u1_id = %s OR u2_id = %s) ORDER BY creation_time DESC'
			q_args = [message.author.id, message.author.id]
			await execute_sql(query, q_args)
			result = connect.crsr.fetchone()

			# build duplicate submission embed
			embed_title = 'Error: Already Submitted'
			embed_description = 'It looks like you\'ve already submitted for your current match! If this is incorrect, contact a moderator.'
			embed = await generate_embed('red', embed_title, embed_description)

			if result is not None:
				u1_id = result[0]
				u2_id = result[1]
				u1_submitted = result[2]
				u2_submitted = result[3]
				match_channel = client.get_channel(result[4])
				start_time = result[5]
				template_url = result[6]
				match_db_id = result[8]
				template_author_id = result[9]
				cancelled = result[10]
				try:
					template_author = client.get_guild(config.MM_GUILD_ID).get_member(template_author_id)
				except:
					await action_log('template_author was not a valid member')

				# check to see if the match has been cancelled
				if cancelled:
					# build submission error embed (match cancelled)
					embed_title = 'Match Cancelled'
					embed_description = 'Your match has been cancelled, please check the match channel for more info.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log(f'cancelled submission by {message.author.display_name}')
					return

				# check for duplicate submissions
				if message.author.id == u1_id:
					if u1_submitted:
						await message.channel.send(embed=embed)
						await action_log(f'duplicate submission by {message.author.display_name}')
						return
					u_order = 1
				elif message.author.id == u2_id:
					if u2_submitted:
						await message.channel.send(embed=embed)
						await action_log(f'duplicate submission by {message.author.display_name}')
						return
					u_order = 2
				# check for an attachment
				if len(message.attachments) != 1:
					# build submission embed
					embed_title = 'Submission Started'
					embed_description = 'Please send me your final meme to confirm your submission! This submission attempt will expire in 120 seconds.'
					embed = await generate_embed('yellow', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log(f'submission attempted without attachment by {message.author.display_name}')

					# asyncio.TimeoutError triggers if client.wait_for(message) times out
					try:
						# define message requirements (DM message from specified user)
						def check(m):
							return m.channel.type == message.channel.type and m.author.id == message.author.id and len(m.attachments) == 1
						# wait for a message
						message = await client.wait_for('message', check=check, timeout=120)
						await action_log(f'submission attachment received from {message.author.display_name}')
					except asyncio.TimeoutError:
						# build submission error embed (timed out)
						embed_title = 'Submission Timed Out'
						embed_description = 'If you\'d like to submit your final meme, send me another message with `.submit`!'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log(f'submission timed out by {message.author.display_name}')
						return
				else:
					await action_log(f'submission attachment received from {message.author.display_name}')

				# build submission confirmation embed
				embed_title = 'Submission Confirmation'
				embed_description = f'Thank you for submitting your final meme {message.author.mention}! If there are any issues with your submission you will be contacted.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log(f'final meme attachment sent in by {message.author.display_name}')

				if template_url is not None:
					# build submission confirmation for match channel
					embed_title = 'Solo Match Complete'
					embed_description = f'{message.author.mention} has completed their part of the match!'
					embed = await generate_embed('green', embed_title, embed_description)
					await match_channel.send(embed=embed)
					await action_log('match channel notified about splitmatch completion')

				# add submission info to postgresql database
				if u_order == 1:
					query = 'UPDATE matches SET u1_submitted = true, u1_image_url = %s WHERE db_id = %s'
					q_args = [message.attachments[0].url, match_db_id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('match info updated in postgresql')
				if u_order == 2:
					query = 'UPDATE matches SET u2_submitted = true, u2_image_url = %s WHERE db_id = %s'
					q_args = [message.attachments[0].url, match_db_id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('match info updated in postgresql')

				if not config.TESTING:
					# pull participant info from database
					query = 'SELECT avg_final_meme_time, total_matches FROM participants WHERE user_id = %s'
					q_args = [message.author.id]
					await execute_sql(query, q_args)
					results = connect.crsr.fetchone()
					# check to see if avg_final_meme_time exists
					if results[0] is None:
						new_avg_final_meme_time = time.time() - float(start_time)
					else:
						new_avg_final_meme_time = ((float(results[0] * results[1]) + (time.time() - float(start_time))) / float(results[1] + 1))
					# update participant stats in database
					query = 'UPDATE participants SET avg_final_meme_time = %s WHERE user_id = %s'
					q_args = [new_avg_final_meme_time, message.author.id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('participant stats updated')

				# pull match info from database
				query = 'SELECT u1_id, u2_id, u1_submitted, u2_submitted, u1_image_url, u2_image_url, channel_id, is_final FROM matches WHERE db_id = %s'
				q_args = [match_db_id]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				match_is_final = result[7]
				# find match_channel and submissions_channel from discord
				match_channel = client.get_channel(result[6])
				submissions_channel = client.get_channel(config.SUBMISSION_CHAN_ID)

				# if it's a split match, reset start_time
				if template_url is not None:
					query = 'UPDATE matches SET start_time = NULL WHERE db_id = %s'
					q_args = [match_db_id]
					await execute_sql(query, q_args)
					connect.conn.commit()

				# only execute if both users have submitted final memes
				if result[2] and result[3]:
					# reset start_time
					query = 'UPDATE matches SET start_time = NULL WHERE db_id = %s'
					q_args = [match_db_id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					# if it's a split match, send the template to the channel
					if template_url is not None:
						try:
							embed_title = 'Match Template'
							embed_description = f'Thanks to {template_author.mention} for the template!'
							embed = await generate_embed('green', embed_title, '', template_url)
							await match_channel.send(embed=embed)
							await action_log('template sent to split match channel')
						except:
							await action_log('template failed to send to channel')

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
						query = 'UPDATE matches SET a_meme = 1 WHERE db_id = %s'
						q_args = [match_db_id]
						await execute_sql(query, q_args)
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
						query = 'UPDATE matches SET a_meme = 2 WHERE db_id = %s'
						q_args = [match_db_id]
						await execute_sql(query, q_args)
						connect.conn.commit()

					# send final memes to #submissions channel
					# submission embed for user 1
					embed_title = 'Final Meme Submission'
					embed_description = f'{u1_mention} ({functions.escape_underscores(u1.display_name)}, {result[0]})'
					embed_link = u1_link
					embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
					await submissions_channel.send(embed=embed)
					# submission embed for user 2
					embed_description = f'{u2_mention} ({functions.escape_underscores(u2.display_name)}, {result[1]})'
					embed_link = u2_link
					embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
					await submissions_channel.send(embed=embed)
					await action_log('final memes sent to #submissions')

					# send final memes to match channel
					# submission embed for image A
					embed_description = 'Image A'
					embed_link = u1_link
					embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
					await match_channel.send(embed=embed)
					# submission embed for image B
					embed_description = 'Image B'
					embed_link = u2_link
					embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
					await match_channel.send(embed=embed)

					if match_is_final:
						verified_role = match_channel.guild.get_role(599354132771504128)
						await match_channel.send(f'Vote in the final! @everyone {verified_role.mention}')
					else:
						if not config.TESTING:
							# await match_channel.send('-mrole 705420253957718098 voting has started in a new match, come vote!')
							duel_mod_role = match_channel.guild.get_role(599996020171997206)
							await match_channel.send(f'Voting has started, please mention `Vote Pings` to let them know! {duel_mod_role.mention}')
						else:
							await match_channel.send('This is just a test match, not pinging `Vote Pings` or `here`.')

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
				await action_log(f'submission attempt without match by {message.author.display_name}')
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
				await action_log(f'template attempted without attachment by {message.author.display_name}')

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
					await action_log(f'template submission timed out by {message.author.display_name}')
					return

			await action_log(f'template attachment received from {message.author.display_name}')
			# build confirmation embed
			embed_title = 'Template Confirmation'
			embed_description = f'Thank you for submitting your template {message.author.mention}! If there are any issues, you will be contacted.'
			embed = await generate_embed('green', embed_title, embed_description)
			await message.channel.send(embed=embed)

			# send template to #templates
			embed_title = 'Voluntary Template Submission'
			embed_description = f'{member.mention} ({functions.escape_underscores(member.display_name)}, {member.id})'
			embed_link = message.attachments[0].url
			embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
			template_chan = client.get_channel(config.TEMPLATE_CHAN_ID)
			template_message = await template_chan.send(embed=embed, nonce='voluntary_template')
			await action_log(f'template attachment sent to #templates by {message.author.display_name}')

			if not config.TESTING:
				# check for existing participant in database
				query = 'SELECT templates_submitted FROM participants WHERE user_id = %s'
				q_args = [message.author.id]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				if result is None:
					# create participant if none exists
					query = 'INSERT INTO participants (user_id, templates_submitted) VALUES (%s, 1)'
					q_args = [message.author.id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('no existing user, new user added to participants table in postgresql')
				else:
					# update participant stats if they already exist
					query = 'UPDATE participants SET templates_submitted = %s WHERE user_id = %s'
					q_args = [result[0] + 1, message.author.id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('user already existed, participant stats updated in postgresql')
			return

		# '.mymatches' command (DM)
		if message_content == '.mymatches':
			await message.channel.trigger_typing()
			# build match embed
			embed_title = 'Your Active Matches'
			embed_description = ''
			match_category = client.get_channel(config.MATCH_CATEGORY_ID)
			for match_channel in match_category.text_channels:
				if match_channel.last_message_id is not None:
					try:
						last_message = await match_channel.fetch_message(match_channel.last_message_id)
					except:
						await action_log('ERROR - last_message_id was invalid')
						last_message = None

					if last_message is not None:
						if len(last_message.embeds) == 0 and len(last_message.mentions) == 2:
							if message.author.id == last_message.mentions[0].id or message.author.id == last_message.mentions[1].id:
								embed_description += f'{match_channel.mention}\n'
			embed_description.rstrip('\n')
			if embed_description == '':
				embed_description = 'No active matches found.'
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log(f'sent user matches to {message.author.display_name}')
			return

		# '.help' command (DM)
		if message_content == '.help':
			# build help embed
			embed_title = 'Help: Commands'
			embed_description = help_cmd.dm_help
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log(f'help query sent to {message.author.display_name}')
			return
		return

	# stats-flex specific commands
	if message.channel.id == 631239602736201728:
		# '.help' command (stats-flex)
		if message_content == '.help':
			# build help embed
			embed_title = 'Help: Commands'
			embed_description = help_cmd.stats_help
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log(f'help query sent to {message.author.display_name} in stats-flex')
			return
		return

	# duel-mods specific commands
	if message.channel.id == 600397545050734612 or message.channel.id == 581728812518080522:
		# '.activematches' command (duel-mods)
		if message_content == '.activematches':
			query = 'SELECT channel_id FROM matches WHERE start_time >= %s'
			q_args = [time.time() - (config.MATCH_TIME)]
			await execute_sql(query, q_args)
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
				embed_description += f'**Total active matches: `{total}`**'
			else:
				embed_description = '**Total active matches: `0`**'
			embed = await generate_embed('green', embed_title, embed_description)
			# send activematches embed
			await message.channel.send(embed=embed)
			await action_log('activematches sent to duel-mods')
			return

		# '.activepolls' command (duel-mods)
		if message_content == '.activepolls':
			query = 'SELECT channel_id, poll_start_time FROM matches WHERE poll_start_time IS NOT NULL AND completed = False'
			await execute_sql(query)
			results = connect.crsr.fetchall()
			embed_title = 'Active Polls'
			# check to make sure there are active polls
			if results is not None:
				# build activepolls embed
				embed_description = ''
				total = 0
				for poll in results:
					channel = client.get_channel(poll[0])
					if channel is not None:
						embed_description += channel.mention + '\n'
						total += 1
				embed_description += f'**Total active polls: `{total}`**'
			else:
				embed_description = '**Total active polls: `0`**'
			embed = await generate_embed('green', embed_title, embed_description)
			# send activepolls embed
			await message.channel.send(embed=embed)
			await action_log('activepolls sent to duel-mods')
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
				query = 'SELECT message_id FROM signups WHERE user_id = %s AND submission_time >= %s'
				q_args = [user_id, time.time() - config.CYCLE]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				if result is not None:
					# DM user to notify of resignup
					user_channel = client.get_user(user_id).dm_channel
					if user_channel is None:
						user_channel = await client.get_user(user_id).create_dm()

					# build resignup embed
					embed_title = 'Re-signup Required'
					embed_description = f'Your signup was removed for reason: `{reason}`. To enter this cycle of Meme Madness please `.signup` with a new template. If you have any questions please contact the moderators. Thank you!'
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
					query = 'DELETE FROM signups WHERE user_id = %s AND submission_time >= %s'
					q_args = [user_id, time.time() - config.CYCLE]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('signup info deleted')

					# build resignup confirmation embed
					embed_title = 'Signup Deleted'
					embed_description = f'{message.guild.get_member(user_id).mention}\'s signup has been deleted. I have sent them a DM including your reason for removing their signup and told them to `.signup` again if they\'d like to participate.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					return
				else:
					# build resignup error embed (no matching signup)
					embed_title = 'Error: No Matching Signup'
					embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `client.user.id`).'
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
				embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `client.user.id`).'
				embed = await generate_embed('red', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('non-int passed to resignup')
				return

		# '.signuplist' command (duel-mods)
		if message_content == '.signuplist' or message_content == '.signups':
			# pull all signups from database
			query = 'SELECT user_id FROM signups WHERE submission_time >= %s'
			q_args = [time.time() - config.CYCLE]
			await execute_sql(query, q_args)
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
				embed_description += f'**Total signups: `{total}`**'
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
				await action_log(f'{total_removed} roles removed')

				# pull all signups from database
				query = 'SELECT user_id FROM signups WHERE submission_time >= %s'
				q_args = [time.time() - config.CYCLE]
				await execute_sql(query, q_args)
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
					embed_description = f'Success! {total_removed} previous tournament roles removed, {total_added} new tournament roles added.'
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
				embed_description = f'Success! {total_removed} previous tournament roles removed.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log(f'{total_removed} roles removed')
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
							embed_description = f'The tournament role for {member.mention} has been set to `Preliminary`.'
							embed = await generate_embed('green', embed_title, embed_description)
							await message.channel.send(embed=embed)
							await action_log(f'prelim set for {member.display_name}')
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
						embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `client.user.id`).'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('no matching submission error with prelim')
						return
				except ValueError:
					# build prelim error embed (no matching signup)
					embed_title = 'Error: No Matching Signup'
					embed_description = 'Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `client.user.id`).'
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
				query = 'SELECT template_required FROM settings WHERE guild_id = %s'
				q_args = [config.MM_GUILD_ID]
				await execute_sql(query, q_args)
				results = connect.crsr.fetchone()
				template_required = results[0]
				if template_required:
					# set templates to no longer be required
					query = 'UPDATE settings SET template_required = False WHERE guild_id = %s'
					q_args = [config.MM_GUILD_ID]
					await execute_sql(query, q_args)
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
					query = 'UPDATE settings SET template_required = True WHERE guild_id = %s'
					q_args = [config.MM_GUILD_ID]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('templates now required')

					# build toggletemplates confirmation embed
					embed_title = 'Templates Enabled'
					embed_description = 'Templates are now required with `.signup`'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('template toggle confirmation')
					return

		# '.togglesignups'
		if message_content == '.togglesignups':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				await action_log('signups toggled')
				# check to see if templates are required
				query = 'SELECT signups_open FROM settings WHERE guild_id = %s'
				q_args = [config.MM_GUILD_ID]
				await execute_sql(query, q_args)
				results = connect.crsr.fetchone()
				signups_open = results[0]
				if signups_open:
					# set templates to no longer be required
					query = 'UPDATE settings SET signups_open = False WHERE guild_id = %s'
					q_args = [config.MM_GUILD_ID]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('signups no longer open')

					# build toggletemplates confirmation embed
					embed_title = 'Signups Closed'
					embed_description = 'Signups are now closed. To re-open, type `.togglesignups`.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('signups toggle confirmation')
					return
				else:
					# set templates to now be required
					query = 'UPDATE settings SET signups_open = True WHERE guild_id = %s'
					q_args = [config.MM_GUILD_ID]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('signups now open')

					# build toggletemplates confirmation embed
					embed_title = 'Signups Open'
					embed_description = 'Signups are now open. To close, type `.togglesignups`.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('signups toggle confirmation')

		# '.createbracket' command (duel-mods)
		if message_content.startswith('.createbracket '):
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# initialize some important variables
				bracket_number = message_content.split()[1]
				tournament_title = f'Meme Madness {bracket_number}'
				tournament_shortcut = f'mmcycle{bracket_number}'

				# send a confirmation embed
				embed_title = 'Creating Bracket...'
				embed_description = f'Creating a Challonge bracket called **{tournament_title}**.'
				embed = await generate_embed('yellow', embed_title, embed_description)
				conf_message = await message.channel.send(embed=embed)

				# pull all signups from database
				query = 'SELECT user_id FROM signups WHERE submission_time >= %s'
				q_args = [time.time() - config.CYCLE]
				await execute_sql(query, q_args)
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
					await action_log('challonge seeds shuffled')
					# send a final embed
					embed_title = 'Bracket Created'
					embed_description = f'Your bracket **{tournament_title}** has been created! Check it out here: https://challonge.com/{tournament_shortcut}'
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
				tournament_shortcut = f'mmcycle{message_content.split()[1]}'
				mm_guild = message.guild
				match_category = mm_guild.get_channel(config.MATCH_CATEGORY_ID)

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
						channel_name = 'match-' + str(match['suggested-play-order']) + '-' + participant1[:6] + '-v-' + participant2[:6]
						channel_topic = tournament_shortcut + '/' + str(match['id']) + '/' + str(match['player1-id']) + '/' + str(match['player2-id'])
						match_channel = await match_category.create_text_channel(channel_name, topic=channel_topic)
						member1 = match_channel.guild.get_member_named(participant1)
						member2 = match_channel.guild.get_member_named(participant2)
						if member1 is None:
							await match_channel.send(f'Please DM each other to find a 30 minute window to complete your match. When you\'re both available, @ mention Duel Mods in {message.guild.get_channel(config.GENERAL_CHAN_ID).mention}. Good luck!\n@{participant1} {member2.mention}')
						elif member2 is None:
							await match_channel.send(f'Please DM each other to find a 30 minute window to complete your match. When you\'re both available, @ mention Duel Mods in {message.guild.get_channel(config.GENERAL_CHAN_ID).mention}. Good luck!\n{member1.mention} @{participant2}')
						else:
							await match_channel.send(f'Please DM each other to find a 30 minute window to complete your match. When you\'re both available, @ mention Duel Mods in {message.guild.get_channel(config.GENERAL_CHAN_ID).mention}. Good luck!\n{member1.mention} {member2.mention}')
						total_created += 1
						if config.TESTING:
							break

				# check to see if any matches were created
				if total_created > 0:
					embed_title = 'Channel Creation Complete'
					embed_description = f'A total of {total_created} channels were created!'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log(f'channel creation complete - {total_created} open matches')
					await conf_message.delete()
				else:
					embed_title = 'No Channels Created'
					embed_description = 'There were no open matches in the specified tournament. Please try again with a different tournament reference.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('no open matches in tournament')
					await conf_message.delete()
			return

		# '.deletematchchannels' command (duel-mods)
		if message_content == '.deletematchchannels':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				await action_log('attempting to delete match channels')
				match_category = message.guild.get_channel(config.MATCH_CATEGORY_ID)

				# send a confirmation embed
				embed_title = 'Deleting Match Channels...'
				embed_description = 'Deleting any match channels.'
				embed = await generate_embed('yellow', embed_title, embed_description)
				conf_message = await message.channel.send(embed=embed)

				total_deleted = 0
				for channel in match_category.text_channels:
					if bool(re.match('^(match-\d+-.+)$', channel.name)):
						await channel.delete()
						total_deleted += 1

				if total_deleted > 0:
					embed_title = 'Channel Deletion Complete'
					embed_description = f'A total of {total_deleted} channels were deleted!'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log(f'channel deletion complete - {total_deleted} channels')
					await conf_message.delete()
				else:
					embed_title = 'No Channels Deleted'
					embed_description = 'There were no channels to delete.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('no channels to delete')
					await conf_message.delete()
			return

		# # '.clearparticipantstats' command (duel-mods)
		# if message_content == '.clearparticipantstats':
		# 	# check to be sure only admin user uses command
		# 	if message.author.id in config.ADMIN_IDS:
		# 		# set participant stats to defaults in database
		# 		query = 'UPDATE participants SET total_matches = DEFAULT, match_wins = DEFAULT, match_losses = DEFAULT, total_votes_for = DEFAULT, avg_final_meme_time = DEFAULT'
		# 		await execute_sql(query)
		# 		connect.conn.commit()

		# 		# build clearparticipantstats confirmation embed
		# 		embed_title = 'Participant Stats Cleared'
		# 		embed_description = 'All participant stats were cleared from the database.'
		# 		embed = await generate_embed('green', embed_title, embed_description)
		# 		await message.channel.send(embed=embed)
		# 		await action_log('participant stats cleared by duel-mods')
		# 		return
		# 	return

		# # '.clearlbpoints' command (duel-mods)
		# if message_content == '.clearlbpoints':
		# 	# check to be sure only admin user uses command
		# 	if message.author.id in config.ADMIN_IDS:
		# 		# reset participant lb_points to default in database
		# 		query = 'UPDATE participants SET lb_points = DEFAULT'
		# 		await execute_sql(query)
		# 		connect.conn.commit()

		# 		# build clearlbpoints confirmation embed
		# 		embed_title = 'Leaderboard Points Reset'
		# 		embed_description = 'All participants\' leaderboard points were cleared from the database.'
		# 		embed = await generate_embed('green', embed_title, embed_description)
		# 		await message.channel.send(embed=embed)
		# 		await action_log('leaderboard points cleared by duel-mods')
		# 		return
		# 	return

		# '.clearsignups' command (duel-mods)
		if message_content == '.clearsignups':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				# delete all rows from signups database
				query = 'DELETE FROM signups'
				await execute_sql(query)
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
				await execute_sql(query)
				connect.conn.commit()
				# delete all rows from votes database
				query = 'DELETE FROM votes'
				await execute_sql(query)
				connect.conn.commit()

				# build clearmatches confirmation embed
				embed_title = 'Matches Cleared'
				embed_description = 'All matches and votes were cleared from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log('matches and votes cleared by duel-mods')
				return
			return

		# '.removeinvalidparticipants' command (duel-mods)
		if message_content == '.removeinvalidparticipants':
			# check to be sure only admin user uses command
			if message.author.id in config.ADMIN_IDS:
				query = 'SELECT user_id FROM participants'
				await execute_sql(query)
				results = connect.crsr.fetchall()
				total = 0
				for result in results:
					user = message.guild.get_member(result[0])
					if user is None:
						query = f'DELETE FROM participants WHERE user_id = %s'
						q_args = [result[0]]
						await execute_sql(query, q_args)
						connect.conn.commit()
						total += 1
				if total == 0:
					embed_title = 'No Invalid Participants'
					embed_description = 'There were no invalid participants to remove.'
				else:
					embed_title = 'Participants Removed'
					embed_description = f'{total} users in the database are no longer in this server. They have been removed from the database.'
				embed = await generate_embed('green', embed_title, embed_description)
				await message.channel.send(embed=embed)
				await action_log(f'{total} invalid participants removed from the participants table')
				return
			return

		# '.remindparticipants' command (DM)
		if message_content == '.remindparticipants':
			await message.channel.trigger_typing()
			# build alert embed
			embed_title = 'Participants Reminded'
			alerted = 0
			match_category = client.get_channel(config.MATCH_CATEGORY_ID)
			for match_channel in match_category.text_channels:
				if match_channel.last_message_id is not None:
					try:
						last_message = await match_channel.fetch_message(match_channel.last_message_id)
					except:
						await action_log('last_message_id was invalid')
						last_message = None

					if last_message is not None:
						if len(last_message.embeds) == 0 and len(last_message.mentions) == 2:
							member1 = last_message.mentions[0]
							member2 = last_message.mentions[1]

							await match_channel.send(f'Friendly reminder to complete this match! If you haven\'t been able to line up your availability, you should plan on doing a split match. To complete a split match, @ mention Duel Mods in {message.guild.get_channel(config.GENERAL_CHAN_ID).mention} when you have 30 minutes free.\n{member1.mention} {member2.mention}')
							alerted += 1
						elif len(last_message.embeds) == 1:
							if last_message.embeds[0].title == 'Solo Match Complete':
								match_channel_messages = await match_channel.history(limit=100).flatten()
								member1 = match_channel_messages[-1].mentions[0]
								member2 = match_channel_messages[-1].mentions[1]

								completed_member_id = last_message.embeds[0].description.split('<@')[1].split('>')[0]
								if member1.id == completed_member_id:
									await match_channel.send(f'Friendly reminder to complete this match! It looks like your opponent has already completed their side of a split match. To complete your half, @ mention Duel Mods in {message.guild.get_channel(config.GENERAL_CHAN_ID).mention} when you have 30 minutes free.\n{member2.mention}')
									alerted += 1
								elif member2.id == completed_member_id:
									await match_channel.send(f'Friendly reminder to complete this match! It looks like your opponent has already completed their side of a split match. To complete your half, @ mention Duel Mods in {message.guild.get_channel(config.GENERAL_CHAN_ID).mention} when you have 30 minutes free.\n{member1.mention}')
									alerted += 1
								else:
									await message.channel.send(f'{message.guild.get_member(config.ADMIN_IDS[0]).mention} there was an error reminding a member of a split match: {completed_member_id}')
			embed_description = f'Participants in `{alerted}` match(es) have been alerted.'
			embed = await generate_embed('green', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log(f'alerted unfinished match participants')
			return

		# '.dbstats' command (duel-mods)
		if message_content == '.dbstats':
			return

		# '.help' command (duel-mods)
		if message_content == '.help':
			# build base embed
			embed_title = 'Mod Help Guide'
			embed_description = """Use the emojis to navigate this help guide:
				\n⚔️ Match Commands
				\n🏆 Tournament Commands
				\n📎 Admin Commands
				\n↩️ Return Here"""
			embed = await generate_embed('yellow', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('mod help guide sent to #duel-mods')
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

				# check for an active match including the specified user
				query = 'SELECT start_time FROM matches WHERE (u1_id = %s OR u2_id = %s OR u1_id = %s OR u2_id = %s) ORDER BY start_time DESC'
				q_args = [member1.id, member1.id, member2.id, member2.id]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				if result is not None:
					if result[0] is not None:
						embed_title = 'Match already in progress'
						embed_description = 'Competitors, please complete your other active matches before starting a new one.'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						return

				embed_title = 'Starting Match'
				embed_description = 'Randomly selecting template...'
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)

				# gather list of all valid templates
				template_list = await client.get_channel(config.TEMPLATE_CHAN_ID).history(limit=500).flatten()
				await action_log(f'list of {len(template_list)} templates compiled from #templates')
				duelmods_chan = client.get_channel(config.DUELMODS_CHAN_ID)

				# loop through until a valid template is found
				found_template = False
				iteration = 0
				while (not found_template) and iteration >= 0:
					iteration = iteration + 1
					# don't allow an infinite loop
					if iteration >= 50:
						embed_title = 'No Valid Template'
						embed_description = 'Template search stopped after iterating through 50 templates. Please try again.'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('50 templates searched, no valid template found, stopping while loop')
						return

					# check to make sure there is at least one template in the list
					if len(template_list) >= 1:
						template_message = random.choice(template_list)
						# initiate reaction-related variables
						ups = 0
						shrugs = 0
						downs = 0
						if len(template_message.reactions) >= 1:
							for reaction in template_message.reactions:
								# count relevant reactions (subtract 1 so that bot reactions aren't counted)
								if reaction.emoji == '👍':
									ups = reaction.count - 1
								elif reaction.emoji == '🤷':
									shrugs = reaction.count - 1
								elif reaction.emoji == '👎':
									downs = reaction.count - 1
						# check to see if the template is quality
						if ups >= 2 and downs <= 1:
							if len(template_message.embeds) == 1:
								template_url = template_message.embeds[0].image.url
								template_author = message.guild.get_member(int(template_message.embeds[0].description.split(' (')[0].lstrip('<@').lstrip('!').rstrip('>')))
							else:
								template_url = template_message.attachments[0].url
								template_author = template_message.author

							# if the template author is neither of the match members, break out of the loop
							if not (member1.mention == template_author.mention or member2.mention == template_author.mention):
								found_template = True

					# trigger this if there are no templates
					else:
						# build startmatch error (no templates)
						embed_title = 'Match Error'
						embed_description = 'No templates in #templates!'
						embed = await generate_embed('red',embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('no templates for .startmatch')
						return

				# check if match is final
				query = 'SELECT next_match_is_final FROM settings WHERE guild_id = %s'
				q_args = [config.MM_GUILD_ID]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				match_is_final = result[0]

				# add match info to postgresql
				query = 'INSERT INTO matches (u1_id, u2_id, channel_id, template_message_id, creation_time, is_final) VALUES (%s, %s, %s, %s, %s, %s)'
				q_args = [member1.id, member2.id, channel_id, template_message.id, time.time(), match_is_final]
				await execute_sql(query, q_args)
				connect.conn.commit()
				await action_log('match added to database')

				if match_is_final:
					# reset guild final settings
					query = 'UPDATE settings SET next_match_is_final = False WHERE guild_id = %s'
					q_args = [config.MM_GUILD_ID]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('current match set as final, guild settings reset')

				# build random template embed
				embed_title = f'Template for #{message.channel.name}'
				embed_description = f'Here\'s a random template! This template was submitted by {template_author.display_name}'
				embed = await generate_embed('green', embed_title, embed_description, attachment=template_url)
				nonce = f'tempcon{channel_id}'
				await duelmods_chan.send(embed=embed, nonce=nonce)
				await duelmods_chan.send(message.author.mention)
				await action_log('template confirmation sent to duel-mods')
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

				embed_title = 'Splitting Match'
				embed_description = 'Randomly selecting template...'
				embed = await generate_embed('yellow', embed_title, embed_description)
				await message.channel.send(embed=embed)

				template_list = await client.get_channel(config.TEMPLATE_CHAN_ID).history(limit=200).flatten()
				await action_log(f'list of {len(template_list)} templates compiled from #templates')
				duelmods_chan = client.get_channel(config.DUELMODS_CHAN_ID)

				# loop through until a valid template is found
				found_template = False
				iteration = 0
				while (not found_template) and iteration >= 0:
					iteration = iteration + 1
					# don't allow an infinite loop
					if iteration >= 50:
						embed_title = 'No Valid Template'
						embed_description = 'Template search stopped after iterating through 50 templates. Please try again.'
						embed = await generate_embed('red', embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('50 templates searched, no valid template found, stopping while loop')
						return

					# check to make sure there is at least one template in the list
					if len(template_list) >= 1:
						template_message = random.choice(template_list)
						if len(template_message.embeds) == 1:
							template_url = template_message.embeds[0].image.url
							template_author = message.guild.get_member(int(template_message.embeds[0].description.split(' (')[0].lstrip('<@').lstrip('!').rstrip('>')))
						else:
							template_url = template_message.attachments[0].url
							template_author = template_message.author

						# if the template author is neither of the match members, break out of the loop
						if not (member1 == template_author or member2 == template_author):
							found_template = True

					# trigger this if there are no templates
					else:
						# build startmatch error (no templates)
						embed_title = 'Match Error'
						embed_description = 'No templates in #templates!'
						embed = await generate_embed('red',embed_title, embed_description)
						await message.channel.send(embed=embed)
						await action_log('no templates for .startmatch')
						return

				# check if match is final
				query = 'SELECT next_match_is_final FROM settings WHERE guild_id = %s'
				q_args = [config.MM_GUILD_ID]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				match_is_final = result[0]

				# add match info to postgresql
				query = 'INSERT INTO matches (u1_id, u2_id, channel_id, creation_time, template_message_id, is_final) VALUES (%s, %s, %s, %s, %s, %s)'
				q_args = [member1.id, member2.id, channel_id, time.time(), template_message.id, match_is_final]
				await execute_sql(query, q_args)
				connect.conn.commit()
				await action_log('match added to database')

				# build random template embed
				embed_title = f'Template for #{message.channel.name}'
				embed_description = f'Here\'s a random template! This template was submitted by {template_author.display_name}'
				embed = await generate_embed('green', embed_title, embed_description, attachment=template_url)
				nonce = f'spltemp{channel_id}'
				await duelmods_chan.send(embed=embed, nonce=nonce)
				await duelmods_chan.send(message.author.mention)
				await action_log(f'template confirmation sent to duel-mods (took {iteration} iterations)')
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

				query = 'SELECT creation_time, u1_id, u2_id, u1_submitted, u2_submitted, template_url, start_time FROM matches WHERE channel_id = %s ORDER BY db_id DESC'
				q_args = [channel_id]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()

				if result is not None:
					failed = False
				else:
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
						submitted = 'u1_submitted'
						await action_log('match and participant found')
						# return if there is a start_time but the other user has not yet submitted
						if result[6] is not None and not result[4]:
							embed_title = 'Match In Progress...'
							embed_description = 'Please wait for the other participant to finish their part of the match!'
							embed = await generate_embed('red', embed_title, embed_description)
							await message.channel.send(embed=embed)
							await action_log('split match already in progress')
							return
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
						submitted = 'u2_submitted'
						await action_log('match and participant found')
						# return if there is a start_time but the other user has not yet submitted
						if result[6] is not None and not result[3]:
							embed_title = 'Match In Progress...'
							embed_description = 'Please wait for the other participant to finish their part of the match!'
							embed = await generate_embed('red', embed_title, embed_description)
							await message.channel.send(embed=embed)
							await action_log('split match already in progress')
							return
					else:
						# failed is true if the mentioned user is not "u1" or "u2"
						failed = True

				# verify that an existing match was found
				if not failed:
					template_url = result[5]
					u_channel = await match_user.create_dm()

					if template_url is not None:
						# update match start_time in database
						query = 'UPDATE matches SET start_time = %s WHERE channel_id = %s AND template_message_id IS NULL AND template_url = %s'
						q_args = [time.time(), channel_id, template_url]
						await execute_sql(query, q_args)
						connect.conn.commit()
						await action_log('match start_time updated in database')

						# send notifying DMs to participant
						embed_title = 'Match Started'
						embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Here is your template:'
						embed = await generate_embed('yellow', embed_title, embed_description, attachment=template_url)
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
							await action_log('participant has DMs turned off')
							return

						# send template to match channel
						embed_title = 'Match Started'
						embed_description = f'{match_user.mention} has 30 minutes to hand in their final meme. Good luck!'
						embed = await generate_embed('green', embed_title, embed_description)
						await match_channel.send(embed=embed)
						await action_log(f'solo match started for {match_user.display_name}')

						# sleep for 15 minutes (config.MATCH_WARN1_TIME seconds)
						await asyncio.sleep(config.MATCH_WARN1_TIME)

						await action_log('checking submission status')
						# check for submissions, remind users to submit if they haven't yet
						query = f'SELECT {submitted}, cancelled FROM matches WHERE {match_udb} = %s ORDER BY db_id DESC'
						q_args = [match_user.id]
						await execute_sql(query, q_args)
						results = connect.crsr.fetchone()
						if results[1]:
							return
						if results[0] is not None:
							if results[0]:
								await action_log('user already submitted')
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
						query = f'SELECT {submitted}, cancelled FROM matches WHERE {match_udb} = %s ORDER BY db_id DESC'
						q_args = [match_user.id]
						await execute_sql(query, q_args)
						results = connect.crsr.fetchone()
						if results[1]:
							return
						if results[0] is not None:
							if results[0]:
								await action_log('user already submitted')
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
						query = f'SELECT {submitted}, cancelled FROM matches WHERE {match_udb} = %s ORDER BY db_id DESC'
						q_args = [match_user.id]
						await execute_sql(query, q_args)
						results = connect.crsr.fetchone()
						if results[1]:
							return
						if results[0] is not None:
							if results[0]:
								await action_log('user already submitted')
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
						embed_description = f'{match_user.mention} has missed their submission deadline.'
						embed2 = await generate_embed('red', embed_title, embed_description)
						await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
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

		# '.forcewin' command (contest category)
		if message_content == '.forcewin':
			await action_log('forcewin command in match channel')
			# check to see who has submitted
			query = 'SELECT db_id, u1_id, u1_submitted, u1_image_url, u2_id, u2_submitted, u2_image_url FROM matches WHERE channel_id = %s'
			q_args = [message.channel.id]
			await execute_sql(query, q_args)
			result = connect.crsr.fetchone()

			if result is not None:
				db_id = result[0]
				u1_id = result[1]
				u1_submitted = result[2]
				u1_image_url = result[3]
				u2_id = result[4]
				u2_submitted = result[5]
				u2_image_url = result[6]
				forced = False

				if u1_submitted and not u2_submitted:
					forced = True
					await action_log('giving the win to user 1')
					winner = message.guild.get_member(u1_id)
					winning_image_url = u1_image_url
				if u2_submitted and not u1_submitted:
					forced = True
					await action_log('giving the win to user 2')
					winner = message.guild.get_member(u2_id)
					winning_image_url = u2_image_url

				if forced:
					# build winning image embed for match archive
					embed_title = 'Final Meme Submission'
					embed_description = functions.escape_underscores(winner.display_name)
					embed_link = winning_image_url
					embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
					await message.channel.send(embed=embed)
					await action_log('image sent to match channel')

					# build notification embed for match channel (win/loss)
					embed_title = 'Match Results'
					embed_description = f'Congratulations to {winner.mention}, you have won this match! Good luck in the next round.'
					embed = await generate_embed('pink', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('match results sent in match channel')

					if not config.TESTING:
						# build winning image embed for match archive
						embed_title = functions.escape_underscores(winner.display_name)
						embed_description = datetime.date.today().strftime("%B %d")
						embed_link = winning_image_url
						embed = await generate_embed('pink', embed_title, embed_description, attachment=embed_link)
						await client.get_channel(config.ARCHIVE_CHAN_ID).send(embed=embed)
						await action_log('winning image sent to archive channel')

						# update participant stats in the database
						query = 'UPDATE participants SET total_matches = total_matches + 1, match_wins = match_wins + 1, lb_points = lb_points + 100 WHERE user_id = %s'
						q_args = [winner.id]
						await execute_sql(query, q_args)
						connect.conn.commit()
						await action_log('winner participant stats updated')

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

					# check to see if challonge info is in the channel topic
					if message.channel.topic is not None:
						tournament_shortcut = message.channel.topic.split('/')[0]
						match_id = message.channel.topic.split('/')[1]
						player1_id = message.channel.topic.split('/')[2]
						player2_id = message.channel.topic.split('/')[3]

						# find player names from challonge
						player1_name = tourney_manager.show_participant(tournament_shortcut, player1_id)['name']
						player2_name = tourney_manager.show_participant(tournament_shortcut, player2_id)['name']

						# figure out which challonge player won
						if player1_name == winner.display_name:
							# player1 wins, 1-0
							scores_csv = '1-0'
							tourney_manager.set_match_winner(tournament_shortcut, int(match_id), scores_csv, int(player1_id))
							await action_log(f'{player1_name} set as match winner in challonge')
						elif player2_name == winner.display_name:
							# player2 wins, 0-1
							scores_csv = '0-1'
							tourney_manager.set_match_winner(tournament_shortcut, int(match_id), scores_csv, int(player2_id))
							await action_log(f'{player2_name} set as match winner in challonge')
					return
				else:
					await action_log('not able to force a win in the found match')
				return
			else:
				await action_log('no match found')
			return

		# '.cancelmatch' command (contest category)
		if message_content == '.cancelmatch':
			# update match in postgresql
			query = 'UPDATE matches SET cancelled = True WHERE channel_id = %s'
			q_args = [message.channel.id]
			await execute_sql(query, q_args)
			connect.conn.commit()
			await action_log('cancelled match in database')

			# send cancelled embed to match channel
			embed_title = 'Match Cancelled'
			embed_description = 'This match has been cancelled. To start a new match, use `.startmatch` or `.startsolo`.'
			embed = await generate_embed('red', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('match channel notified of cancellation')
			return

		# '.showresults' command (contest category)
		if message_content == '.showresults':
			await action_log('showresults command in match channel')
			# check to see who submitted each meme
			query = 'SELECT db_id, u1_id, u2_id, a_meme, creation_time FROM matches WHERE channel_id = %s'
			q_args = [message.channel.id]
			await execute_sql(query, q_args)
			results = connect.crsr.fetchall()
			if len(results) > 1:
				result = [0, 0, 0, 0, 0]
				# find the most recent match by creation_time
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
			query = 'SELECT COUNT(*) FROM votes WHERE match_id = %s AND a_vote = True'
			q_args = [result[0]]
			await execute_sql(query, q_args)
			a_votes = connect.crsr.fetchone()[0]
			# check how many votes image B got
			query = 'SELECT COUNT(*) FROM votes WHERE match_id = %s AND b_vote = True'
			q_args = [result[0]]
			await execute_sql(query, q_args)
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
					embed_description = f'This match has ended in a {a_votes} - {b_votes} tie! Participants, please contact each other and find a time to rematch.'
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
			embed_description = f'Congratulations to {winner.mention}, you have won this match with image {winning_image}! Thank you for participating {loser.mention}. The final score was {a_votes} - {b_votes}.'
			embed = await generate_embed('pink', embed_title, embed_description)
			await message.channel.send(embed=embed)
			await action_log('voting results sent in match channel')
			return

		# '.forcepoll' command (contest category)
		if message_content.startswith('.forcepoll '):
			u_order = int(message_content.split()[1])
			query = 'SELECT u1_id, u2_id, u1_submitted, u2_submitted, u1_image_url, u2_image_url, channel_id, is_final, db_id FROM matches WHERE channel_id = %s ORDER BY db_id DESC'
			q_args = [message.channel.id]
			await execute_sql(query, q_args)
			result = connect.crsr.fetchone()
			match_is_final = result[7]
			if u_order == 1:
				try:
					# set user order
					u1 = message.channel.guild.get_member(result[0])
					u1_mention = u1.mention
					u1_link = result[4]
					u2 = message.channel.guild.get_member(result[1])
					u2_mention = u2.mention
					u2_link = result[5]
				except AttributeError:
					await action_log('final meme submission stopped due to an AttributeError')
					return
				# update match info in database
				query = 'UPDATE matches SET a_meme = 1 WHERE db_id = %s'
				q_args = [result[8]]
				await execute_sql(query, q_args)
				connect.conn.commit()
			if u_order == 2:
				try:
					# ser user order
					u1 = message.channel.guild.get_member(result[1])
					u1_mention = u1.mention
					u1_link = result[5]
					u2 = message.channel.guild.get_member(result[0])
					u2_mention = u2.mention
					u2_link = result[4]
				except AttributeError:
					await action_log('final meme submission stopped due to an AttributeError')
					return
				# update match info in database
				query = 'UPDATE matches SET a_meme = 2 WHERE db_id = %s'
				q_args = [result[8]]
				await execute_sql(query, q_args)
				connect.conn.commit()

			# send final memes to #submissions channel
			submissions_channel = message.guild.get_channel(config.SUBMISSION_CHAN_ID)
			# submission embed for user 1
			embed_title = 'Final Meme Submission'
			embed_description = f'{u1_mention} ({functions.escape_underscores(u1.display_name)}, {result[0]})'
			embed_link = u1_link
			embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
			await submissions_channel.send(embed=embed)
			# submission embed for user 2
			embed_description = f'{u2_mention} ({functions.escape_underscores(u2.display_name)}, {result[1]})'
			embed_link = u2_link
			embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
			await submissions_channel.send(embed=embed)
			await action_log('final memes sent to #submissions')

			# send final memes to match channel
			# submission embed for image A
			embed_description = 'Image A'
			embed_link = u1_link
			embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
			await message.channel.send(embed=embed)
			# submission embed for image B
			embed_description = 'Image B'
			embed_link = u2_link
			embed = await generate_embed('green', embed_title, embed_description, attachment=embed_link)
			await message.channel.send(embed=embed)

			if match_is_final:
				verified_role = message.channel.guild.get_role(599354132771504128)
				await message.channel.send(f'Vote in the final! @everyone {verified_role.mention}')
			else:
				if not config.TESTING:
					# await message.channel.send('-mrole 705420253957718098 voting has started in a new match, come vote!')
					duel_mod_role = message.channel.guild.get_role(599996020171997206)
					await message.channel.send(f'Voting has started, please mention `Vote Pings` to let them know! {duel_mod_role.mention}')
				else:
					await message.channel.send('This is just a test match, not pinging `Vote Pings` or `here`.')

			# build voting embed
			embed_title = 'Match Voting'
			embed_description = '**Vote for your favorite!** Results will be sent to this channel when voting ends in 2 hours.\n🇦 First image\n🇧 Second image'
			embed = await generate_embed('pink', embed_title, embed_description)
			await message.channel.send(embed=embed, nonce='poll')
			return

		# '.matchisfinal' command (contest category)
		if message_content == '.matchisfinal':
			await action_log('setting next match as final in database settings')
			query = 'UPDATE settings SET next_match_is_final = True WHERE guild_id = %s'
			q_args = [config.MM_GUILD_ID]
			await execute_sql(query, q_args)
			connect.conn.commit()
			await action_log('next match set as final')

			embed_title = 'Set as Final'
			embed_description = 'The next match has been set as final in the database.'
			embed = await generate_embed('green', embed_title, embed_description)
			await message.channel.send(embed=embed)
			return
		return

# client event triggers on any discord reaction add
@client.event
async def on_raw_reaction_add(payload):
	# create variables for base message and channel
	channel = client.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)

	# find out if the message being reacted to is from MadnessMod
	if message.author.id == client.user.id:
		if len(message.embeds) == 1:
			# create variables for the reaction emoji, user, and guild
			emoji = payload.emoji.name
			guild = client.get_guild(payload.guild_id)
			if guild is not None:
				user = guild.get_member(payload.user_id)
			else:
				user = client.get_user(payload.user_id)

			if not user.bot:
				# match voting polls
				if message.embeds[0].title == 'Match Voting' and message.embeds[0].description.startswith('**Vote for your favorite!'):
					# remove the user's reaction from the bot (anonymous polling)
					await message.remove_reaction(emoji, user)
					await action_log(f'reaction added to poll by {user.display_name}')

					# create dm channel with the user
					user_channel = await user.create_dm()

					# check for existing participant in database
					query = 'SELECT match_votes, lb_points, vote_streak, longest_vote_streak, unvoted_match_start_time, last_vote_streak_time FROM participants WHERE user_id = %s'
					q_args = [user.id]
					await execute_sql(query, q_args)
					result = connect.crsr.fetchone()
					if result is None:
						# create participant if none exists
						query = 'INSERT INTO participants (user_id) VALUES (%s)'
						q_args = [user.id]
						await execute_sql(query, q_args)
						connect.conn.commit()
						await action_log('no existing user, new user added to participants table in postgresql')
						match_votes = 0
						lb_points = 0
						vote_streak = 0
						longest_vote_streak = 0
						unvoted_match_start_time = None
						last_vote_streak_time = 0
					else:
						match_votes = result[0]
						lb_points = result[1]
						vote_streak = result[2]
						longest_vote_streak = result[3]
						unvoted_match_start_time = result[4]
						last_vote_streak_time = result[5]

					# find the ID of the active match
					query = 'SELECT db_id, u1_id, u2_id FROM matches WHERE channel_id = %s ORDER BY db_id DESC'
					q_args = [payload.channel_id]
					await execute_sql(query, q_args)
					result = connect.crsr.fetchone()
					if result is not None:
						match_id = result[0]
						u1_id = result[1]
						u2_id = result[2]

						if not config.TESTING:
							# check to see if the person voting is one of the match participants
							if user.id == u1_id or user.id == u2_id:
								embed_title = 'Invalid Vote'
								embed_description = 'You cannot vote in your own match.'
								embed = await generate_embed('red', embed_title, embed_description)
								await user_channel.send(embed=embed)
								await action_log(f'attempted self-vote in match by {user.display_name}')
								return

						# check postgresql database for an existing vote by the user in the specified match
						query = 'SELECT a_vote, b_vote FROM votes WHERE user_id = %s AND match_id = %s'
						q_args = [user.id, match_id]
						await execute_sql(query, q_args)
						result = connect.crsr.fetchone()
						if result is not None:
							if result[0] or result[1]:
								# find which image the user originally voted for
								if result[0] and emoji == '🇦':
									vote_position = 'A'
								elif result[1] and emoji == '🇧':
									vote_position = 'B'
								elif (result[0] and emoji == '🇧') or (result[1] and emoji == '🇦'):
									# send the user a warning if their vote was for the wrong image
									embed_title = 'Invalid Vote'
									embed_description = 'You have previously voted for the other image, please remove your vote before attempting to vote again.'
									embed = await generate_embed('red', embed_title, embed_description)
									# send embed to the user via dm
									await user_channel.send(embed=embed)
									await action_log(f'invalid vote in match by {user.display_name}')
									return
								else:
									# send the user a warning if their vote broke any other rules
									embed_title = 'Invalid Vote'
									embed_description = 'You attempted to react to a match poll with an invalid emoji.'
									embed = await generate_embed('red', embed_title, embed_description)
									# send embed to the user via dm
									await user_channel.send(embed=embed)
									await action_log(f'invalid vote in match by {user.display_name}')
									return
								# generate vote removal embed
								embed_title = 'Vote Removal'
								embed_description = f'Your vote for **image {vote_position}** has been removed.'
								embed = await generate_embed('yellow', embed_title, embed_description)
								# remove vote from postgresql
								query = 'DELETE FROM votes WHERE user_id = %s AND match_id = %s'
								q_args = [user.id, match_id]
								await execute_sql(query, q_args)
								connect.conn.commit()
								await action_log('vote removed from database')
								if not config.TESTING:
									# update participant stats
									query = 'UPDATE participants SET match_votes = %s, lb_points = %s WHERE user_id = %s'
									q_args = [match_votes - 1, lb_points - 10, user.id]
									await execute_sql(query, q_args)
									connect.conn.commit()
									await action_log('participant stats updated')
								# send embed to the user via dm
								await user_channel.send(embed=embed)
								return
							return
						# find which image the user voted for
						if emoji == '🇦':
							vote_position = 'A'
							query = 'INSERT INTO votes (user_id, match_id, a_vote) VALUES (%s, %s, True)'
							q_args = [user.id, match_id]
						elif emoji == '🇧':
							vote_position = 'B'
							query = 'INSERT INTO votes (user_id, match_id, b_vote) VALUES (%s, %s, True)'
							q_args = [user.id, match_id]
						else:
							await action_log('no vote position specified')
							return
						# add vote info to postgresql via the above queries
						await execute_sql(query, q_args)
						connect.conn.commit()
						await action_log('vote inserted into database')

						vote_streak_bonus = 0
						# check to see if the user's last vote was within 48 hours
						streak_kept = False
						try:
							if unvoted_match_start_time is None:
								streak_kept = True
							elif time.time() <= unvoted_match_start_time + 172800:
								streak_kept = True
						except TypeError:
							await action_log('ERROR - unvoted_match_start_time caused a TypeError')

						if streak_kept:
							# check to see if the user's streak was incremented at least 23 hours ago
							if time.time() >= last_vote_streak_time + 82800:
								# increment the user's vote streak
								vote_streak += 1
								last_vote_streak_time = time.time()
								# check to see if the user has voted at least 2 days in a row
								if vote_streak >= 2:
									if vote_streak < len(config.VOTE_STREAK_BONUSES):
										vote_streak_bonus = config.VOTE_STREAK_BONUSES[int(vote_streak - 1)]
										last_vote_streak_time = time.time()
									else:
										vote_streak_bonus = config.VOTE_STREAK_BONUSES[-1]
										last_vote_streak_time = time.time()
								# check to see if this is the user's longest vote streak
								if vote_streak > longest_vote_streak:
									longest_vote_streak = vote_streak
						else:
							vote_streak = 1
							last_vote_streak_time = time.time()

						if not config.TESTING:
							# update participant vote count, lb_points, and vote streak
							query = 'UPDATE participants SET match_votes = %s, lb_points = %s, vote_streak = %s, longest_vote_streak = %s, unvoted_match_start_time = NULL, last_vote_streak_time = %s WHERE user_id = %s'
							q_args = [match_votes + 1, lb_points + 10 + vote_streak_bonus, vote_streak, longest_vote_streak, last_vote_streak_time, user.id]
							await execute_sql(query, q_args)
							connect.conn.commit()
							await action_log('participant stats updated')

						# send vote confirmation to the user via dm
						embed_title = 'Vote Confirmation'
						if vote_streak == 1:
							vote_streak_string = '1 day'
						else:
							vote_streak_string = f'{vote_streak} days'
						embed_description = f'Your vote for **image {vote_position}** has been confirmed. If you\'d like to change your vote, remove this vote by using the same emoji.\n\nYou have earned **10 points** for voting!'
						if vote_streak_bonus > 0:
							embed_description += f'\nYour new voting streak is `{vote_streak_string}`, next streak available in `23 hours`.\nYou have earned **{vote_streak_bonus} bonus points** for increasing your voting streak!'
						else:
							# calculate seconds until the user's next voting streak
							try:
								next_streak_seconds = int(last_vote_streak_time) + 82800 - round(time.time())
								if round(next_streak_seconds / (60 * 60)) > 1:
									# round to the nearest hour
									next_streak_string = f'{round(next_streak_seconds / (60 * 60))} hours'
								elif round(next_streak_seconds / 60) > 0:
									# round to the nearest minute
									next_streak_string = f'{round(next_streak_seconds / 60)} minutes'
								else:
									# there was some kind of error
									await action_log('CRITICAL ERROR - next_streak_seconds was negative')
									return
							except TypeError:
								await action_log('ERROR - next_streak_seconds caused a TypeError')
								next_streak_string = '`N/A`'

							embed_description += f'\nYour current voting streak is `{vote_streak_string}`, next streak available in `{next_streak_string}`.'
						embed = await generate_embed('green', embed_title, embed_description)
						await user_channel.send(embed=embed)
						await action_log('vote confirmation sent to user')
					return

				# mod help guide
				if message.embeds[0].title == 'Mod Help Guide':
					# remove the user's reaction from the bot
					await message.remove_reaction(emoji, user)
					await action_log(f'reaction added to mod help guide')

					embed_title = 'Mod Help Guide'
					# check to see which emoji was used
					if emoji == '⚔️':
						# match commands
						embed_description = """**⚔️ Match Commands**
							\n`.cancelmatch` - cancels the match in a given match channel
							\n`.forcewin` - ends a match by forcing one of the participants to win (use in matches when one participant hasn't submitted)
							\n`.matchisfinal` - sets the next match as a final match which will ping `Verified` and `everyone`
							\n`.showresults` - shows the results of the most recent match in the match channel it's called in
							\n`.splitmatch @<user> @<user>` - splits a match between two users so they can compete separately
							\n`.startmatch @<user> @<user>` - starts a match between two users
							\n`.startsolo @<user>` - starts a user's solo match (use after `.splitmatch`)"""
					elif emoji == '🏆':
						# tournament commands
						embed_description = """**🏆 Tournament Commands**
							\n`.remindparticipants` - alerts all participants of unfinished matches
							\n`.createbracket <tournament reference>` - creates a Challonge bracket with the given tournament reference (for example, use `10` to get Meme Madness 10) and populates all participants
							\n`.creatematchchannels <tournament reference>` - creates a match channel for every "open" match from the specified Challonge bracket
							\n`.deletematchchannels` - deletes existing match channels from the matches category
							\n`.prelim <user ID>` - sets a user's tournament role to `Preliminary` (deprecated)
							\n`.removetournamentroles` - remove past participants' round roles (deprecated)
							\n`.resignup <user ID> <reason>` - deletes a user's template and DMs them with `<reason>`, prompting them to re-signup
							\n`.settournamentroles` - removes all past tournament roles and initializes the tournament's participants' round roles (sets them to Round 1)
							\n`.signuplist` - displays a full list of signups for the current tournament"""
					elif emoji == '📎':
						# admin commands
						embed_description = """**📎 Admin Commands**
							\n`.activematches` - displays all currently active matches
							\n`.activepolls` - displays all currently active polls
							\n`.clearmatches` - clears all matches and votes from the database
							\n`.clearsignups` - clears all signups from the database
							\n`.reconnect` - forces the bot to reconnect to its database
							\n`.removeinvalidparticipants` - removes users who have left the server from the database
							\n`.restartpolls` - fixes any match polls that are no longer counting votes
							\n`.togglesignups` - open or close tournament signups
							\n`.toggletemplates` - enable or disable template requirements with `.signup`"""
					elif emoji == '↩️':
						# back to main help menu
						embed_description = """Use the emojis to navigate this help guide:
							\n⚔️ Match Commands
							\n🏆 Tournament Commands
							\n📎 Admin Commands
							\n↩️ Return Here"""
					else:
						# invalid emoji, do nothing
						return

					# update the help guide
					embed = await generate_embed('yellow', embed_title, embed_description)
					await message.edit(embed=embed)
					await action_log('mod help guide edited')
					return

				# points leaderboard (overall)
				if message.embeds[0].title == 'Overall Points Leaderboard':
					# remove the user's reaction from the bot
					await message.remove_reaction(emoji, user)
					await action_log(f'reaction added to leaderboard by {user.display_name}')

					try:
						# check which page the leaderboard is currently on
						lb_page = int(message.embeds[0].description.split('Page ')[1].split(':')[0])
					except IndexError:
						lb_page = 1

					# check to see which emoji was used
					if emoji == '⬅️':
						# previous page
						if lb_page == 1:
							return
						lb_page -= 1
					elif emoji == '🔅':
						# jump to self
						query = 'WITH cte_lb_rank AS (SELECT user_id, RANK () OVER (ORDER BY lb_points DESC) lb_rank FROM participants) SELECT lb_rank FROM cte_lb_rank WHERE user_id = %s'
						q_args = [user.id]
						await execute_sql(query, q_args)
						result = connect.crsr.fetchone()
						if result is not None:
							user_rank = result[0]
							lb_page = ceil(user_rank / 10)
					elif emoji == '➡️':
						lb_page += 1

					# update the embed description
					first_participant = (lb_page * 10) - 9
					last_participant = lb_page * 10
					query = 'SELECT user_id, lb_points, RANK () OVER (ORDER BY lb_points DESC) lb_rank FROM participants ORDER BY lb_points DESC'
					await execute_sql(query)
					results = connect.crsr.fetchall()
					embed_title = 'Overall Points Leaderboard'

					iteration = 0
					user_found = False
					# iterate through the participants in the database
					for entry in results:
						# initialize variables for the member and their info
						member = guild.get_member(entry[0])
						lb_points = entry[1]
						lb_rank = entry[2]

						if member is not None:
							iteration += 1

							if iteration < first_participant and member == user:
								user_found = True
								embed_description = 'User\'s rank:\n'
								embed_description += functions.format_lb_entry(lb_page, lb_rank, member.display_name, lb_points)

							elif iteration == first_participant:
								if user_found:
									embed_description += f'\nPage {lb_page}:\n'
								else:
									embed_description = f'Page {lb_page}:\n'

							if iteration >= first_participant and iteration <= last_participant:
								if member == user:
									user_found = True
								embed_description += functions.format_lb_entry(lb_page, lb_rank, member.display_name, lb_points)
							elif iteration > last_participant and member == user:
								embed_description += '\nUser\'s rank:\n'
								embed_description += functions.format_lb_entry(lb_page, lb_rank, member.display_name, lb_points)

							if iteration > last_participant and user_found:
								break

					embed = await generate_embed('blue', embed_title, embed_description)
					await message.edit(embed=embed)
					return
	return

# client event triggers on any discord reaction add
@client.event
async def on_reaction_add(reaction, user):
	# create variable for base message
	message = reaction.message

	if message.nonce is not None:
		# act on template confirmations for split matches
		if message.nonce.startswith('spltemp'):
			if not user.bot:
				match_channel = client.get_channel(int(message.nonce.lstrip('spltemp')))

				# pull match data from database
				query = 'SELECT template_message_id, u1_id, u2_id FROM matches WHERE start_time IS NULL AND template_message_id IS NOT NULL AND channel_id = %s'
				q_args = [match_channel.id]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				template_message_id = result[0]
				u1 = message.guild.get_member(result[1])
				u2 = message.guild.get_member(result[2])

				# get custom emojis from discord
				check_emoji = client.get_emoji(637394596472815636)
				x_emoji = client.get_emoji(637394622200676396)
				if check_emoji == None or x_emoji == None:
					await action_log('ERROR IN TEMPLATE RANDOMIZATION -- EMOJI NOT FOUND')
					return

				# get url information from the base message
				template_url = message.embeds[0].image.url
				template_message = await client.get_channel(config.TEMPLATE_CHAN_ID).fetch_message(template_message_id)
				template_author = message.guild.get_member(int(template_message.embeds[0].description.split(' (')[0].lstrip('<@').lstrip('!').rstrip('>')))

				#  find which reaction was added
				if reaction.emoji == check_emoji:
					# delete original message
					await message.delete()
					# build template accepted embed
					embed_title = 'Template Accepted'
					embed_description = 'The randomized template was accepted. It has been stored in the database.'
					embed = await generate_embed('green', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('randomized template accepted')

					# delete message in match channel
					await match_channel.last_message.delete()
					# build split match embed
					embed_title = 'Match Split'
					embed_description = f'The match between {u1.mention} and {u2.mention} has been split. Mods, use the `.startsolo @user` command to start each match.'
					embed = await generate_embed('green', embed_title, embed_description)
					await match_channel.send(embed=embed)

					# update match start_time and template_url in database
					query = 'UPDATE matches SET template_message_id = NULL, template_url = %s, template_author_id = %s WHERE channel_id = %s AND start_time IS NULL AND template_message_id IS NOT NULL'
					q_args = [template_url, template_author.id, match_channel.id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('match template updated in database')
				elif reaction.emoji == x_emoji:
					# delete original message
					await message.delete()
					# build template rejected embed
					embed_title = 'Template Rejected'
					embed_description = 'The randomized template was rejected. Please try `.splitmatch` again.'
					embed = await generate_embed('red', embed_title, embed_description)
					await message.channel.send(embed=embed)
					await action_log('randomized template rejected')

					# delete message from match channel
					await match_channel.last_message.delete()
					# send embed in match channel
					await match_channel.send(embed=embed)
					await action_log('match channel notified')

					# remove match from database
					query = 'DELETE FROM matches WHERE channel_id = %s AND start_time IS NULL AND template_message_id IS NOT NULL'
					q_args = [match_channel.id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('match removed from database')

		# act on template confirmations for normal matches
		if message.nonce.startswith('tempcon'):
			# don't act on bot reactions
			if not user.bot:
				# find match channel
				match_channel = client.get_channel(int(message.nonce.lstrip('tempcon')))

				# pull match data from database
				query = 'SELECT u1_id, u2_id, template_message_id FROM matches WHERE start_time IS NULL AND template_message_id IS NOT NULL AND channel_id = %s'
				q_args = [match_channel.id]
				await execute_sql(query, q_args)
				result = connect.crsr.fetchone()
				# save match data to variables and start DM channels with participants
				member1 = message.guild.get_member(result[0])
				u1_channel = await member1.create_dm()
				member2 = message.guild.get_member(result[1])
				u2_channel = await member2.create_dm()
				template_message_id = result[2]

				# get custom emojis from discord
				check_emoji = client.get_emoji(637394596472815636)
				x_emoji = client.get_emoji(637394622200676396)
				if check_emoji == None or x_emoji == None:
					await action_log('ERROR IN TEMPLATE RANDOMIZATION -- EMOJI NOT FOUND')
					return

				# get url information from the base message
				template_url = message.embeds[0].image.url
				template_message = await client.get_channel(config.TEMPLATE_CHAN_ID).fetch_message(template_message_id)
				template_author = message.guild.get_member(int(template_message.embeds[0].description.split(' (')[0].lstrip('<@').lstrip('!').rstrip('>')))

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
					query = 'UPDATE matches SET start_time = %s, template_message_id = NULL WHERE channel_id = %s AND start_time IS NULL AND template_message_id = %s'
					q_args = [time.time(), match_channel.id, template_message_id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('match start_time updated in database')

					# send notifying DMs to participants
					embed_title = 'Match Started'
					embed_description = 'Your Meme Madness match has started! You have 30 minutes from this message to complete the match. **Please DM me the `.submit` command when you\'re ready to hand in your final meme.** Here is your template:'
					embed = await generate_embed('yellow', embed_title, embed_description, attachment=template_url)
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
						query = 'DELETE FROM matches WHERE channel_id = %s AND start_time IS NOT NULL AND template_message_id IS NULL'
						q_args = [match_channel.id]
						await execute_sql(query, q_args)
						connect.conn.commit()
						await action_log('match removed from database')
						return

					# delete message from match channel
					await match_channel.last_message.delete()
					# send template to match channel
					embed_title = 'Match Started'
					embed_description = f'{member1.mention} and {member2.mention} have 30 minutes to hand in their final memes. Good luck! (Thanks to {template_author.mention} for the template!)'
					embed = await generate_embed('green', embed_title, embed_description, attachment=template_url)
					await match_channel.send(embed=embed)
					await action_log(f'match started between {member1.display_name} and {member2.display_name}')

					if not config.TESTING:
						# delete template from #templates channel, move to #temp-archive
						await client.get_channel(config.TEMP_ARCHIVE_CHAN_ID).send(embed=template_message.embeds[0])
						await template_message.delete()
						await action_log('template deleted from templates channel')

					# sleep for 15 minutes (config.MATCH_WARN1_TIME seconds)
					await asyncio.sleep(config.MATCH_WARN1_TIME)

					await action_log('checking submission status')
					# check for submissions, remind users to submit if they haven't yet
					query = 'SELECT u1_submitted, u2_submitted, cancelled FROM matches WHERE u1_id = %s AND u2_id = %s ORDER BY db_id DESC'
					q_args = [member1.id, member2.id]
					await execute_sql(query, q_args)
					result = connect.crsr.fetchone()
					if result is not None:
						if result[2]:
							return
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
					query = 'SELECT u1_submitted, u2_submitted, cancelled FROM matches WHERE u1_id = %s AND u2_id = %s ORDER BY db_id DESC'
					q_args = [member1.id, member2.id]
					await execute_sql(query, q_args)
					result = connect.crsr.fetchone()
					if result is not None:
						if result[2]:
							return
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
					query = 'SELECT u1_submitted, u2_submitted, cancelled FROM matches WHERE u1_id = %s AND u2_id = %s ORDER BY db_id DESC'
					q_args = [member1.id, member2.id]
					await execute_sql(query, q_args)
					result = connect.crsr.fetchone()
					if result is not None:
						if result[2]:
							return
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
						embed_description = f'{member1.mention} has missed their submission deadline.'
						embed2 = await generate_embed('red', embed_title, embed_description)
						await client.get_channel(config.SUBMISSION_CHAN_ID).send(embed=embed2)
					# executes if member2 has not submitted
					if not result[1]:
						await u2_channel.send(embed=embed1)
						# build missed deadline embed
						embed_description = f'{member2.mention} has missed their submission deadline.'
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
					query = 'DELETE FROM matches WHERE channel_id = %s AND start_time IS NULL AND template_message_id IS NOT NULL'
					q_args = [match_channel.id]
					await execute_sql(query, q_args)
					connect.conn.commit()
					await action_log('match removed from database')
			return
		return
	return

# client event triggers when discord bot client is fully loaded and ready
@client.event
async def on_ready():
	# change discord bot client presence to 'playing Meme Madness' 
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Meme Madness'))

	# send ready confirmation to command line
	print(f'Logged in as {client.user.name} - {client.user.id}')
	if config.TESTING:
		print('Currently in TESTING MODE')
	print('------')

	# start end_polls task
	if end_polls.get_task() is None:
		end_polls.start()
	return

# starts instance of discord bot client
client.run(config.TOKEN)