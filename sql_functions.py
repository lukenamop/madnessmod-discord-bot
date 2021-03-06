#!/usr/bin/env python3

# import files
import discord
import asyncio
import config
import connect

# function to safely execute SQL queries, with error handling for closed connections
async def execute_sql(query, q_args=None, attempt=1):
	reconnect_and_retry = False
	try:
		if q_args is None:
			# execute a basic SQL query
			connect.crsr.execute(query)
		else:
			# find out how many arguments there are
			q_arg_len = len(q_args)
			if q_arg_len == 1:
				connect.crsr.execute(query, (q_args))
			elif q_arg_len > 1:
				connect.crsr.execute(query, q_args)

	except connect.psycopg2.errors.InFailedSqlTransaction as error:
		reconnect_and_retry = True
		print(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')
	except connect.psycopg2.OperationalError as error:
		reconnect_and_retry = True
		print(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')
	except connect.psycopg2.InterfaceError as error:
		reconnect_and_retry = True
		print(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')
	except connect.psycopg2.DatabaseError as error:
		reconnect_and_retry = True
		print(f'failed SQL transaction, reconnecting automatically: {type(error)}: {error}')

	# reconnect to the database and try to re-execute the SQL query
	if reconnect_and_retry:
		success = connect.db_connect()
		if success:
			print('reconnection was a success')
			# only try 3 times, if it still doesn't work there is some larger issue
			if attempt <= 3:
				await execute_sql(query, q_args=q_args, attempt=(attempt + 1))
		else:
			print('connection failed')
	return