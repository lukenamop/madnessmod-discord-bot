#!/usr/bin/env python3

# import files
import discord
import asyncio
import io
import datetime
from PIL import Image, ImageDraw, ImageFont

# function to create a custom match frame image for the start of a match
async def create_match_frame_image(member1, member2):
	# make sure the members are accessible and in the guild
	try:
		member1_display_name = member1.display_name
		member2_display_name = member2.display_name
	except:
		return None

	# load the source background from the resources folder
	match_frame_source = Image.open('resources/images/transparent_background.png')

	# load the mentioned members' avatars and resize them
	member1_avatar = Image.open(io.BytesIO(await member1.avatar_url_as(format='png', size=1024).read())).resize((580, 580), resample=Image.BICUBIC)
	member2_avatar = Image.open(io.BytesIO(await member2.avatar_url_as(format='png', size=1024).read())).resize((580, 580), resample=Image.BICUBIC)

	# paste the avatars on the match frame source
	match_frame_source.paste(member1_avatar, (140, 110))
	match_frame_source.paste(member2_avatar, (720, 110))

	# load the match frame
	match_frame_transparent = Image.open('resources/images/match_frame_transparent.png')

	# paste the match frame
	match_frame_source.paste(match_frame_transparent, mask=match_frame_transparent.split()[3])

	# load the match frame lines
	match_frame_lines = Image.open('resources/images/match_frame_lines_logo.png')

	# paste the match frame lines
	match_frame_source.paste(match_frame_lines, mask=match_frame_lines.split()[3])

	# add the first mentioned member's username to the image
	roboto_font = ImageFont.truetype('resources/fonts/Roboto-Bold.ttf', size=55)
	draw_member1_name = ImageDraw.Draw(match_frame_source)
	w_1, h_1 = draw_member1_name.textsize(member1_display_name, font=roboto_font)
	if 361 - w_1 >= 0:
		draw_member1_name.text(((368 - w_1 + 258), 639), member1_display_name, fill='white', font=roboto_font)
	else:
		W_difference = 361 - w_1
		px_per_pt = 13.5
		pt_change = -int(W_difference / px_per_pt)
		roboto_font = ImageFont.truetype('resources/fonts/Roboto-Bold.ttf', size=(55 - pt_change))
		w_1, h_1 = draw_member1_name.textsize(member1_display_name, font=roboto_font)
		draw_member1_name.text(((368 - w_1 + 258), 639 + int(pt_change * 0.85)), member1_display_name, fill='white', font=roboto_font)

	# add the second mentioned member's username to the image
	roboto_font = ImageFont.truetype('resources/fonts/Roboto-Bold.ttf', size=55)
	draw_member2_name = ImageDraw.Draw(match_frame_source)
	w_2, h_2 = draw_member2_name.textsize(member2_display_name, font=roboto_font)
	if 361 - w_2 >= 0:
		draw_member2_name.text((812, 639), member2_display_name, fill='white', font=roboto_font)
	else:
		W_difference = 361 - w_2
		px_per_pt = 13.5
		pt_change = -int(W_difference / px_per_pt)
		roboto_font = ImageFont.truetype('resources/fonts/Roboto-Bold.ttf', size=(55 - pt_change))
		draw_member2_name.text((812, (639 + int(pt_change * 0.85))), member2_display_name, fill='white', font=roboto_font)

	# save the final image to memory
	final_image = io.BytesIO()
	match_frame_source.save(final_image, format='png')
	final_image.seek(0)
	final_file = discord.File(final_image, 'match_frame_edited.png')
	return final_file

# add '\' before underscores in a specified input_string
def escape_underscores(input_string):
	return input_string.translate(str.maketrans({'_': '\_'}))

# format leaderboard entries
def format_lb_entry(lb_page, lb_rank, member_name, lb_points):
	if lb_page >= 1 and lb_page < 10:
		if lb_rank < 10:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points:,} points\n'
		elif lb_rank >= 10:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points:,} points\n'
	elif lb_page >= 10 and lb_page < 100:
		if lb_rank < 100:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points:,} points\n'
		elif lb_rank >= 100:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points:,} points\n'
	elif lb_page >= 100 and lb_page < 1000:
		if lb_rank < 1000:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points:,} points\n'
		elif lb_rank >= 1000:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points:,} points\n'
	else:
		return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points:,} points\n'

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

# function to translate seconds into hours/minutes/seconds
def time_string(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	if d > 0:
		if h > 0:
			return f'{int(d)}d {int(h)}h'
		else:
			return f'{int(d)}d'
	elif h > 0:
		if m > 0:
			return f'{int(h)}h {int(m)}m'
		else:
			return f'{int(h)}h'
	elif m > 0:
		if s > 0:
			return f'{int(m)}m {int(s)}s'
		else:
			return f'{int(m)}m'
	elif s > 0:
		return f'{int(s)}s'
	else:
		return 'invalid'