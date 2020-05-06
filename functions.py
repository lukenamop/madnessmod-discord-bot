#!/usr/bin/env python3

# add '\' before underscores in a specified input_string
def escape_underscores(input_string):
	return input_string.translate(str.maketrans({'_': '\_'}))

# format leaderboard entries
def format_lb_entry(lb_page, lb_rank, member_name, lb_points):
	if lb_page >= 1 and lb_page < 10:
		if lb_rank < 10:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
		elif lb_rank >= 10:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
	elif lb_page >= 10 and lb_page < 100:
		if lb_rank < 100:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
		elif lb_rank >= 100:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
	elif lb_page >= 100 and lb_page < 1000:
		if lb_rank < 1000:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
		elif lb_rank >= 1000:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
	else:
		return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'

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