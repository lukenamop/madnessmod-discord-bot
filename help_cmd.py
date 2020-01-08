dm_help = """`.donate` - shows MadnessMod donation info
	\n`.help` - returns this help menu
	\n`.signup` - submits a template to the Meme Madness moderators (must be used in the same message as an attachment)
	\n`.submit` - submits a final meme to your active match
	\n`.template` - submits a template to be used in Meme Madness matches"""

stats_help = """`.donate` - shows MadnessMod donation info
	\n`.help` - returns this help menu
	\n`.stats` - displays your Meme Madness stats (can also be used like `.stats @<user>`)"""

mod_help = """`.cancelmatch` - cancels the match in a given match channel
	\n`.donate` - shows MadnessMod donation info
	\n`.forcewin` - ends a match by forcing one of the participants to win (use in split matches when one participant hasn't competed)
	\n`.help` - returns this help menu
	\n`.matchisfinal` - sets the next match as a final match which will ping `Verified` and `everyone`
	\n`.resignup <user ID> <reason>` - deletes a user's template and DMs them with `<reason>`, prompting them to re-signup
	\n`.showresults` - shows the results of the most recent match in the match channel it's called in
	\n`.signuplist` - displays a full list of signups for the current cycle
	\n`.startmatch @<user> @<user>` - starts a match between two users, if an image is attached it will be supplied as their template (can only be used in a #contest channel)
	\n`.splitmatch @<user> @<user>` - splits a match into two solo matches
	\n`.startsolo @<user>` - starts a user's solo match after a `.splitmatch`"""

admin_help = """`.activematches` - displays all currently active matches and polls
	\n`.cancelmatch` - cancels the match in a given match channel
	\n`.clearmatches` - clears all matches and votes from the database (**admin only**)
	\n`.clearsignups` - clears all signups from the database (**admin only**)
	\n`.createbracket <tournament reference>` - creates a Challonge bracket with the given tournament reference (for example, Meme Madness 10) and populates all participants (**admin only**)
	\n`.creatematchchannels <tournament reference>` - creates a match channel for every "open" match from the specified Challonge bracket (**admin only**)
	\n`.donate` - shows MadnessMod donation info
	\n`.forcewin` - ends a match by forcing one of the participants to win (use in split matches when one participant hasn't competed)
	\n`.help` - returns this help menu
	\n`.matchisfinal` - sets the next match as a final match which will ping `Verified` and `everyone`
	\n`.prelim <user ID>` - sets a user's tournament role to `Preliminary` (**admin only**)
	\n`.reconnect` - forces the bot to reconnect to its database (**admin only**)
	\n`.removetournamentroles` - remove past participants' round roles (**admin only**)
	\n`.resignup <user ID> <reason>` - deletes a user's template and DMs them with `<reason>`, prompting them to re-signup
	\n`.settournamentroles` - initializes the tournament's participants' round roles (sets them to Round 1) (**admin only**)
	\n`.showresults` - shows the results of the most recent match in the match channel it's called in
	\n`.signuplist` - displays a full list of signups for the current cycle
	\n`.startmatch @<user> @<user>` - starts a match between two users, if an image is attached it will be supplied as their template (can only be used in a #contest channel)
	\n`.toggletemplates` - enable or disable template requirements with `.signup` (**admin only**)"""