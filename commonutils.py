#!/usr/bin/env python

# General purpose functions

verbose = False
def verbose_print(*args):
	if verbose :
		# Print each argument separately
		for arg in args:
			print arg,
		print
	else:
		pass	# do nothing

def get_array_dim(array):
	if type(array) == list:
		# array of arrays
		try:
			if type(array[0]) == list: #if type() == str does not True for unicode strings
				#TODO : recursively
				return 2
			# array of objects
			else:
				return 1
				#TODO : check data type for each item
		except IndexError as err:
			assert False, "array is empty : " + str(array)
	else:
		assert False, "object is not an array but of type : " + str(type(array))

def super_map(array, function, *args):
	resulting_array = []
	for item in array:
		# Apply function to the item, passing optional arguments
		result = function(item, *args)
		resulting_array.append(result)
	return resulting_array

def super_submap(two_dim_array, function, *args):
	resulting_two_dim_array = []
	for array in two_dim_array:
		resulting_array = super_map(array, function, *args)
		resulting_two_dim_array.append(resulting_array)
	return resulting_two_dim_array

def get_item(iterable, index, default=None):
	if iterable:
		try:
			return iterable[index]
		except IndexError as err:
			assert False, "index " + str(index) + " out of bounds of iterable : " + str(iterable) + " of length : " + str(len(iterable))
		except KeyError as err:
			assert False, "key " + str(index) + " could not be found in iterable : " + str(iterable)
		except TypeError as err:
			assert False, "iterable : " + str(iterable) + " of type : " + str(type(iterable)) + " is not hashable, with key [" + str(index) + "] of type : " + str(type(index))
	return default

def get_subitem(iterable, index, subindex, default=None):
	item = get_item(iterable, index)
	subitem = get_item(item, subindex, default)
	return subitem

def append_string(input_string, string2):
	return input_string + string2

def prepend_string(input_string, string2):
	return string2 + input_string

def get_array_type(array):
	try:
		array_type = type(array[0])
	except IndexError as err:
		assert False, "array is empty"
	for item in array:
		if type(item) != array_type:
			assert False, "array is not uniform : " + str(array)
	return array_type

# Input/output functions

def output_results(results, output_format):
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

def output_grouped_results(group_keys, grouped_results, output_format):
	# check
	if len(group_keys) != len(grouped_results):
		assert False, "mismatch number for grouped output : "  + str(len(grouped_results)) + " group results for " + str(len(group_keys)) + " keys"
	# make dict
	result_dicts = []
	for index, results in enumerate(grouped_results):
		result_dict = { 
			"key" : group_keys[index],
			"results" : results
		}
		result_dicts.append(result_dict)
	output_results(result_dicts, output_format)

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
	acceptable_short_non_arg_options = super_map(acceptable_non_arg_options, get_item, 0)
	acceptable_short_arg_options = super_map(acceptable_arg_options, get_subitem, "option_name", 0)
	acceptable_short_options_string = "".join(acceptable_short_non_arg_options) + "".join(super_map(acceptable_short_arg_options, append_string, ":"))
	verbose_print("long options are : '" + acceptable_short_options_string + "'")
	acceptable_long_non_arg_options = super_map(acceptable_non_arg_options, get_item, 1)
	acceptable_long_arg_options = super_map(acceptable_arg_options, get_subitem, "option_name", 1)
	acceptable_long_options_dict = acceptable_long_non_arg_options + super_map(acceptable_long_arg_options, append_string, "=")
	verbose_print("long options are : '" + " ". join(acceptable_long_options_dict) + "'")
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
			if option in super_map(acceptable_short_non_arg_options, prepend_string, "-"):
				option_name = acceptable_long_non_arg_options[acceptable_short_non_arg_options.index(option[1:])] #map(lambda x: "-" + x, short_non_arg_options_dict)
				options_dict[option_name] = True
			elif option in super_map(acceptable_long_non_arg_options, prepend_string, "--"):
				option_name = option[2:]
				options_dict[option_name] = True
			# 3B. Arg options
			elif option in super_map(acceptable_short_arg_options, prepend_string, "-"):
				option_name = acceptable_long_arg_options[acceptable_short_arg_options.index(option[1:])]
				matching_acceptable_arg_option_dict = [ acceptable_arg_option_dict for acceptable_arg_option_dict in acceptable_arg_options if acceptable_arg_option_dict["option_name"][1] == option_name ][0]
				acceptable_arg_option_values = matching_acceptable_arg_option_dict["acceptable_values"]
				if arg in acceptable_arg_option_values:
					options_dict[option_name] = arg
				else:
					assert False, "unhandled option value : " + arg + " for option " + option_name
			elif option in super_map(acceptable_long_arg_options, prepend_string, "--"):
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

def get_input_data(input_type, input_format, command_line_args, input_data_group_name_key, input_data_group_array_key):
	import sys
	# 0. Get input from stdin or command line arguments (input type = stdin or cli)
	input_data = []
	if len(command_line_args) == 0:
		# get only last line to avoid log messages
		input_data.append(get_last_line(sys.stdin))
	else:
		input_data = command_line_args
	# 1. Arrange data in a 1 or 2 dim array
	# dimension 1 = array of data blocks, dimension 2 = array of arrays of data blocks or array of dicts with arrays of data blocks)
	data_blocks = []
	data_keys = []
	# 1.A. Array of data blocks
	if input_type in ["inline"]:
		data_blocks = input_data
		verbose_print("input data is " + str(data_blocks))
	# 1.B Array of arrays of data blocks or array of dicts with arrays of data blocks
	elif input_type in ["inline_json", "json", "inline-csv", "csv"]:
		if len(input_data) != 1:
			assert False, "script accept only one file"
		else:
			# 1.B.A. JSON data
			if input_type.endswith("json"):
				if input_type == "inline_json":
					json_data = decode_json(input_data[0])
				elif input_type == "json":
					json_data = read_json(input_data[0])
				else:
					assert False, "unknown json format : " + input_type
				if type(json_data) == list:
					# 1.B.A.A JSON array of data blocks
					if isinstance(json_data[0], basestring): #if type() == str does not True for unicode strings
						data_blocks = json_data
					# 1.B.A.B. JSON array of dicts of data blocks
					elif type(json_data[0]) == dict:
						data_blocks, data_keys = get_dict_data(json_data, input_data_group_name_key, input_data_group_array_key, False)
					else:
						assert False, "unknown organization for data : " + str(json_data[0])
				else:
					assert False, "JSON input type must be array, " + str(json_data)
			# B. CSV data
			elif input_format.endswith("csv"):
				#TODO
				pass
	else:
		assert False, "unhandled input type : " + input_type
	# 2. Load Data depending on type (only HTML supported)
	loaded_data = load_data(data_blocks, input_format)
	return [loaded_data, data_keys]

def get_dict_data(data_dicts, input_data_group_name_key, input_data_group_array_key, merge):
	data_keys = []
	data_blocks = []
	for data_dict in data_dicts:
		try:
			data_keys.append(data_dict[input_data_group_name_key])
			data_blocks_part = data_dict[input_data_group_array_key]
			verbose_print("dict contains : " + str(data_blocks_part))
			if type(data_blocks_part) != list:
				assert False, "incorrect data organization : " + str(type(data_blocks_part))
			if merge:
				data_blocks += data_blocks_part
			else:
				data_blocks.append(data_blocks_part)
		except KeyError as err:
			assert False, "incorrect key name, " + str(err)
	verbose_print("data_blocks are : " + str(data_blocks))
	return [data_blocks, data_keys]

def get_last_line(file):
	last_line = file.readline()
	for line in file:
		print(line) # necessary has script can be piped with -v option set
		last_line = line
	return last_line

# Data and file handling functions

def load_data(data_array, input_format):
	if input_format in ["url", "html", "inline_html"]:
		array_dim = get_array_dim(data_array)
		if array_dim == 1:
			# verbose_print("loaded_data is : " + str(loaded_data))
			loaded_data = [load_html_data(data_block, input_format) for data_block in data_array]
		elif array_dim == 2:
			# verbose_print("loaded " + str(len(loaded_data)) + " data blocks")
			loaded_data = [ [load_html_data(data_block, input_format) for data_block in grouped_data_blocks] for grouped_data_blocks in data_array]
		else:
			assert False, "unsupported array dimension : " + str(array_dim)
	else:
		assert False, "unsupported data format : " + str(input_format)
	return loaded_data

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