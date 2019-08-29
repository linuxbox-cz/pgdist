# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import config
import logging
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import subprocess

import random
import string

import pg_project

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

PGDIST_VERSION = 1

CREATE_PGDIST = """
CREATE SCHEMA IF NOT EXISTS pgdist;

CREATE TABLE pgdist.pgdist_version (
	version INTEGER NOT NULL
);

CREATE TABLE pgdist.installed (
	project TEXT NOT NULL PRIMARY KEY,
	version TEXT NOT NULL,
	from_version TEXT,
	part INTEGER NOT NULL,
	parts INTEGER NOT NULL
);

CREATE TABLE pgdist.history (
	project TEXT NOT NULL,
	ts TIMESTAMPTZ DEFAULT NOW(),
	version TEXT NOT NULL,
	part INTEGER NOT NULL,
	comment TEXT
);

INSERT INTO pgdist.pgdist_version VALUES (%d);
INSERT INTO pgdist.history (project, version, part, comment) VALUES ('pgdist', %d, 1, 'Create PGdist info schema.');

""" % (PGDIST_VERSION, PGDIST_VERSION)

PGDIST_UPDATES = [
]

class PgError(Exception):
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

def run(c, conninfo, cmd=None, single_transaction=True, dbname=None, file=None):
	args = [c]
	if c == "psql":
		args.append("--no-psqlrc")
		args.append("--echo-queries")
		args.append("--set")
		args.append("ON_ERROR_STOP=1")
	if dbname:
		args.append(dbname)
	else:
		args.append(conninfo.dbname)
	if conninfo.port:
		args.append("--port")
		args.append(conninfo.port)
	if conninfo.user:
		args.append("--username")
		args.append(conninfo.user)
	if single_transaction:
		args.append("--single-transaction")
	if file:
		args.append("--file")
		args.append(file)
	if c == "pg_dump":
		args.append("--schema-only")

	logging.verbose("run: %s" % (" ".join(args)),)
	process = subprocess.Popen(args, bufsize=8192, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
	output, unused_err = process.communicate(cmd)
	retcode = process.poll()
	logging.debug(output)
	if retcode != 0:
		output = "\n".join(output.split("\n")[-40:])
		logging.error("Command fail: %s\n%s" % (" ".join(args), output))
		sys.exit(1)
	return (retcode, output)

def connect(conninfo, dbname=None):
	try:
		conn = psycopg2.extras.DictConnection(conninfo.dsn(dbname))
	except Exception as e:
		logging.error("Error connect: %s" % (e,))
		sys.exit(1)
	conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
	return conn

def list_database(conninfo):
	databases = []
	conn = connect(conninfo)
	cursor = conn.cursor()
	cursor.execute("SELECT datname FROM pg_database WHERE datname NOT IN ('template0') ORDER BY datname;")
	for row in cursor:
		databases.append(row["datname"])
	cursor.close()
	conn.close()

	return databases

def check_pgdist_installed(conn):
	cursor = conn.cursor()
	schema = False
	tables_count = 0

	cursor.execute("SELECT nspname FROM pg_catalog.pg_namespace WHERE nspname = 'pgdist';")
	for row in cursor:
		schema = True

	cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'pgdist' AND table_name in ('history', 'pgdist_version', 'installed');")
	for row in cursor:
		if row["count"] == 3 and schema:
			return True

	return False

def check_pgdist_version(dbname, conn):
	cursor = conn.cursor()
	cursor.execute("SELECT version FROM pgdist.pgdist_version;")
	for row in cursor:
		if row["version"] < PGDIST_VERSION:
			logging.error("Error: old version pgdist in database %s, run pgdist-update" % (dbname,))
			sys.exit(1)
		if row["version"] > PGDIST_VERSION:
			logging.error("Error: old version pgdist for database %s, update pgdist" % (dbname,))
			sys.exit(1)
		return True

def pgdist_install(dbname, conn):
	cursor = conn.cursor()
	if not check_pgdist_installed(conn):
		logging.verbose("Create PGdist info schema into database %s" % (dbname,))
		cursor.execute(CREATE_PGDIST)

	while True:
		cursor.execute("SELECT version FROM pgdist.pgdist_version;")
		version = cursor.fetchall()

		if not version:
			cursor.execute("INSERT INTO pgdist.pgdist_version VALUES (%s);", (PGDIST_VERSION,))
			cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES ('pgdist', %s, 1, 'Create PGdist info schema.');", (PGDIST_VERSION,))

		for row in version:
			cur_version = row["version"]
			if cur_version >= PGDIST_VERSION:
				return
			logging.verbose("Update PGdist info schema into database %s to version %d" % (dbname, cur_version+1))
			cursor.execute(PGDIST_UPDATES[cur_version-1])
			cursor.execute("UPDATE pgdist.pgdist_version SET version=%s;", (cur_version+1,))

def get_history(conninfo, project_name, dbname):
	history = []
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(None, conn)
	logging.verbose("getting history from db: %s" % (dbname))

	if project_name:
		cursor.execute("SELECT project, ts::TEXT, version, part::TEXT, comment FROM pgdist.history WHERE project = %s ORDER BY ts ASC;", (project_name,))
	else:
		cursor.execute("SELECT project, ts::TEXT, version, part::TEXT, comment FROM pgdist.history ORDER BY ts ASC;")

	for row in cursor.fetchall():
		history.append([dbname] + row)
	return history

def installed_history(project_name, dbname, conninfo):
	history = []

	if dbname:
		history = get_history(conninfo, project_name, dbname)
	else:
		for database in list_database(conninfo):
			history += get_history(conninfo, project_name, database)

	headers = ["database", "project", "ts", "version", "part", "comment"]
	col_max_len = []

	for header in headers:
		col_max_len.append(len(header))

	for row in history:
		for i, col in enumerate(col_max_len):
			if len(row[i]) > col:
				col_max_len[i] = len(row[i])

	total_length = -1 #last space

	for i in col_max_len:
		total_length += i

	print

	for i, col in enumerate(headers):
		print("%s%s" % (col, " " * (col_max_len[i] - len(col)))),
	print

	print("=" * (total_length + len(headers)))

	for row in history:
		for i, col in enumerate(row):
			print("%s%s" % (col, " " * (col_max_len[i] - len(col)))),
		print
	print("=" * (total_length + len(headers)))

def pgdist_update(dbname, conninfo):
	if dbname:
		dbs = [dbname]
	else:
		dbs = list_database(conninfo)
	
	for db in dbs:
		conn = connect(conninfo, db)
		cursor = conn.cursor()
		if check_pgdist_installed(conn):
			pgdist_install(db, conn)
		conn.close()

def update_password(role_name, cursor):
	password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits ) for _ in range(12))
	print("ALTER ROLE %s PASSWORD" % (role_name,))
	cursor.execute("ALTER ROLE %s PASSWORD %%s;" % (role_name,), (password,))
	open(os.path.join(config.get_password_path(), role_name), 'w').write("PGPASSWORD=%s\n" % (password, ))

def create_role(conn, conn_db, role, project_name, version, part):
	logging.debug("check role: %s" % (role,))
	changed = False
	cursor = conn.cursor()
	cursor.execute("SELECT rolname, rolcanlogin, passwd FROM pg_roles LEFT JOIN pg_shadow ON usename=rolname WHERE rolname=%s;", (role.name,))
	row = cursor.fetchone()
	if row:
		if not row["rolcanlogin"] and role.login:
			changed = True
			logging.verbose("ALTER ROLE %s LOGIN;" % (role.name,))
			cursor.execute("ALTER ROLE %s LOGIN;" % (role.name,))
		if row["rolcanlogin"] and role.nologin:
			changed = True
			logging.verbose("ALTER ROLE %s NOLOGIN;" % (role.name,))
			cursor.execute("ALTER ROLE %s NOLOGIN;" % (role.name,))
		if role.login and role.password and not row["passwd"]:
			changed = True
			update_password(role.name, cursor)
		if changed:
			conn_db.cursor().execute("INSERT INTO pgdist.history(project, version, part, comment) VALUES(%s, %s, %s, %s)", (project_name, str(version), part, "role changed: %s" % (str(role))))
	else:
		login = ""
		if role.login:
			login = "LOGIN"
		if role.nologin:
			login = "NOLOGIN"

		print("CREATE ROLE %s %s" % (role.name, login))
		cursor.execute("CREATE ROLE %s %s;" % (role.name, login))

		if role.password:
			update_password(role.name, cursor)
		conn_db.cursor().execute("INSERT INTO pgdist.history(project, version, part, comment) VALUES(%s, %s, %s, %s)", (project_name, str(version), part, "role added: %s" % (str(role))))
	conn_db.close()

def install(dbname, project, ver, conninfo, directory, create_db, is_require):
	if ver.parts and create_db:
		if not dbname in list_database(conninfo):
			conn = connect(conninfo)
			cursor = conn.cursor()
			cmd = "CREATE DATABASE %s %s" % (dbname, ver.parts[0].dbparam)
			print(cmd)
			cursor.execute(cmd)

			for part in ver.parts:
				for role in part.roles:
					create_role(conn, connect(conninfo, dbname), role, project.name, ver.version, part.part)
			conn.close()
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(dbname, conn)
	for part in ver.parts:
		for require in part.requires:
			cursor.execute("SELECT 1 FROM pgdist.installed WHERE project=%s", (require,))
			if not cursor.fetchall():
				pg_project.install(require, dbname, None, conninfo, directory, create_db, True)
	for part in ver.parts:
		for role in part.roles:
			create_role(conn, connect(conninfo, dbname), role, project.name, ver.version, part.part)
	for part in ver.parts:
		str_part = ""
		str_require = ""
		if len(ver.parts) > 1:
			str_part = " part %d/%d" % (part.part, len(ver.parts))
		if is_require:
			str_require = " require"
		print("Install%s %s %s%s to %s" % (str_require, project.name, str(ver.version), str_part, dbname))

		run("psql", conninfo, dbname=dbname, file=os.path.join(directory, part.fname), single_transaction=part.single_transaction)
		cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES (%s, %s, %s, %s);",
			(project.name, str(ver.version), part.part, "installed new version %s, part %d/%d" % (str(ver.version), part.part, len(ver.parts))))
		cursor.execute("UPDATE pgdist.installed SET version=%s, part=%s, parts=%s WHERE project=%s RETURNING *;",
			(str(ver.version), part.part, len(ver.parts), project.name))
		if not cursor.fetchone():
			cursor.execute("INSERT INTO pgdist.installed (project, version, part, parts) VALUES (%s, %s, %s, %s);",
				(project.name, str(ver.version), part.part, len(ver.parts)))


def update(dbname, project, update, conninfo, directory):
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(dbname, conn)
	for part in update.parts:
		for require in part.requires:
			cursor.execute("SELECT 1 FROM pgdist.installed WHERE project=%s", (require,))
			if not cursor.fetchall():
				pg_project.install(require, dbname, None, conninfo, directory, False, True)
	for part in update.parts:
		for role in part.roles:
			create_role(conn, connect(conninfo, dbname), role, project.name, update.version, part.part)
	for part in update.parts:
		if len(update.parts) == 1:
			print("Update %s in %s %s > %s" % (project.name, dbname, str(update.version_old), str(update.version_new)))
		else:
			print("Update %s in %s %s > %s part %d/%d" % (project.name, dbname, str(update.version_old), str(update.version_new), part.part, len(update.parts)))
		run("psql", conninfo, dbname=dbname, file=os.path.join(directory, part.fname), single_transaction=part.single_transaction)
		cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES (%s, %s, %s, %s);",
			(project.name, str(update.version_new), part.part, "updated from version %s to %s, part %d/%d" % (str(update.version_new), str(update.version_old), part.part, len(update.parts))))
		cursor.execute("UPDATE pgdist.installed SET version=%s, from_version=%s,  part=%s, parts=%s WHERE project=%s RETURNING *;",
			(str(update.version_new), str(update.version_old), part.part, len(update.parts), project.name))
		if not cursor.fetchone():
			cursor.execute("INSERT INTO pgdist.installed (project, version, part, parts) VALUES (%s, %s, %s, %s);",
				(project.name, str(update.version), part.part, len(update.parts)))

def clean(project_name, dbname, conninfo):
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(dbname, conn)
	logging.info("clean %s from %s" % (project_name, dbname))
	cursor.execute("DELETE FROM pgdist.installed WHERE project = %s RETURNING *", (project_name,))
	for row in cursor.fetchall():
		cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES (%s, %s, %s, %s);",
			(project_name, row["version"], row["part"], "clean info of project"))
	conn.close()

def set_version(project_name, dbname, version, conninfo):
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(dbname, conn)
	logging.info("set version %s in %s to %s" % (project_name, dbname, version))
	cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES (%s, %s, %s, %s);",
		(project_name, version, 1, "set version %s" % (version,)))
	cursor.execute("UPDATE pgdist.installed SET version=%s, from_version=NULL, part=1, parts=1 WHERE project=%s RETURNING *;",
		(version, project_name))
	if not cursor.fetchone():
		cursor.execute("INSERT INTO pgdist.installed (project, version, part, parts) VALUES (%s, %s, 1, 1);",
			(project_name, version))
	conn.close()

def get_version(project_name, dbname, conninfo):
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(dbname, conn)
	logging.debug("get version %s in %s" % (project_name, dbname))
	cursor.execute("SELECT version FROM pgdist.installed WHERE project=%s;",
		(project_name, ))
	for row in cursor:
		return row["version"]
		conn.close()
	conn.close()
	return None

def check_installed(dbname, project_name, conninfo):
	conn = connect(conninfo, dbname)
	if pg.check_pgdist_installed(conn):
		pg.check_pgdist_version(db, conn)
		cursor = conn.cursor()
		cursor.execute("SELECT 1 FROM pgdist.installed WHERE project=%s", (project_name,))
		for row in cursor:
			conn.close()
			return True
	conn.close()
	return False

def check_installed2(cursor, project_name):
	cursor.execute("SELECT 1 FROM pgdist.installed WHERE project=%s", (project_name,))
	for row in cursor:
		conn.close()
		return True
	return False
