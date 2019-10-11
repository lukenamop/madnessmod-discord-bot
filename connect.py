#!/usr/bin/env python3

import config
import psycopg2
import os

conn = psycopg2.connect(config.DB_URL)
crsr = conn.cursor()

# print connection properties
print('postgres connection info:')
print(conn.get_dsn_parameters())

print('settings:')
crsr.execute("""SELECT * FROM settings""")
for row in crsr.fetchall():
	print(row)

print('participants:')
crsr.execute("""SELECT * FROM participants""")
for row in crsr.fetchall():
	print(row)

# print('signups:')
# crsr.execute("""SELECT * FROM signups""")
# for row in crsr.fetchall():
# 	print(row)

# print('matches:')
# crsr.execute("""SELECT * FROM matches""")
# for row in crsr.fetchall():
# 	print(row)

# print('votes:')
# crsr.execute("""SELECT * FROM votes""")
# for row in crsr.fetchall():
# 	print(row)

# TABLE settings
# db_id SERIAL PRIMARY KEY
# guild_id NUMERIC(18) NOT NULL
# template_required BOOLEAN DEFAULT True

# TABLE participants
# db_id SERIAL PRIMARY KEY
# user_id NUMERIC(18) NOT NULL
# total_matches NUMERIC(5) DEFAULT 0
# match_wins NUMERIC(5) DEFAULT 0
# match_losses NUMERIC(5) DEFAULT 0
# total_votes_for NUMERIC(7) DEFAULT 0
# avg_final_meme_time NUMERIC(4) DEFAULT NULL

# TABLE signups
# db_id SERIAL PRIMARY KEY
# user_id NUMERIC(18) NOT NULL
# message_id NUMERIC(18) NOT NULL
# submission_time NUMERIC(10) NOT NULL

# TABLE matches
# db_id SERIAL PRIMARY KEY
# u1_id NUMERIC(18) NOT NULL
# u2_id NUMERIC(18) NOT NULL
# start_time NUMERIC(10) DEFAULT NULL
# u1_submitted BOOLEAN DEFAULT False
# u2_submitted BOOLEAN DEFAULT False
# channel_id NUMERIC(18) NOT NULL
# u1_image_url VARCHAR(200) DEFAULT NULL
# u2_image_url VARCHAR(200) DEFAULT NULL
# a_meme NUMERIC(1) DEFAULT NULL

# TABLE votes
# db_id SERIAL PRIMARY KEY
# user_id NUMERIC(18) NOT NULL
# match_id NUMERIC(10) NOT NULL
# a_vote BOOLEAN DEFAULT False
# b_vote BOOLEAN DEFAULT False