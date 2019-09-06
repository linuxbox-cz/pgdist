def get_header(header_data):
	# nl = new_line
	if header_data["type"] == 'config':
		nl = "\n"
	else:
		nl = "--\n"

	# hs = header_string
	hs = nl

	if header_data["type"] == 'update':
		hs += "-- pgdist update\n"
	else:
		hs += "-- pgdist project\n"

	hs += "-- name: %s\n" % (header_data["project_name"])
	hs += nl

	if header_data.get("version"):
		hs += "-- version: %s\n" % (header_data["version"])
		hs += nl

	if header_data.get("old_version") and header_data.get("new_version"):
		hs += "-- old version: %s\n" % (header_data["old_version"])
		hs += "-- new version: %s\n" % (header_data["new_version"])
		hs += nl

	if header_data.get("dbparam"):
		hs += "-- dbparam: %s\n" % (header_data["dbparam"])
		hs += nl

	if header_data["roles"]:
		for role in header_data["roles"]:
			hs += "-- role: %s\n" % (role)
		hs += nl

	if header_data["requires"]:
		for require in header_data["requires"]:
			hs += "-- require: %s\n" % (require)
		hs += nl

	if header_data.get("tables_data"):
		for table_data in header_data["tables_data"]:
			hs += "-- table_data: %s\n" % (table_data)
		hs += nl

	# ps = part_string
	ps = ""

	for part in header_data["parts"]:
		if header_data["type"] == 'config':
			ps += "-- part\n"
		else:
			ps += "-- part: %s\n" % (part["number"])


		if part["single_transaction"]:
			ps += "-- single_transaction\n"
		else:
			ps += "-- not single_transaction\n"

		if part.get("data") and header_data["type"] == 'config':
			ps += nl
			ps += "%s" % (part["data"])

	if header_data["type"] == 'config':
		hs += "-- end header_data\n"
		hs += nl
		hs += ps
	else:
		hs += ps
		hs += nl
		hs += "-- end header_data\n"

	return hs
