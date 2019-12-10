#!/usr/bin/env python3

# import libraries
import challonge

# import additional files
import config

# set challonge API credentials
challonge.set_credentials(config.C_USERNAME, config.C_API_KEY)
print('challonge API connected')

# create a challonge tournament with the specified name and shortcut
def create_tournament(tournament_name, tournament_shortcut):
	challonge.tournaments.create(tournament_name, tournament_shortcut, hold_third_place_match=True, quick_advance=True)
	return

# add a participant to a specified challonge tournament
def add_participant(tournament_shortcut, username):
	challonge.participants.create(tournament_shortcut, username)
	return

# add multiple participants to a specified challonge tournament
def bulk_add_participants(tournament_shortcut, bulk_usernames):
	for username in bulk_usernames:
		challonge.participants.create(tournament_shortcut, username)
	return

# shuffle participant seeds in a specified challonge tournament
def shuffle_seeds(tournament_shortcut):
	challonge.participants.randomize(tournament_shortcut)
	return

# set a winner in the specified challonge match
def set_match_winner(tournament_shortcut, match_id, scores_csv, winner_id):
	challonge.matches.update(tournament_shortcut, match_id, scores_csv=scores_csv, winner_id=winner_id)
	return

# return an index of all matches within a specified challonge tournament
def index_tournament(tournament_shortcut):
	return challonge.matches.index(tournament_shortcut)

# return information about a participant in a specified challonge tournament
def show_participant(tournament_shortcut, participant_id):
	return challonge.participants.show(tournament_shortcut, participant_id)