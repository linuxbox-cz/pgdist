# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import logging
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import subprocess

import random
import string

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

PGDIST_VERSION = 1

CREATE_PGDIST = """
CREATE SCHEMA pgdist;

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

INSERT INTO pgdist.pgdist_version VALUES (1);
INSERT INTO pgdist.history (project, version, part, comment) VALUES ('pgdist', 1, 1, 'Create PGdist info schema.');

"""

class PgError(Exception):
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

def run(c, conninfo, cmd=None, single_transaction=True, dbname=None, file=None, debug=False):
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

	logging.debug(args)
	process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
	output, unused_err = process.communicate(cmd)
	retcode = process.poll()
	if retcode != 0:
		output = "\n".join(output.split("\n")[-40:])
		print(output)
		logging.error("Command fail")
		sys.exit(1)
		#raise PgError(retcode, c, output=output)
	else:
		if debug:
			print(output)
	return (retcode, output)


def connect(conninfo, dbname=None):
	conn = psycopg2.extras.DictConnection(conninfo.dsn(dbname))
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
	cursor.execute("SELECT nspname FROM pg_namespace WHERE nspname = 'pgdist';")
	for row in cursor:
		return True
	return False

def check_pgdist_version(conn):
	cursor = conn.cursor()
	cursor.execute("SELECT version FROM pgdist.pgdist_version;")
	for row in cursor:
		if row["version"] < PGDIST_VERSION:
			logging.error("Error: old version pgdist in database, run pgdist-update")
			sys.exit(1)
		if row["version"] > PGDIST_VERSION:
			logging.error("Error: old version pgdist, update pgdist")
			sys.exit(1)
		return True

def pgdist_install(conn):
	cursor = conn.cursor()
	if not check_pgdist_installed(conn):
		logging.debug("Create PGdist info schema into database")
		cursor.execute(CREATE_PGDIST)
	# TODO will make update after we have updates

def pgdist_update(dbname, conninfo):
	if dbname:
		dbs = [dbname]
	else:
		dbs = list_database(conninfo)
	
	for db in dbs:
		conn = connect(conninfo, dbname)
		cursor = conn.cursor()
		pgdist_install(conn)
		conn.close()

def create_role(conn, role):
	logging.debug("check role: %s" % (role,))
	cursor = conn.cursor()
	cursor.execute("SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname=%s;", (role.name,))
	row = cursor.fetchone()
	if row:
		if not row["rolcanlogin"] and role.login:
			logging.debug("ALTER ROLE %s LOGIN;" % (role.name,))
			cursor.execute("ALTER ROLE %s LOGIN;" % (role.name,))
		if row["rolcanlogin"] and role.nologin:
			logging.debug("ALTER ROLE %s NOLOGIN;" % (role.name,))
			cursor.execute("ALTER ROLE %s NOLOGIN;" % (role.name,))
	else:
		if role.login:
			login = "LOGIN"
		if role.nologin:
			login = "NOLOGIN"
		if role.password:
			password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits ) for _ in range(12))
			logging.debug("CREATE ROLE %s %s" % (role.name, login))
			cursor.execute("CREATE ROLE %s %s PASSWORD %%s;" % (role.name, login), (password, ))
			open("/etc/lbox/postgresql/roles/"+role.name, 'w').write("PGPASSWORD=%s\n" % (password, ))
		else:
			cursor.execute("CREATE ROLE %s %s;" % (role.name, login))

def install(dbname, project, ver, conninfo, directory, verbose):
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(conn)
	for part in ver.parts:
		for role in part.roles:
			create_role(conn, role)
	for part in ver.parts:
		logging.info("install %s to %s version %s part %d/%d" % (project.name, dbname, str(ver.version), part.part, len(ver.parts)))
		run("psql", conninfo, dbname=dbname, file=os.path.join(directory, part.fname), single_transaction=part.single_transaction, debug=verbose)
		cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES (%s, %s, %s, %s);",
			(project.name, str(ver.version), part.part, "installed new version %s, part %d/%d" % (str(ver.version), part.part, len(ver.parts))))
		cursor.execute("UPDATE pgdist.installed SET version=%s, part=%s, parts=%s WHERE project=%s RETURNING *;",
			(str(ver.version), part.part, len(ver.parts), project.name))
		if not cursor.fetchone():
			cursor.execute("INSERT INTO pgdist.installed (project, version, part, parts) VALUES (%s, %s, %s, %s);",
				(project.name, str(ver.version), part.part, len(ver.parts)))


def update(dbname, project, update, conninfo, directory, verbose):
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(conn)
	for part in update.parts:
		for role in part.roles:
			create_role(conn, role)
	for part in update.parts:
		logging.info("update %s in %s %s > %s part %d/%d" % (project.name, dbname, str(update.version_old), str(update.version_new), part.part, len(ver.parts)))
		run("psql", conninfo, dbname=dbname, file=os.path.join(directory, part.fname), single_transaction=part.single_transaction, debug=verbose)
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
	pgdist_install(conn)
	logging.info("clean %s from %s" % (project.name, dbname))
	cursor.execute("DELETE FROM pgdist.installed WHERE project = %s RETURNING *", (project_name,))
	for row in cursor.fetchall():
		cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES (%s, %s, %s, %s);",
			(project_name, row["version"], row["part"], "clean info of project"))
	conn.close()

def set_version(project_name, dbname, version, conninfo):
	conn = connect(conninfo, dbname)
	cursor = conn.cursor()
	pgdist_install(conn)
	logging.info("set version %s in %s to %s" % (project_name, dbname, version))
	cursor.execute("INSERT INTO pgdist.history (project, version, part, comment) VALUES (%s, %s, %s, %s);",
		(project_name, version, 1, "set version %s" % (version,)))
	cursor.execute("UPDATE pgdist.installed SET version=%s, from_version=NULL, part=1, parts=1 WHERE project=%s RETURNING *;",
		(version, project_name))
	if not cursor.fetchone():
		cursor.execute("INSERT INTO pgdist.installed (project, version, part, parts) VALUES (%s, %s, 1, 1);",
			(project_name, version))
