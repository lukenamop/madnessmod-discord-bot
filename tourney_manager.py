#!/usr/bin/env python3

# import libraries
import challonge

# import additional files
import config

# set challonge API credentials
challonge.set_credentials(config.C_USERNAME, config.C_API_KEY)
print('challonge API connected')

def create_tournament(name, shortcut):
	challonge.tournaments.create(name, shortcut, hold_third_place_match=True, quick_advance=True)
	return

def add_participant(tournament_shortcut, username):
	challonge.participants.create(tournament_shortcut, username)
	return

def bulk_add_participants(tournament_shortcut, bulk_usernames):
	for username in bulk_usernames:
		challonge.participants.create(tournament_shortcut, username)
	return