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

import pg_project

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

def check_pgdist_installed(dbname, conn):
	cursor = conn.cursor()
	cursor.execute("SELECT nspname FROM pg_namespace WHERE nspname = 'pgdist';")
	for row in cursor:
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
	if not check_pgdist_installed(dbname, conn):
		logging.verbose("Create PGdist info schema into database %s" % (dbname,))
		cursor.execute(CREATE_PGDIST)
	while True:
		cursor.execute("SELECT version FROM pgdist.pgdist_version;")
		for row in cursor.fetchall():
			cur_version = row["version"]
			if cur_version >= PGDIST_VERSION:
				return
			logging.verbose("Update PGdist info schema into database %s to version %d" % (dbname, cur_version+1))
			cursor.execute(PGDIST_UPDATES[cur_version-1])
			cursor.execute("UPDATE pgdist.pgdist_version SET version=%s;", (cur_version+1,))

def pgdist_update(dbname, conninfo):
	if dbname:
		dbs = [dbname]
	else:
		dbs = list_database(conninfo)
	
	for db in dbs:
		conn = connect(conninfo, db)
		cursor = conn.cursor()
		if check_pgdist_installed(db, conn):
			pgdist_install(db, conn)
		conn.close()

def create_role(conn, role):
	logging.debug("check role: %s" % (role,))
	cursor = conn.cursor()
	cursor.execute("SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname=%s;", (role.name,))
	row = cursor.fetchone()
	if row:
		if not row["rolcanlogin"] and role.login:
			logging.verbose("ALTER ROLE %s LOGIN;" % (role.name,))
			cursor.execute("ALTER ROLE %s LOGIN;" % (role.name,))
		if row["rolcanlogin"] and role.nologin:
			logging.verbose("ALTER ROLE %s NOLOGIN;" % (role.name,))
			cursor.execute("ALTER ROLE %s NOLOGIN;" % (role.name,))
	else:
		login = ""
		if role.login:
			login = "LOGIN"
		if role.nologin:
			login = "NOLOGIN"
		if role.password:
			password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits ) for _ in range(12))
			print("CREATE ROLE %s %s" % (role.name, login))
			cursor.execute("CREATE ROLE %s %s PASSWORD %%s;" % (role.name, login), (password, ))
			open("/etc/lbox/postgresql/roles/"+role.name, 'w').write("PGPASSWORD=%s\n" % (password, ))
		else:
			print("CREATE ROLE %s %s" % (role.name, login))
			cursor.execute("CREATE ROLE %s %s;" % (role.name, login))

def install(dbname, project, ver, conninfo, directory, create_db, is_require):
	if ver.parts and create_db:
		if not dbname in list_database(conninfo):
			conn = connect(conninfo)
			for part in ver.parts:
				for role in part.roles:
					create_role(conn, role)
			cursor = conn.cursor()
			cmd = "CREATE DATABASE %s %s" % (dbname, ver.parts[0].dbparam)
			print(cmd)
			cursor.execute(cmd)
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
			create_role(conn, role)
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
			create_role(conn, role)
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
	if pg.check_pgdist_installed(db, conn):
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
