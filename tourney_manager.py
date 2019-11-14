#!/usr/bin/env python3

# import libraries
import challonge

# import additional files
import config

# set challonge API credentials
challonge.set_credentials(config.C_USERNAME, config.C_API_KEY)

# challonge.tournaments.create('test tournament 2', 'ttjachar88', hold_third_place_match=True, quick_advance=True)
challonge.participants.create('ttjachar88','lukenamop')
challonge.participants.create('ttjachar88','eltoch')
challonge.participants.create('ttjachar88','UncreativeFilth')

# print(challonge.matches.index('mmcycle9'))