#!/usr/bin/env python3

# import libraries
import challonge

# import additional files
import config

# set challonge API credentials
challonge.set_credentials(config.C_USERNAME, config.C_API_KEY)
print('challonge API connected')

def create_tournament(tournament_name, tournament_shortcut):
	challonge.tournaments.create(tournament_name, tournament_shortcut, hold_third_place_match=True, quick_advance=True)
	return

def add_participant(tournament_shortcut, username):
	challonge.participants.create(tournament_shortcut, username)
	return

def bulk_add_participants(tournament_shortcut, bulk_usernames):
	for username in bulk_usernames:
		challonge.participants.create(tournament_shortcut, username)
	return

def shuffle_seeds(tournament_shortcut):
	challonge.participants.randomize(tournament_shortcut)
	return

def set_match_winner(tournament_shortcut, match_id, scores_csv, winner_id):
	challonge.matches.update(tournament_shortcut, match_id, scores_csv=scores_csv, winner_id=winner_id)
	return

def index_tournament(tournament_shortcut):
	return challonge.matches.index(tournament_shortcut)

def show_participant(tournament_shortcut, participant_id):
	return challonge.participants.show(tournament_shortcut, participant_id)

##### TESTING BELOW

# [{'id': 180695793,
# 'tournament-id': 7797446,
# 'state': 'open',
# 'player1-id': 109357021,
# 'player2-id': 109357023,
# 'player1-prereq-match-id': None,
# 'player2-prereq-match-id': None,
# 'player1-is-prereq-match-loser': False,
# 'player2-is-prereq-match-loser': False,
# 'winner-id': None,
# 'loser-id': None,
# 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>),
# 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>),
# 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>),
# 'identifier': 'A',
# 'has-attachment': False,
# 'round': 1,
# 'player1-votes': None,
# 'player2-votes': None,
# 'group-id': None,
# 'attachment-count': None,
# 'scheduled-time': None,
# 'location': None,
# 'underway-at': None,
# 'optional': False,
# 'rushb-id': None,
# 'completed-at': None,
# 'suggested-play-order': 1,
# 'forfeited': None,
# 'prerequisite-match-ids-csv': None,
# 'scores-csv': None},

# {'id': 180695794, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357005, 'player2-id': 109357042, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'B', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 2, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695795, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357006, 'player2-id': 109357041, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'C', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 3, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695796, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357014, 'player2-id': 109357031, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'D', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 4, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695797, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357013, 'player2-id': 109357032, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'E', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 5, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695798, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357018, 'player2-id': 109357027, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'F', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 6, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695799, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357009, 'player2-id': 109357037, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'G', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 7, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695800, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357017, 'player2-id': 109357028, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'H', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 8, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695801, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357010, 'player2-id': 109357036, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'I', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 9, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695802, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357020, 'player2-id': 109357024, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'J', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 10, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695803, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357004, 'player2-id': 109357043, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'K', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 11, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695804, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357007, 'player2-id': 109357040, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'L', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 12, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695805, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357015, 'player2-id': 109357030, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'M', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 13, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695806, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357012, 'player2-id': 109357033, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'N', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 14, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695807, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357019, 'player2-id': 109357026, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'O', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 15, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695808, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357008, 'player2-id': 109357038, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'P', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 16, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695809, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357016, 'player2-id': 109357029, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'Q', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 17, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695810, 'tournament-id': 7797446, 'state': 'open', 'player1-id': 109357011, 'player2-id': 109357035, 'player1-prereq-match-id': None, 'player2-prereq-match-id': None, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 9, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'R', 'has-attachment': False, 'round': 1, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 18, 'forfeited': None, 'prerequisite-match-ids-csv': None, 'scores-csv': None},
# {'id': 180695811, 'tournament-id': 7797446, 'state': 'pending', 'player1-id': 109356958, 'player2-id': None, 'player1-prereq-match-id': None, 'player2-prereq-match-id': 180695793, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': None, 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'S', 'has-attachment': False, 'round': 2, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 19, 'forfeited': None, 'prerequisite-match-ids-csv': '180695793', 'scores-csv': None},
# {'id': 180695812, 'tournament-id': 7797446, 'state': 'pending', 'player1-id': None, 'player2-id': None, 'player1-prereq-match-id': 180695794, 'player2-prereq-match-id': 180695795, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': None, 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'T', 'has-attachment': False, 'round': 2, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 20, 'forfeited': None, 'prerequisite-match-ids-csv': '180695794,180695795', 'scores-csv': None},
# {'id': 180695813, 'tournament-id': 7797446, 'state': 'pending', 'player1-id': 109356988, 'player2-id': None, 'player1-prereq-match-id': None, 'player2-prereq-match-id': 180695796, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': None, 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'U', 'has-attachment': False, 'round': 2, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 21, 'forfeited': None, 'prerequisite-match-ids-csv': '180695796', 'scores-csv': None},
# {'id': 180695814, 'tournament-id': 7797446, 'state': 'pending', 'player1-id': 109356997, 'player2-id': None, 'player1-prereq-match-id': None, 'player2-prereq-match-id': 180695797, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': None, 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'V', 'has-attachment': False, 'round': 2, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 22, 'forfeited': None, 'prerequisite-match-ids-csv': '180695797', 'scores-csv': None},
# {'id': 180695815, 'tournament-id': 7797446, 'state': 'pending', 'player1-id': 109356980, 'player2-id': None, 'player1-prereq-match-id': None, 'player2-prereq-match-id': 180695798, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': None, 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'W', 'has-attachment': False, 'round': 2, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 23, 'forfeited': None, 'prerequisite-match-ids-csv': '180695798', 'scores-csv': None},
# {'id': 180695816, 'tournament-id': 7797446, 'state': 'pending', 'player1-id': 109357001, 'player2-id': None, 'player1-prereq-match-id': None, 'player2-prereq-match-id': 180695799, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': None, 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'X', 'has-attachment': False, 'round': 2, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 24, 'forfeited': None, 'prerequisite-match-ids-csv': '180695799', 'scores-csv': None},
# {'id': 180695817, 'tournament-id': 7797446, 'state': 'pending', 'player1-id': 109356981, 'player2-id': None, 'player1-prereq-match-id': None, 'player2-prereq-match-id': 180695800, 'player1-is-prereq-match-loser': False, 'player2-is-prereq-match-loser': False, 'winner-id': None, 'loser-id': None, 'started-at': None, 'created-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'updated-at': datetime.datetime(2019, 11, 14, 20, 25, 8, tzinfo=<FixedOffset '+00:00' datetime.timedelta(0)>), 'identifier': 'Y', 'has-attachment': False, 'round': 2, 'player1-votes': None, 'player2-votes': None, 'group-id': None, 'attachment-count': None, 'scheduled-time': None, 'location': None, 'underway-at': None, 'optional': False, 'rushb-id': None, 'completed-at': None, 'suggested-play-order': 25, 'forfeited': None, 'prerequisite-match-ids-csv': '180695800', 'scores-csv': None},

# {'id': 109357021,
# 'tournament-id': 7797446,
# 'name': 'skeletonwithbow',
# 'seed': 32,
# 'active': True,
# 'created-at': datetime.datetime(2019, 11, 14, 21, 21, 38, tzinfo=<FixedOffset '+01:00' datetime.timedelta(0, 3600)>),
# 'updated-at': datetime.datetime(2019, 11, 14, 21, 21, 38, tzinfo=<FixedOffset '+01:00' datetime.timedelta(0, 3600)>),
# 'invite-email': None,
# 'final-rank': None,
# 'misc': None,
# 'icon': None,
# 'on-waiting-list': False,
# 'invitation-id': None,
# 'group-id': None,
# 'checked-in-at': None,
# 'ranked-member-id': None,
# 'challonge-username': None,
# 'challonge-email-address-verified': None,
# 'removable': True,
# 'participatable-or-invitation-attached': False,
# 'confirm-remove': True,
# 'invitation-pending': False,
# 'display-name-with-invitation-email-address': 'skeletonwithbow',
# 'email-hash': None,
# 'username': None,
# 'display-name': 'skeletonwithbow',
# 'attached-participatable-portrait-url': None,
# 'can-check-in': False,
# 'checked-in': False,
# 'reactivatable': False,
# 'check-in-open': False,
# 'group-player-ids': None,
# 'has-irrelevant-seed': False}