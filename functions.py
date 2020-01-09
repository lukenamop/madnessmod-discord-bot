#!/usr/bin/env python3

# add '\' before underscores in a specified input_string
def escape_underscores(input_string):
	return input_string.translate(str.maketrans({'_': '\_'}))

# format leaderboard entries
def format_lb_entry(lb_page, iteration, lb_rank, member_name, lb_points):
	if lb_page == 1:
		if iteration < 10:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
		elif iteration >= 10:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
	elif lb_page == 10:
		if iteration < 100:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
		elif iteration >= 100:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
	elif lb_page == 100:
		if iteration < 1000:
			# add an extra space to align the other ranks
			return f'**` {lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
		elif iteration >= 1000:
			return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'
	else:
		return f'**`{lb_rank}:` {escape_underscores(member_name)}** - {lb_points} points\n'