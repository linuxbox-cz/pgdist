import difflib

import color

def get_header(project_name, header_type, parts, roles=None, requires=None, version=None, old_version=None, new_version=None, dbparam=None, tables_data=None):
	if header_type == 'config':
		nl = "\n" # nl = new_line
		hs = "" # hs = header_string
	else:
		nl = "--\n" # nl = new_line
		hs = nl # hs = header_string
	if header_type == 'update':
		hs += "-- pgdist update\n"
	else:
		hs += "-- pgdist project\n"
	hs += "-- name: %s\n" % (project_name)
	hs += nl
	if version:
		hs += "-- version: %s\n" % (version)
		hs += nl
	if old_version and new_version:
		hs += "-- old version: %s\n" % (old_version)
		hs += "-- new version: %s\n" % (new_version)
		hs += nl
	if dbparam:
		hs += "-- dbparam: %s\n" % (dbparam)
		hs += nl
	if roles:
		for role in roles:
			hs += "-- role: %s\n" % (role)
		hs += nl
	if requires:
		for require in requires:
			hs += "-- require: %s\n" % (require)
		hs += nl
	if tables_data:
		for table_data in tables_data:
			hs += "-- table_data: %s\n" % (table_data)
		hs += nl
	ps = "" # ps = part_string
	for part in parts:
		if header_type == 'config':
			ps += "-- part\n"
		else:
			ps += "-- part: %s\n" % (part["number"])
		if part["single_transaction"]:
			ps += "-- single_transaction\n"
		else:
			ps += "-- not single_transaction\n"
		if part.get("data") and header_type == 'config':
			ps += nl
			ps += "%s\n" % (part["data"])
	if header_type == 'config':
		hs += "-- end header_data\n"
		hs += nl
		hs += ps
	else:
		hs += ps
		hs += nl
		hs += "-- end header_data\n"
		hs += nl
	return hs

def get_command(command, name, element_name="sqldist file"):
	cs = "\n" # cs = command_string
	cs += "--\n"
	cs += "-- %s: %s\n" % (element_name, name)
	cs += "--\n"
	cs += "\n"
	cs += command.strip()
	cs += "\n"
	cs += ";-- end %s: %s\n" % (element_name, name)
	return cs

def diff(source, target, start_string="-- ", colored=False, from_file="removeline542358", to_file="removeline542358"):
	dc = difflib.unified_diff(source, target, fromfile=from_file, tofile=to_file) # dc = diff_c
	r = "" # r = result
	for d in dc:
		if "removeline542358" in d:
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
	return d + "\n"
