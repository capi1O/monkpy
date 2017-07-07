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

def get_array_depth(array):
	array_depth = 1
	try:
		while type(array[0]) == list and is_array_homogeneous(array):
			array_depth += 1
			array = array[0]
	except TypeError as err:
		verbose_print("object is not an array but of type : " + str(type(array)))
		array_depth -= 1
	except IndexError as err:
		verbose_print("array is empty : " + str(array))
	return array_depth

def is_array_equal(array):
	array = iter(array)
	try:
		first = next(array)
	except StopIteration:
		return True
	return all(first == rest for rest in array)

def get_array_width(array):
	# check that all items are arrays
	if get_array_depth(array) >= 2:
		#get of number of elements for each item has same 
		widths = map(len, array)
		# check if all array elements are the same
		if is_array_equal(widths):
			return widths[0]
		else:
			assert False, "array is not rectangular : " + str(array)
	else:
		assert False, "array is not deep enough : " + str(array)
	
def is_array_homogeneous(array):
	if type(array) != list:
		assert False, "object is not an array but of type : " + str(type(array))
	try:
		item_type = type(array[0])
	except IndexError as err:
		# assert False, "array is empty : " + str(array)
		verbose_print("array is empty : " + str(array))
		return False
	for item in array:
		if type(item) != item_type :
			return False
	return True

def super_map(array, function, *args):
	resulting_array = []
	for item in array:
		# Apply function to the item, passing optional arguments
		result = function(item, *args)
		resulting_array.append(result)
	return resulting_array

def super_submap(two_levels_array, function, *args):
	resulting_two_levels_array = []
	for array in two_levels_array:
		resulting_array = super_map(array, function, *args)
		resulting_two_levels_array.append(resulting_array)
	return resulting_two_levels_array

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
	if is_array_homogeneous(array):
		return type(array[0])
	else:
		assert False, "array is not homogeneous : " + str(array)

def is_string(object_type):
	return object_type in [str, unicode]
	# return isinstance(object, basestring): #if type() == str does not True for unicode strings

def get_all_keys(dicts):
	dict_keys = []
	for dictionnary in dicts:
		dict_keys += dictionnary.keys()
	return list(set(dict_keys))

def flatten_dicts(group_dicts, group_name_key, group_dicts_key):
	flattened_dicts = []
	for group_dict in group_dicts:
		group_name = group_dict[group_name_key]
		dicts = group_dict[group_dicts_key]
		for dictionnary in dicts:
			dictionnary[group_name_key] = group_name
			flattened_dicts.append(dictionnary)
	return flattened_dicts

def utf8_dict(dictionnary):
	return { k:v.encode('utf8') for k,v in dictionnary.items() }
	
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
		write_dicts_to_csv('output.csv', results)
	else:
		assert False, "unhandled output format : " + output_format

def output_grouped_results(group_names, group_results_dicts, output_format, group_name_key, group_results_dicts_key):
	# check
	if len(group_names) != len(group_results_dicts):
		assert False, "mismatch number for grouped output : "  + str(len(group_results_dicts)) + " group results for " + str(len(group_names)) + " keys"
	# make dict
	result_dicts = []
	for index, results in enumerate(group_results_dicts):
		result_dict = { 
			group_name_key : group_names[index],
			group_results_dicts_key : results
		}
		result_dicts.append(result_dict)
	# flatter dict for CSV output
	if output_format.endswith("csv"):
		result_dicts = flatten_dicts(result_dicts, group_name_key, group_results_dicts_key)
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
	# 1. Arrange data in a 1 or 2 deep array
	# depth 1 = array of data blocks, depth 2 = array of arrays of data blocks or array of dicts with arrays of data blocks)
	data_blocks = []
	data_keys = []
	# 1.A. Array items are data blocks
	if input_type in ["inline"]:
		data_blocks = input_data
		verbose_print("input data is " + str(data_blocks))
	# 1.B Array item are groups of data blocks (organized in array or dicts)
	elif input_type in ["inline-json", "json", "inline-csv", "csv"]:
		if len(input_data) == 0:
			assert False, "no input"
		elif len(input_data) == 1:
			# A. JSON data
			if input_type.endswith("json"):
				if input_type == "inline-json":
					json_data = decode_json(input_data[0])
				elif input_type == "json":
					json_data = read_json(input_data[0])
				else:
					assert False, "unknown json format : " + input_type
				# Check how data is organized
				array_type = get_array_type(json_data)
				# List of data blocks (in JSON array)
				if is_string(array_type):
					data_blocks = json_data
				# List of grouped data blocks (JSON array of dicts of data blocks)
				elif array_type == dict:
					data_blocks, data_keys = get_dict_data(json_data, input_data_group_name_key, input_data_group_array_key, False)
					#TODO : Check each data block, must be strings
				else:
					assert False, "unknown organization for data : " + str(json_data[0])
			# B. CSV data
			elif input_type.endswith("csv"):
				if input_type == "inline-csv":
					csv_data = decode_csv(input_data[0])
				elif input_type == "csv":
					csv_data_lines = read_csv(input_data[0])
				else:
					assert False, "unknown csv format : " + input_type
				# Check how data is organized
				# check number of columns
				columns_number = get_array_width(csv_data_lines)
				# List of data blocks
				if columns_number == 1:
					csv_data = super_map(csv_data_lines, get_item, 0)
					# check type
					if is_string(get_array_type(csv_data)):
						data_blocks = csv_data
					else:
						assert False, "incorrect CSV data : " + str(csv_data)
				# List of grouped data blocks 
				elif columns_number == 2:
					header_row = True
					if header_row:
						csv_data_group_name_key = csv_data_lines[0][0]
						csv_data_group_array_key = csv_data_lines[0][1]
						# Remove header row
						csv_data_lines.pop(0)
					# Get keys and values
					group_keys = list(set(super_map(csv_data_lines, get_item, 0)))
					if is_string(get_array_type(group_keys)):
						pass #alright
					# group data lines where key is same
					csv_data_groups = []
					for key in group_keys:
						csv_data_group = []
						for csv_data_line in csv_data_lines:
							if csv_data_line[0] == key:
								csv_data_group.append(csv_data_line[1])
						csv_data_groups.append(csv_data_group)
					if is_string(get_array_type(csv_data_groups)):
						pass #alright
					data_blocks = csv_data_groups
					data_keys = group_keys
					#TODO : Check each data block, must be strings	
				else:
					assert False, "unsupported organization for CSV data : " + str(csv_data_lines)
			else:
				assert False, "impossible"
		else:
			assert False, "too many groups of data blocks provided"
			#TODO : handle multiple files
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

def array_from_file(open_file):
	lines = []
	for line in open_file:
		lines.append(line)
	return lines

def get_last_line(open_file):
	last_line = open_file.readline()
	for line in open_file:
		print(line) # necessary has script can be piped with -v option set
		last_line = line
	return last_line

# Data and file handling functions

def load_data(data_array, input_format):
	if input_format in ["url", "html-file", "raw-html"]:
		array_depth = get_array_depth(data_array)
		if array_depth == 1:
			# verbose_print("loaded_data is : " + str(loaded_data))
			loaded_data = [load_html_data(data_block, input_format) for data_block in data_array]
		elif array_depth == 2:
			# verbose_print("loaded " + str(len(loaded_data)) + " data blocks")
			loaded_data = [ [load_html_data(data_block, input_format) for data_block in grouped_data_blocks] for grouped_data_blocks in data_array]
		else:
			assert False, "unsupported array dimension : " + str(array_depth)
	else:
		assert False, "unsupported data format : " + str(input_format)
	return loaded_data

def load_html_data(html_thing, input_format):
	# URLs : load HTML from them
	if input_format == "url":
		html_data = load_url(html_thing)
		pass
	# raw encoded HTML strings : decode
	elif input_format == "raw-html":
			html_data = decode_html(html_thing)
		# HTML local files : read HTML files
	elif input_format == "html-file":
			verbose_print("input data is loaded from html file")
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
		assert False, "Error : could not decode JSON from line : " + json_line + ", error : " + str(value_error)

def read_json(json_filename):
	import json
	try:
		with open(json_filename) as json_file:
			return json.load(json_file)	
	except ValueError as value_error:
		assert False, "Error : could not read JSON file : " + json_file + ", error : " + str(value_error)
	except IOError as io_error:
		assert False, "file : '" + json_filename + "' does not exist"

def decode_csv(csv_line):
	return None

def read_csv(csv_filename):
	import csv
	try:
		with open(csv_filename) as csv_file:
			return array_from_file(csv.reader(csv_file, delimiter=',', quotechar='"'))
	except ValueError as value_error:
		assert False, "Error : could not read CSV file : " + csv_file + ", error : " + str(value_error)
	except IOError as io_error:
		assert False, "file : '" + csv_filename + "' does not exist"

def write_dicts_to_csv(csv_file, dicts):
	import csv
	csv_columns = get_all_keys(dicts)
	try:
		with open(csv_file, 'w') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
			writer.writeheader()
			for dictionnary in dicts:
				writer.writerow(utf8_dict(dictionnary))
	except IOError as (errno, strerror):
		print("I/O error({0}): {1}".format(errno, strerror))
	return

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