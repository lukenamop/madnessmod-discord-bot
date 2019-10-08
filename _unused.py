# '.registermatch' command (duel-mods)
# if message_content.startswith('.registermatch '):
# 	message_split = message_content.split(' ')
# 	match_num = message_split[1]
# 	ud1_id = int(message_split[2])
# 	user1 = message.guild.get_member(ud1_id)
# 	ud1 = user1.name + '#' + user1.discriminator
# 	ud2_id = int(message_split[3])
# 	user2 = message.guild.get_member(ud2_id)
# 	ud2 = user2.name + '#' + user2.discriminator
# 	channel_name = 'match-' + match_num + '-' + user1.display_name[:5] + '-v-' + user2.display_name[:5]
# 	category_id = 581876790172319767
# 	category = message.guild.get_channel(category_id)
# 	await message.guild.create_text_channel(channel_name, category=category)
# 	await action_log('match channel created')

# 	# add match info to postgresql
# 	query = 'INSERT INTO matches (ud1, ud1_id, ud2, ud2_id, channel_id) VALUES (\'' + ud1 + '\', ' + str(ud1_id) + ', \'' + ud2 + '\', ' + str(ud2_id) + ', 0)'
# 	connect.crsr.execute(query)
# 	connect.conn.commit()
# 	await action_log('match info added to postgresql')

# 	# respond to the command
# 	embed_title = 'Match Registered'
# 	embed_description = 'The match between ' + ud1 + ' and ' + ud2 + ' has been registered! Their match channel has been created.'
# 	embed = await generate_embed('green', embed_title, embed_description)
# 	await message.channel.send(embed=embed)
# 	return

# '.startmatch' command (duel-mods)
# if message_content.startswith('.startmatch '):
# 	message_split = message_content.split(' ')
# 	uid = message_split[1]
# 	query = 'SELECT ud1, ud1_id, ud2, ud2_id FROM matches WHERE ud1_id = ' + uid
# 	connect.crsr.execute(query)
# 	result = connect.crsr.fetchone()
# 	if result is None:
# 		query = 'SELECT ud1, ud1_id, ud2, ud2_id FROM matches WHERE ud2_id = ' + uid
# 		connect.crsr.execute(query)
# 		result = connect.crsr.fetchone()
# 		if result is None:
# 			embed_title = 'Error: No Match'
# 			embed_description = 'There is no match with that user. Double check that you\'ve copied the user\'s exact 18 digit ID (e.g. `622139031756734492`).'
# 			embed = generate_embed('red', embed_title, embed_description)
# 			await message.channel.send(embed=embed)
# 			await action_log('no match error when starting match')
# 			return

# 	# add start_time to postgresql
# 	ud1 = result[0]
# 	ud1_id = result[1]
# 	ud2 = result[2]
# 	ud2_id = result[3]
# 	embed_title = 'Your Match Has Begun!'
# 	embed_description = 'Your Meme Madness match just started! You have 30 minutes to submit your final meme. Check your match channel to see which mod to send your meme to.'
# 	if message.attachments[0] is None:
# 		embed = await generate_embed('green', embed_title, embed_description)
# 	else:
# 		embed_link = message.attachments[0].url
# 		embed = await generate_embed('green', embed_title, embed_description, embed_link)
# 	user_channel = client.get_user(ud1_id).dm_channel
# 	user_channel.send(embed=embed)
# 	user_channel = client.get_user(ud2_id).dm_channel
# 	user_channel.send(embed=embed)
# 	query = 'UPDATE matches SET start_time = ' + str(time.time()) + ' WHERE ud1_id = ' + str(ud1_id) + ' AND ud2_id = ' + str(ud2_id)
# 	connect.crsr.execute(query)
# 	connect.conn.commit()
# 	embed_title = 'Match Started'
# 	embed_description = 'The match between ' + ud1 + ' and ' + ud2 + ' has been started! They have been mentioned in their match\'s channel and have 30 minutes to submit their memes.'
# 	embed = await generate_embed('green', embed_title, embed_description)
# 	await message.channel.send(embed=embed)
# 	await action_log('match started by duel-mods')
# 	return