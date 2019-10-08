#!/usr/bin/env python3

# add '\' before underscores in a specified input_string
def escape_underscores(input_string):
	return input_string.translate(str.maketrans({'_': '\_'}))