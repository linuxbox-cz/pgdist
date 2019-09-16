import difflib

import color

def get_header(project_name, header_type, parts, roles=None, requires=None, version=None, old_version=None, new_version=None, dbparam=None, tables_data=None):
	hs = "--\n" # hs = header_string
	hs += "-- pgdist %s\n" % (header_type)
	hs += "-- name: %s\n" % (project_name)
	hs += "--\n"
	if version:
		hs += "-- version: %s\n" % (version)
		hs += "--\n"
	if old_version and new_version:
		hs += "-- old version: %s\n" % (old_version)
		hs += "-- new version: %s\n" % (new_version)
		hs += "--\n"
	if dbparam:
		hs += "-- dbparam: %s\n" % (dbparam)
		hs += "--\n"
	if roles:
		for role in roles:
			hs += "-- role: %s\n" % (role)
		hs += "--\n"
	if requires:
		for require in requires:
			hs += "-- require: %s\n" % (require)
		hs += "--\n"
	if tables_data:
		for table_data in tables_data:
			hs += "-- table_data: %s\n" % (table_data)
		hs += "--\n"
	ps = "" # ps = part_string
	get_parts(parts, header_type)
	if header_type == 'config':
		hs += "-- end header_data\n"
		hs += "--\n"
		hs += ps
	else:
		hs += ps
		hs += "--\n"
		hs += "-- end header_data\n"
		hs += "--\n"
	return hs

def get_parts(parts, header_type):
	ps = ""
	for part in parts:
		ps += "-- part: %s\n" % (part["number"])
		if part["single_transaction"]:
			ps += "-- single_transaction\n"
		else:
			ps += "-- not single_transaction\n"
		if part.get("data") and header_type == 'config':
			ps += "\n"
			ps += "%s\n" % (part["data"])
	return ps

def get_command(command, name, element_name="sqldist file"):
	cs = "\n" # cs = command_string
	cs += "--\n"
	cs += "-- %s: %s\n" % (element_name, name)
	cs += "--\n"
	cs += "\n"
	cs += command.strip() + "\n"
	cs += "\n"
	cs += ";-- end %s: %s\n" % (element_name, name)
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
