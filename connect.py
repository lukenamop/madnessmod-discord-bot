#!/usr/bin/env python3

# import libraries
import psycopg2
import os

# import additional files
import config

def db_connect():
	# establish database connection
	global conn
	conn = psycopg2.connect(config.DB_URL)
	global crsr
	crsr = conn.cursor()
	print('database connected')

	# print connection properties
	print('postgres connection info:')
	print(conn.get_dsn_parameters())

	crsr.execute("""SELECT * FROM settings""")
	for row in crsr.fetchall():
		print('settings: ' + str(row))

	crsr.execute("""SELECT COUNT(*) FROM participants""")
	result = crsr.fetchone()
	print('participants: ' + str(result[0]))

	crsr.execute("""SELECT COUNT(*) FROM matches""")
	result = crsr.fetchone()
	print('matches: ' + str(result[0]))

	crsr.execute("""SELECT COUNT(*) FROM votes""")
	result = crsr.fetchone()
	print('votes: ' + str(result[0]))

	return True

db_connect()

# TABLE settings
# db_id SERIAL PRIMARY KEY
# template_required BOOLEAN DEFAULT True
# guild_id NUMERIC(18) NOT NULL
# next_match_is_final BOOLEAN DEFAULT False

# TABLE participants
# db_id SERIAL PRIMARY KEY
# user_id NUMERIC(18) NOT NULL
# total_matches NUMERIC(5) DEFAULT 0
# match_wins NUMERIC(5) DEFAULT 0
# match_losses NUMERIC(5) DEFAULT 0
# total_votes_for NUMERIC(7) DEFAULT 0
# avg_final_meme_time NUMERIC(4) DEFAULT NULL
# templates_submitted NUMERIC(7) DEFAULT 0
# match_votes NUMERIC(7) DEFAULT 0
# lb_points NUMERIC(10) DEFAULT 0
# longest_vote_streak NUMERIC(5) DEFAULT 0
# vote_streak NUMERIC(5) DEFAULT 0
# last_vote_streak_time NUMERIC(10) DEFAULT 0
# unvoted_match_start_time NUMERIC(10) DEFAULT NULL

# TABLE signups
# db_id SERIAL PRIMARY KEY
# user_id NUMERIC(18) NOT NULL
# message_id NUMERIC(18) NOT NULL
# submission_time NUMERIC(10) NOT NULL

# TABLE matches
# db_id SERIAL PRIMARY KEY
# u1_id NUMERIC(18) NOT NULL
# u2_id NUMERIC(18) NOT NULL
# creation_time NUMERIC(10) DEFAULT NULL
# start_time NUMERIC(10) DEFAULT NULL
# u1_submitted BOOLEAN DEFAULT False
# u2_submitted BOOLEAN DEFAULT False
# channel_id NUMERIC(18) NOT NULL
# u1_image_url VARCHAR(200) DEFAULT NULL
# u2_image_url VARCHAR(200) DEFAULT NULL
# a_meme NUMERIC(1) DEFAULT NULL
# template_message_id NUMERIC(18) DEFAULT NULL
# template_url VARCHAR(200) DEFAULT NULL
# template_author_id NUMERIC(18) DEFAULT NULL
# poll_start_time NUMERIC(10) DEFAULT NULL
# poll_extensions NUMERIC(1) DEFAULT 0
# is_final BOOLEAN DEFAULT False
# cancelled BOOLEAN DEFAULT False

# TABLE votes
# db_id SERIAL PRIMARY KEY
# user_id NUMERIC(18) NOT NULL
# match_id NUMERIC(10) NOT NULL
# a_vote BOOLEAN DEFAULT False
# b_vote BOOLEAN DEFAULT False