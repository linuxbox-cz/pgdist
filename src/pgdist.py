#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import atexit
import argparse
import subprocess
import logging
import logging.handlers

reload(sys)
sys.setdefaultencoding('utf-8')

description = """
PGdist - distribute PotgreSQL functions, tables, etc...
PGdist Devel - develop PostgreSQL project

    init PROJECT [DIRECTORY] - initialize pgdist project
    create-schema SCHEMA - create new schema directories
    status - show new files and removed files compared to pg_project.sql
    add FILE1 [FILE2 ...] - add files to pg_project.sql
    rm FILE1 [FILE2 ...] - removed files from pg_project.sql

    test-load - load project to testing postgres
    create-version VERSION [GIT_TAG] - create version files
    create-update GIT_TAG NEW_VERSION - create update files with differencies
                                          - GIT_TAG - old version tag
                                          - NEW_VERSION - version created by create-version
    test-update GIT_TAG NEW_VERSION - load old and new version and compare it
                                          - GIT_TAG - old version tag
                                          - NEW_VERSION - version created by create-version

    diff-db PGCONN [GIT_TAG] - diff project and database
    diff-db-file PGCONN FILE - diff file and database
    diff-file-db FILE PGCONN - diff database and file

    role-list - print roles in project
    role-add NAME [login|nologin] [password] - add role to project
    role-change NAME [login|nologin] [password] - change role
    role-rm NAME - remove role from project, not remove from databases

    require-add PROJECT GIT GIT_TREE_ISH - add require to another project
    require-rm PROJECT - remove require to another project

    dbparam-set [PARAM [...]] - parameters with create a database (e.g.: OWNER lbadmin ...)
    dbparam-get - print parameters to create a database

    data-add TABLE [COLUMN1 [...]] - add table to compare data
    data-rm TABLE - remove table to compare data
    data-list - list table of data compare

PGdist Server - manage projects in PostgreSQL database

    list [PROJECT [DBNAME]] - show list of installed projects in databases
    install PROJECT DBNAME [VERSION] - install project to database
    check-update [PROJECT [DBNAME [VERSION]]] - check update project
    update [PROJECT [DBNAME [VERSION]]] - update project
    clean PROJECT [DBNAME] - remove all info about project
    set-version PROJECT DBNAME VERSION - force change version without run scripts
    pgdist-update [DBNAME] - update pgdist version in database

PGCONN - ssh connection + connection URI, see:
    https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING
    without string 'postgresql://'
    examples:
        localhost/mydb - connect to mydb
        root@server//user@/mydb - connect to server via ssh and next connect to postgres as user into mydb

Configuration:
    connection to testing database in file "~/.pgdist" (or ".pgdist" in project path) with content:
        [pgdist]
        test_db: user@host/dbname

        test_db - PGCONN to testing postgres, user has to create databases and users
"""

def main():
	logging.basicConfig(format="%(message)s")
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=description, add_help=False)
	less = False

	# common argument
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="count", default=0)
	parser.add_argument("-?", "--help", dest="help", action="store_true", help="show this help message and exit")
	parser.add_argument("cmd", nargs="?")
	parser.add_argument("args", nargs="*")

	# develop projects
	parser.add_argument("--less", help="print output in less", action="store_true")
	parser.add_argument("--noless", help="don't print output in less", action="store_true")
	parser.add_argument("--all", help="use all files", action="store_true")
	parser.add_argument("-f", "--force", help="overwriting and removing files", action="store_true")
	parser.add_argument("-c", "--config", help="configuration file")
	parser.add_argument("--color", help="never, always or auto colorred output", default="auto", choices=["auto", "never", "always"])
	parser.add_argument("--swap", help="Swap compare data, commands diff-...", default=False, action="store_true")
	parser.add_argument("--gitversion", help="use as version for git tag")
	parser.add_argument("--no-owner", dest="no_owner", help="do not dump and compare ownership of objects", action="store_true")
	parser.add_argument("--no-acl", dest="no_acl", help="do not dump and compare access privileges (grant/revoke commands)", action="store_true")
	parser.add_argument("--diff-raw", dest="diff_raw", help="compare raw SQL dumps", action="store_true")
	parser.add_argument("--no-clean", dest="no_clean", help="no clean test database after load/update test", action="store_true", default=False)
	parser.add_argument("--cache", dest="cache", help="cache dump remote database for 4 hours", action="store_true", default=False)
	parser.add_argument("--pg_extractor", dest="pg_extractor", help="Dump by pg_extractor, compare by diff -r", action="store_true")
	parser.add_argument("--pg_extractor_basedir", dest="pg_extractor_basedir", help="Dump by pg_extractor do directory PG_EXTRACTOR_BASEDIR")
	parser.add_argument("--pre-load", dest="pre_load", help="SQL file to load before load project")
	parser.add_argument("--post-load", dest="post_load", help="SQL file to load after load project")
	parser.add_argument("--pre-remoted-load", dest="pre_remoted_load", help="SQL file to load before load remote dump, command: diff-db")
	parser.add_argument("--post-remoted-load", dest="post_remoted_load", help="SQL file to load after project, command: diff-db, path unversion install")
	parser.add_argument("--pre-load-old", dest="pre_load_old", help="SQL file to load before load old version of the project")
	parser.add_argument("--post-load-old", dest="post_load_old", help="SQL file to load after load old version of the project")
	parser.add_argument("--pre-load-new", dest="pre_load_new", help="SQL file to load before load new version of the project")
	parser.add_argument("--post-load-new", dest="post_load_new", help="SQL file to load after load new version of the project")

	# install projects
	parser.add_argument("--showall", help="show all versions", action="store_true")
	parser.add_argument("-d", "--dbname", dest="dbname", help="Specifies the name of the database to connect to.")
	parser.add_argument("-h", "--host", dest="host", help="Specifies the host name of the machine on which the server is running.")
	parser.add_argument("-p", "--port", dest="port", help="Specifies the TCP port or the local Unix-domain socket file.")
	parser.add_argument("-U", "--username", dest="user", help="Connect to the database as the user username.")
	parser.add_argument("-C", "--create", dest="create", help="Create the database.", action="store_true")
	parser.add_argument("--directory", help="directory contains script install and update", default="/usr/share/pgdist/install")
	parser.add_argument("--syslog-facility", dest="syslog_facility", help="syslog facility")
	parser.add_argument("--syslog-ident", dest="syslog_ident", help="syslog ident")

	args = parser.parse_args()

	if args.help:
		parser.print_help()
		sys.exit(1)

	VERBOSE = logging.DEBUG + 5
	logging.addLevelName(VERBOSE, "VERBOSE")
	def verbose(message, *args, **kws):
		if logging.getLogger().root.isEnabledFor(VERBOSE):
			logging.getLogger().root._log(VERBOSE, message, args, **kws) 
	logging.verbose = verbose
	if args.verbose > 2:
		logging.basicConfig(format="%(asctime)-15s %(filename)s:%(lineno)d %(message)s")
		logging.getLogger().setLevel(logging.DEBUG)
		logging.debug("verbosity debug turned on")
	elif args.verbose > 0:
		logging.getLogger().setLevel(VERBOSE)
		logging.verbose("verbosity turned on")
	else:
		logging.getLogger().setLevel(logging.INFO)

	if args.syslog_facility or args.syslog_ident:
		handler = logging.handlers.SysLogHandler(facility=args.syslog_facility, address='/dev/log')
		if args.syslog_ident:
			handler.setFormatter(logging.Formatter(args.syslog_ident+": %(message)s"))
		logging.getLogger().addHandler(handler)

	if args.cmd in ("init", "create-schema", "status", "test-load", "create-version", "add", "rm",
		"create-update", "test-update",
		"diff-db", "diff-db-file", "diff-file-db",
		"role-list", "role-add", "role-change", "role-rm",
		"require-add", "require-rm", "dbparam-set", "dbparam-get",
		"data-add", "data-rm", "data-list"):

		sys.path.insert(1, os.path.join(sys.path[0], "dev"))
		import color
		import address
		import config
		import pg_parser
		import pg_project
		import pg_extractor as pg_extractor_m

		if args.less:
			less = True
		elif args.noless or args.cmd not in ("diff-db", "diff-db-file", "diff-file-db"):
			less = False
		else:
			less = sys.stdout.isatty()

		if less:
			pager = subprocess.Popen(["less", "-FKSMIR"], bufsize=1, stdin=subprocess.PIPE, stdout=sys.stdout)
			sys.stdout = pager.stdin
			atexit.register(close_less, pager)

		config.load(args.config)
		if less and args.color == "auto":
			color.set("always")
		else:
			color.set(args.color)

	if args.cmd in ("list", "install", "check-update", "update", "clean", "set-version", "pgdist-update"):
		sys.path.insert(1, os.path.join(sys.path[0], "mng"))
		import conninfo
		import pg_project

	if args.pg_extractor:
		pg_extractor = pg_extractor_m.PG_extractor(args.pg_extractor_basedir)
	else:
		pg_extractor = None

	# develop projects
	if args.cmd == "init" and len(args.args) in (1, 2,):
		(project_name, directory) = args_parse(args.args, 2)
		if not directory:
			directory = os.getcwd()
		pg_project.project_init(project_name, directory)

	elif args.cmd == "create-schema" and len(args.args) in (1,):
		(schema_name,) = args_parse(args.args, 1)
		pg_project.create_schema(schema_name)

	elif args.cmd == "status" and len(args.args) in (0,):
		pg_project.status()

	elif args.cmd == "add":
		pg_project.add(args.args, args.all)

	elif args.cmd ==  "rm":
		pg_project.rm(args.args, args.all)

	elif args.cmd == "test-load" and len(args.args) in (0,):
		pg_project.test_load(not args.no_clean, args.pre_load, args.post_load, pg_extractor=pg_extractor)

	elif args.cmd == "create-version" and len(args.args) in (1, 2,):
		(version, git_tag) = args_parse(args.args, 2)
		pg_project.create_version(version, git_tag, args.force)

	elif args.cmd == "create-update" and len(args.args) in (2,):
		(git_tag, new_version) = args_parse(args.args, 2)
		pg_project.create_update(git_tag, new_version, args.force, args.gitversion, clean=not args.no_clean, pre_load=args.pre_load, post_load=args.post_load,
			pre_load_old=args.pre_load_old, pre_load_new=args.pre_load_new, post_load_old=args.post_load_old, post_load_new=args.post_load_new)

	elif args.cmd == "test-update" and len(args.args) in (2,):
		(git_tag, new_version) = args_parse(args.args, 1)
		pg_project.test_update(git_tag, new_version, args.gitversion, not args.no_clean, pre_load=args.pre_load, post_load=args.post_load,
			pre_load_old=args.pre_load_old, pre_load_new=args.pre_load_new, post_load_old=args.post_load_old, post_load_new=args.post_load_new,
			pg_extractor=pg_extractor)

	elif args.cmd == "diff-db" and len(args.args) in (1, 2):
		(pgconn, git_tag) = args_parse(args.args, 2)
		pg_project.diff_pg(address.Address(pgconn), git_tag, args.diff_raw, not args.no_clean, args.no_owner, args.no_acl,
			pre_load=args.pre_load, post_load=args.post_load, pre_remoted_load=args.pre_remoted_load, post_remoted_load=args.post_remoted_load,
			swap=args.swap, pg_extractor=pg_extractor, cache=args.cache)

	elif args.cmd == "diff-db-file" and len(args.args) in (2,):
		(pgconn, file) = args_parse(args.args, 2)
		pg_project.diff_pg_file(address.Address(pgconn), file, args.diff_raw, not args.no_clean, args.no_owner, args.no_acl,
			pre_load=args.pre_load, post_load=args.post_load, pre_remoted_load=args.pre_remoted_load, post_remoted_load=args.post_remoted_load,
			swap=args.swap, pg_extractor=pg_extractor, cache=args.cache)

	elif args.cmd == "diff-file-db" and len(args.args) in (2,):
		(file, pgconn) = args_parse(args.args, 2)
		pg_project.diff_pg_file(address.Address(pgconn), file, args.diff_raw, not args.no_clean, args.no_owner, args.no_acl,
			pre_load=args.pre_load, post_load=args.post_load, pre_remoted_load=args.pre_remoted_load, post_remoted_load=args.post_remoted_load,
			swap=not args.swap, pg_extractor=pg_extractor, cache=args.cache)

	elif args.cmd == "role-list" and len(args.args) in (0,):
		pg_project.role_list()

	elif args.cmd == "role-add" and len(args.args) in (1, 2, 3,):
		(name, arg1, arg2) = args_parse(args.args, 3)
		pg_project.role_add(name, arg1, arg2)

	elif args.cmd == "role-change" and len(args.args) in (1, 2, 3,):
		(name, arg1, arg2) = args_parse(args.args, 3)
		pg_project.role_change(name, arg1, arg2)

	elif args.cmd == "role-rm" and len(args.args) in (1,):
		(name,) = args_parse(args.args, 1)
		pg_project.role_rm(name)

	elif args.cmd == "require-add" and len(args.args) in (3,):
		(project_name, git, git_tree_ish) = args_parse(args.args, 3)
		pg_project.require_add(project_name, git, git_tree_ish)

	elif args.cmd == "require-rm" and len(args.args) in (1,):
		(project_name, ) = args_parse(args.args, 1)
		pg_project.require_rm(project_name)

	elif args.cmd == "dbparam-set":
		if len(args.args) == 0:
			dbparam = None
		else:
			dbparam = " ".join(args.args)
		pg_project.dbparam_set(dbparam)

	elif args.cmd == "dbparam-get" and len(args.args) in (0,):
		pg_project.dbparam_get()

	elif args.cmd == "data-add" and len(args.args) >= 1:
		table = args.args[0]
		columns = args.args[1:]
		pg_project.tabledata_add(table, columns)

	elif args.cmd == "data-rm" and len(args.args) in (1,):
		(table, ) = args_parse(args.args, 1)
		pg_project.tabledata_rm(table)

	elif args.cmd == "data-list" and len(args.args) in (0,):
		pg_project.tabledata_list()

	# install projects
	elif args.cmd == "list" and len(args.args) in (0, 1, 2,):
		(project_name, dbname) = args_parse(args.args, 2)
		pg_project.prlist(project_name, dbname, conninfo.ConnInfo(args), args.directory, args.showall)

	elif args.cmd == "install" and len(args.args) in (2, 3,):
		(project_name, dbname, version) = args_parse(args.args, 3)
		pg_project.install(project_name, dbname, version, conninfo.ConnInfo(args), args.directory, args.create, False)

	elif args.cmd == "check-update" and len(args.args) in (0, 1, 2, 3,):
		(project_name, dbname, version) = args_parse(args.args, 3)
		pg_project.check_update(project_name, dbname, version, conninfo.ConnInfo(args), args.directory)

	elif args.cmd == "update" and len(args.args) in (0, 1, 2, 3,):
		(project_name, dbname, version) = args_parse(args.args, 3)
		pg_project.update(project_name, dbname, version, conninfo.ConnInfo(args), args.directory)

	elif args.cmd == "clean" and len(args.args) in (1, 2,):
		(project_name, dbname) = args_parse(args.args, 2)
		pg_project.clean(project_name, dbname, conninfo.ConnInfo(args))

	elif args.cmd == "set-version" and len(args.args) in (3,):
		(project_name, dbname, version) = args_parse(args.args, 3)
		pg_project.set_version(project_name, dbname, version, conninfo.ConnInfo(args))

	elif args.cmd == "pgdist-update" and len(args.args) in (0,1):
		(dbname,) = args_parse(args.args, 1)
		pg_project.pgdist_update(dbname, conninfo.ConnInfo(args))

	else:
		parser.print_help()
		sys.exit(1)

	sys.exit(0)

def close_less(pager):
	pager.stdin.close()
	pager.wait()

def args_parse(args, n):
	return args + [None] * (n - len(args))

main()
