#!/usr/bin/env python3

# import libraries
import challonge

# import additional files
import config

# set challonge API credentials
challonge.set_credentials(config.C_USERNAME, config.C_API_KEY)

print(challonge.matches.index('mmcycle9'))