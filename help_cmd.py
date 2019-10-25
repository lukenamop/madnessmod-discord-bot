dm_help = """`.donate` - shows MadnessMod donation info
	\n`.help` - returns this help menu
	\n`.signup` - submits a template to the Meme Madness moderators (must be used in the same message as an attachment)
	\n`.submit` - submits a final meme to your active match
	\n`.template` - submits a template to be used in Meme Madness matches"""

stats_help = """`.donate` - shows MadnessMod donation info
	\n`.help` - returns this help menu
	\n`.stats` - displays your Meme Madness stats (can also be used like `.stats @<user>`)"""

mod_help = """`.donate` - shows MadnessMod donation info
	\n`.help` - returns this help menu
	\n`.resignup <user ID> <reason>` - deletes a user's template and DMs them with `<reason>`, prompting them to re-signup
	\n`.showresults` - shows the results of the most recent match in the match channel it's called in
	\n`.signuplist` - displays a full list of signups for the current cycle
	\n`.startmatch @<user> @<user>` - starts a match between two users, if an image is attached it will be supplied as their template (can only be used in a #contest channel)"""

admin_help = """`.clearmatches` - clears all matches and votes from the database (**admin only**)
	\n`.clearsignups` - clears all signups from the database (**admin only**)
	\n`.donate` - shows MadnessMod donation info
	\n`.help` - returns this help menu
	\n`.prelim <user ID>` - sets a user's tournament role to `Preliminary`
	\n`.removetournamentroles` - remove past participants' round roles (**admin only**)
	\n`.resignup <user ID> <reason>` - deletes a user's template and DMs them with `<reason>`, prompting them to re-signup
	\n`.settournamentroles` - initializes the tournament's participants' round roles (sets them to Round 1) (**admin only**)
	\n`.showresults` - shows the results of the most recent match in the match channel it's called in
	\n`.signuplist` - displays a full list of signups for the current cycle
	\n`.startmatch @<user> @<user>` - starts a match between two users, if an image is attached it will be supplied as their template (can only be used in a #contest channel)
	\n`.toggletemplates` - enable or disable template requirements with `.signup` (**admin only**)"""