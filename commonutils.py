#!/usr/bin/env python

verbose = False
def verbose_print(*args):
	if verbose :
		# Print each argument separately
		for arg in args:
			print arg,
		print
	else:
		pass	# do nothing


def output_result(results, output_type):
	import json

	if output_type == "stdout":
		print json.dumps(results)
	elif output_type == "pretty":
		print json.dumps(results, indent=4, sort_keys=True, ensure_ascii=False, encoding="utf-8")
	elif output_type == "json":
		with open("output.json", 'w+') as output_file:
			json.dump(results, output_file)
	elif output_type == "csv":
		#TODO : write to CSV file
		pass
	else:
		assert False, "unhandled output type : " + output_type


def parse_arguments(available_commands, short_non_arg_options_dict, long_non_arg_options_dict, short_arg_options_dict, long_arg_options_dict):
	import getopt, sys

	# 0A. Check correct number of arguments
	if len(short_non_arg_options_dict) != len(long_non_arg_options_dict):
		assert False, "non-arg options number mismatch : " + str(short_non_arg_options_dict) + str(long_non_arg_options_dict)
	if len(short_arg_options_dict) != len(long_arg_options_dict):
		assert False, "arg options number mismatch : " + str(short_arg_options_dict) + str(long_arg_options_dict)
	# 0B. Build the options string and dict for getopt
	short_options_string = "".join(short_non_arg_options_dict) + "".join(map(lambda x: x + ":", short_arg_options_dict))
	long_options_dict = long_non_arg_options_dict + map(lambda x: x + "=", long_arg_options_dict)
	
	input_data = []
	try:
		# 1. Get the options and standard (non-optional ) arguments
		opts, non_opts_args = getopt.gnu_getopt(sys.argv[1:], short_options_string, long_options_dict)
		# 2. Parse the  ommand (take the first non-optional argument as command)
		if len(non_opts_args) != 0:
			command = non_opts_args.pop(0)
			# print command
			if command not in available_commands:
				assert False, "unhandled command : " + command
		else:
			assert False, "no command provided"
		# 3. Get the options value
		options_dict = {}
		for option, arg in opts:
			# 3A. Non-arg options
			if option in map(lambda x: "-" + x, short_non_arg_options_dict):
				option_name = long_non_arg_options_dict[short_non_arg_options_dict.index(option[1:])] #map(lambda x: "-" + x, short_non_arg_options_dict)
				options_dict[option_name] = True
			elif option in map(lambda x: "--" + x, long_non_arg_options_dict):
				option_name = option[2:]
				options_dict[option_name] = True
			# 3B. Arg options
			elif option in map(lambda x: "-" + x, short_arg_options_dict):
				option_name = long_arg_options_dict[short_arg_options_dict.index(option[1:])]
				options_dict[option_name] = arg
				#TODO : check if option value is valid
			elif option in map(lambda x: "--" + x, long_arg_options_dict):
				option_name = option[2:]
				options_dict[option_name] = arg
				#TODO : check if option value is valid
			else:
				assert False, "unhandled option : " + option
		# Set verbose
		global verbose
		verbose = options_dict.get("verbose", False)
		# 4. Return 
		return [command, options_dict, non_opts_args] #non_opts_args are the remaining arguments
	except getopt.GetoptError as err:
		sys.stderr.write(str(err))
		# usage()
		sys.exit(2)

def get_input_data(input_type, command_line_args):
	import sys, urllib

	# 0. Get input from stdin or command line arguments
	input_data = []
	if len(command_line_args) == 0:
		# get only last line to avoid log messages
		input_data.append(get_last_line(sys.stdin))
	else:
		input_data = command_line_args
	# 1. Load input from file if needed
	if input_type == "raw":
		pass
	elif input_type == "url":
		#map(urllib.open(), input_data)
		pass
	elif input_type == "html":
		verbose_print("input data is html")
		input_data = map(load_local_html, input_data)
	elif input_type == "json":
		input_data = map(decode_json(), input_data)
	elif input_type == "csv":
		#TODO : write to CSV file
		pass
	return input_data

def get_last_line(std_input):
	import sys
	
	last_line = std_input.readline()
	for line in std_input:
		print(line) # necessary has script can be piped with -v option set
		last_line = line
	return last_line

def encode_html(html):
	from shellescape import quote
	return quote(html)
	
def decode_html(encoded_html):
	from HTMLParser import HTMLParser
	return HTMLParser().unescape(encoded_html)

def decode_json(json_line):
	import json
	
	try:
		return json.loads(json_line)
	except ValueError as value_error:
		sys.stderr.write("Error : could not decode JSON from line : " + json_line), value_error
		sys.exit(2)

def load_local_html(html_filename):
	import os

	if os.path.exists(html_filename):
		with open(html_filename, 'r') as html_file:
			try:
				return html_file.read()
			except EOFError:
				sys.stderr.write("error while reading file '" + html_filename + "'")
	else:
		# print "file does not exist"
		return None