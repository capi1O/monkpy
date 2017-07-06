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

def get_input_data(input_type, input_format, command_line_args):
	import sys
	# 0. Get input from stdin or command line arguments (input type = stdin or cli)
	input_data = []
	data_is_organized = False
	if len(command_line_args) == 0:
		# get only last line to avoid log messages
		input_data.append(get_last_line(sys.stdin))
	else:
		input_data = command_line_args
	# 1. 
	# inline string : load it straight
	if  input_type == "inline":
		input_data = [load_html_data(data, input_format) for data in input_data]
	# JSON strings : decode
	elif input_type == "inline_json":
		if len(input_data) == 1:
			input_data = decode_json(input_data[0])
			data_is_array = not check_data_organization(input_data[0], input_format)
			if data_is_array:
				input_data = [load_html_data(data, input_format) for data in input_data]
			else:
				assert False, "JSON data is organized, not implemented yet : " + str(input_data)
				data_is_organized = True
		else:
			assert False, "script accept only one JSON"	
	# JSON filenames : read JSON files
	elif input_type == "json":
		# input_data = map(read_json(), input_data)
		if len(input_data) == 1:
			input_data = read_json(input_data[0])
			data_is_array = not check_data_organization(input_data[0], input_format)
			if data_is_array:
				input_data = [load_html_data(data, input_format) for data in input_data]
			else:
				assert False, "JSON data is organized, not implemented yet : " + str(input_data)
				data_is_organized = True
		else:
			assert False, "script accept only one JSON file, " + str(len(input_data)) + " provided"
	# CSV strings
	elif input_type == "inline_csv":
		if len(input_data) == 1:
			#TODO : decode
			pass
		else:
			assert False, "script accept only one CSV"
	# CSV filenames
	elif input_type == "csv":
		if len(input_data) == 1:
			#TODO : read CSV file
			pass
		else:
			assert False, "script accept only one CSV file"
	else:
		assert False, "unhandled input type : " + input_type
	return input_data, data_is_organized

def check_data_organization(organized_input_data, input_format):
	# A. JSON organized data
	if input_format.endswith("json"):
		# Sanity check
		if type(organized_input_data) == list:
			# A.A JSON array, each item is either inline raw HTML, URL or HTML filename
			if type(organized_input_data[0]) == str:
				return False
			# A.B. JSON array, each item is a dictionnary
			elif type(organized_input_data[0]) == dict:
				return True
			# key1 = group name 
			# key2 = array of items : raw HTML, URL or HTML filename
			else:
				assert False, "unknown organization for data : " + str(organized_input_data)
		else:
			assert False, "json input type must be array"
	# B. CSV organized data
	elif input_format.endswith("csv"):
		#TODO
		pass
		return False
	else:
		return False

def load_html_data(html_thing, input_format):
	# URLs : load HTML from them
	if input_format == "url":
		html_data = load_url(html_thing)
		pass
	# raw encoded HTML strings : decode
	elif input_format == "inline_html":
		html_data = decode_html(html_thing)
	# HTML local files : read HTML files
	elif input_format == "html":
		verbose_print("input data is html")
		html_data = load_local_html(html_thing)
	else:
		assert False, "unhandled input format : " + input_format
	return html_data

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

def read_json(json_filename):
	import json
	try:
		with open(json_filename) as json_file:
			return json.load(json_file)	
	except ValueError as value_error:
		sys.stderr.write("Error : could not read JSON file : " + json_file), value_error
		sys.exit(2)
		
def load_local_html(html_filename):
	import os
	verbose_print("loading html file : '" + html_filename + "'")
	if os.path.exists(html_filename):
		with open(html_filename, 'r') as html_file:
			try:
				return html_file.read()
			except EOFError:
				sys.stderr.write("error while reading file '" + html_filename + "'")
	else:
		assert False, "file : '" + html_filename + "' does not exist"

def load_url(url_address):
	import urllib2
	response = urllib2.urlopen(url_address)
	return response.read()