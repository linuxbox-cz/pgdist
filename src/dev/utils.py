# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import difflib

import color

def get_header(project_name, header_type, part=None, roles=None, requires=None, version=None, old_version=None, new_version=None, dbparam=None, tables_data=None):
	project_config = header_type == "project-config"
	header = "--\n"
	header += "-- pgdist %s\n" % (header_type)
	header += "-- name: %s\n" % (project_name)
	header += "--\n"
	if version:
		header += "-- version: %s\n" % (version)
		header += "--\n"
	if old_version and new_version:
		header += "-- old version: %s\n" % (old_version)
		header += "-- new version: %s\n" % (new_version)
		header += "--\n"
	if dbparam and (project_config or part.number == 1):
		header += "-- dbparam: %s\n" % (dbparam)
		header += "--\n"
	if roles and (project_config or part.number == 1):
		for role in roles:
			header += "-- role: %s\n" % (role)
		header += "--\n"
	if requires and (project_config or part.number == 1):
		for require in requires:
			header += "-- require: %s\n" % (require)
		header += "--\n"
	if tables_data:
		for table_data in tables_data:
			header += "-- table_data: %s\n" % (table_data)
		header += "--\n"
	return header

def get_part_header(parts, header_type):
	part_string = ""
	if header_type == "project-config":
		part_string += "-- end header_data\n"
		part_string += "--\n"
		for i, part in enumerate(parts):
			part_string += "\n"
			part_string += "-- part: %s\n" % (part.number)
			if part.single_transaction:
				part_string += "-- single_transaction\n"
			else:
				part_string += "-- not single_transaction\n"
			if part.data:
				part_string += "\n"
				part_string += "%s" % (part.data)
	else:
		for part in parts:
			part_string += "-- part: %s\n" % (part.number)
			if part.single_transaction:
				part_string += "-- single_transaction\n"
			else:
				part_string += "-- not single_transaction\n"
			part_string += "--\n"
			part_string += "-- end header_data\n"
			part_string += "--\n"
	return part_string

def get_command(command, name, element_name="sqldist file"):
	cs = "\n" # cs = command_string
	cs += "--\n"
	cs += "-- %s %s\n" % (element_name.lower(), name)
	cs += "--\n"
	cs += "\n"
	cs += command.strip() + "\n"
	cs += "\n"
	cs += ";-- end %s %s\n\n" % (element_name.lower(), name)
	return cs

def diff(source, target, start_string="-- ", colored=False, from_file="removeline542358", to_file="removeline542358"):
	dc = difflib.unified_diff(source, target, fromfile=from_file, tofile=to_file) # dc = diff_c
	r = "" # r = result
	for d in dc:
		if from_file == "removeline542358" and from_file in d:
			pass
		elif d.startswith("-"):
			if colored:
				r += "%s%s\n" % (start_string, color.red(d))
			else:
				r += "%s%s\n" % (start_string, d)
		elif d.startswith("+"):
			if colored:
				r += "%s%s\n" % (start_string, color.green(d))
			else:
				r += "%s%s\n" % (start_string, d)
	return r + "\n"
