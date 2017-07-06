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


def output_result(results, output_format):
	import json
	if output_format == "raw":
		print json.dumps(results)
	elif output_format == "pretty":
		print json.dumps(results, indent=4, sort_keys=True, ensure_ascii=False, encoding="utf-8")
	elif output_format == "json":
		with open("output.json", 'w+') as output_file:
			json.dump(results, output_file)
	elif output_format == "csv":
		#TODO : write to CSV file
		pass
	else:
		assert False, "unhandled output format : " + output_format

def parse_arguments(available_commands, acceptable_non_arg_options, acceptable_arg_options):
	import getopt, sys
	# 0A. Check if each provided option has short and long version
	for acceptable_non_arg_option in acceptable_non_arg_options:
		if len(acceptable_non_arg_options) != 2:
			assert False, "non-arg options number mismatch : " + str(acceptable_arg_option)
	for acceptable_arg_option_dict in acceptable_arg_options:
		acceptable_arg_option = acceptable_arg_option_dict["option_name"]
		if len(acceptable_arg_option) != 2:
			assert False, "arg options number mismatch : " + str(acceptable_arg_option)
	
	# 0B. Build the options string and dict for getopt
	acceptable_short_non_arg_options = map(lambda x : x[0], acceptable_non_arg_options)
	acceptable_short_arg_options = map(lambda x: x["option_name"][0], acceptable_arg_options)
	acceptable_short_options_string = "".join(acceptable_short_non_arg_options) + "".join(map(lambda x: x + ":", acceptable_short_arg_options))
	print acceptable_short_options_string
	acceptable_long_non_arg_options = map(lambda x : x[1], acceptable_non_arg_options)
	acceptable_long_arg_options = map(lambda x: x["option_name"][1], acceptable_arg_options)
	acceptable_long_options_dict = acceptable_long_non_arg_options + map(lambda x: x + "=", acceptable_long_arg_options)
	print acceptable_long_options_dict
	input_data = []
	try:
		# 1. Get the options and standard (non-optional ) arguments
		opts, non_opts_args = getopt.gnu_getopt(sys.argv[1:], acceptable_short_options_string, acceptable_long_options_dict)
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
			if option in map(lambda x: "-" + x, acceptable_short_non_arg_options):
				option_name = acceptable_long_non_arg_options[acceptable_short_non_arg_options.index(option[1:])] #map(lambda x: "-" + x, short_non_arg_options_dict)
				options_dict[option_name] = True
			elif option in map(lambda x: "--" + x, acceptable_long_non_arg_options):
				option_name = option[2:]
				options_dict[option_name] = True
			# 3B. Arg options
			elif option in map(lambda x: "-" + x, acceptable_short_arg_options):
				option_name = acceptable_long_arg_options[acceptable_short_arg_options.index(option[1:])]
				matching_acceptable_arg_option_dict = [ acceptable_arg_option_dict for acceptable_arg_option_dict in acceptable_arg_options if acceptable_arg_option_dict["option_name"][1] == option_name ][0]
				acceptable_arg_option_values = matching_acceptable_arg_option_dict["acceptable_values"]
				if arg in acceptable_arg_option_values:
					options_dict[option_name] = arg
				else:
					assert False, "unhandled option value : " + arg + " for option " + option_name
			elif option in map(lambda x: "--" + x, acceptable_long_arg_options):
				option_name = option[2:]
				matching_acceptable_arg_option_dict = [ acceptable_arg_option_dict for acceptable_arg_option_dict in acceptable_arg_options if acceptable_arg_option_dict["option_name"][1] == option_name ][0]
				acceptable_arg_option_values = matching_acceptable_arg_option_dict["acceptable_values"]
				if arg in acceptable_arg_option_values:
					options_dict[option_name] = arg
				else:
					assert False, "unhandled option value : " + arg + " for option " + option_name
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

def get_input_data(input_format, command_line_args):
	import sys
	# 0. Get input from stdin or command line arguments (input type = stdin or cli)
	input_data = []
	if len(command_line_args) == 0:
		# get only last line to avoid log messages
		input_data.append(get_last_line(sys.stdin))
	else:
		input_data = command_line_args
	# 1. Parse the input depending on format
	# raw HTML strings : decode
	if input_format == "raw":
		input_data = map(decode_html, input_data)
	# URLs : load HTML from them
	elif input_format == "url":
		map(load_url, input_data)
		pass
	# HTML local files : read HTML files
	elif input_format == "html":
		verbose_print("input data is html")
		input_data = map(load_local_html, input_data)
	# JSON : decode
	elif input_format == "json":
		input_data = map(decode_json(), input_data)
	# CSV : 
	elif input_format == "csv":
		#TODO : read CSV file
		pass
	else:
		assert False, "unhandled input format : " + input_format
	return input_data

def get_last_line(file):
	last_line = file.readline()
	for line in file:
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

def load_url(url_address):
	import urllib2
	response = urllib2.urlopen(url_address)
	return response.read()