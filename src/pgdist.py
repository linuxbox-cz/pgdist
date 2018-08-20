#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import argparse
import logging
import logging.handlers

description = """
PGdist - distribute PotgreSQL functions, tables, etc...

    init project [directory] - initialize pgdist project
    create-schema schema - create new schema directory tree
    status - show new files and removed files compared to pg_project.sql
    add file1 [file2 ...] - add files to pg_project.sql
    rm file1 [file2 ...] - removed files from pg_project.sql

    test-load - load project to testing postgres
    create-version version [git_tag] - create version files
    create-update git_tag new-version - create version files with differencies
                                          - old-version - git tag
                                          - new-version - version created by create-version
    test-update git_tag new-version - load old and new version and compare it
                                          - old-version - git tag
                                          - new-version - version created by create-version
 
    diff-db pgconn [git_tag] - diff project and database

    role-list - print roles in project
    role-add name [nologin|login] [password] - add role to project
    role-change name [nologin|login] [password] - change param on role
    role-rm name - remove role from project, not remove from databases

    require-add project git git_tree_ish - add require to another project
    require-rm project - remove require to another project

PGdist Server - manage projects in PostgreSQL database

    list [project [dbname]] - show list of installed projects in database
    install project dbname [version] - install project to database
    update [project [dbname [version]]] - update project
    clean project [dbname] - remove all info about project
    set-version project version dbname - force change version without run scripts
    pgdist-update [dbname] - update pgdist version in database

pgconn - ssh connection + connection URI, see:
    https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING
    without string 'postgresql://'
    examples:
        localhost/mydb - connect to mydb
        root@server//user@/mydb - connect to server via ssh and next connect to postgres as user into mydb

Configuration:
    connection to testing database in file "~/.pgdist" (or ".pgdist" in project path) with content:
        [pgdist]
        test_db: user@host/dbname

        test_db - URI to testing postgres, user has to create databases and users
"""

def main():
	logging.basicConfig(format="%(message)s")
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=description, add_help=False)

	# common argument
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("-?", "--help", dest="help", action="store_true", help="show this help message and exit")
	parser.add_argument("cmd", nargs="?")
	parser.add_argument("args", nargs="*")

	# develop projects
	parser.add_argument("--all", help="use all files", action="store_true")
	parser.add_argument("-f", "--force", help="overwriting and removing files", action="store_true")
	parser.add_argument("-c", "--config", help="configuration file")
	parser.add_argument("--color", help="never, always or auto colorred output", default="auto", choices=["auto", "never", "always"])
	parser.add_argument("--gitversion", help="use as version for git tag")
	parser.add_argument("--no-owner", dest="no_owner", help="do not dump and compare ownership of objects", action="store_true")
	parser.add_argument("--no-acl", dest="no_acl", help="do not dump and compare access privileges (grant/revoke commands)", action="store_true")
	parser.add_argument("--diff-raw", dest="diff_raw", help="compare raw SQL dumps", action="store_true")
	parser.add_argument("--no-clean", dest="no_clean", help="no clean test database after load/update test", action="store_true", default=False)

	# install projects
	parser.add_argument("--showall", help="show all versions", action="store_true")
	parser.add_argument("-d", "--dbname", dest="dbname", help="Specifies the name of the database to connect to.")
	parser.add_argument("-h", "--host", dest="host", help="Specifies the host name of the machine on which the server is running.")
	parser.add_argument("-p", "--port", dest="port", help="Specifies the TCP port or the local Unix-domain socket file.")
	parser.add_argument("-U", "--username", dest="user", help="Connect to the database as the user username.")
	parser.add_argument("--directory", help="directory contains script install and update", default="/usr/share/pgdist/install")
	parser.add_argument("--syslog-facility", dest="syslog_facility", help="syslog facility")
	parser.add_argument("--syslog-ident", dest="syslog_ident", help="syslog ident")

	args = parser.parse_args()

	if args.help:
		parser.print_help()
		sys.exit(1)

	if args.verbose:
		logging.basicConfig(format="%(asctime)-15s %(filename)s:%(lineno)d %(message)s")
		logging.getLogger().setLevel(logging.DEBUG)
		logging.debug("verbosity turned on")

	if args.syslog_facility or args.syslog_ident:
		handler = logging.handlers.SysLogHandler(facility=args.syslog_facility, address='/dev/log')
		if args.syslog_ident:
			handler.setFormatter(logging.Formatter(args.syslog_ident+": %(message)s"))
		logging.getLogger().addHandler(handler)

	if args.cmd in ("init", "create-schema", "status", "test-load", "create-version", "add", "rm",
		"create-update", "test-update", "diff-db", "role-list", "role-add", "role-change", "role-rm",
		"require-add", "require-rm"):

		sys.path.insert(1, os.path.join(sys.path[0], "dev"))
		import color
		import address
		import config
		import pg_parser
		import project

		config.load(args.config)
		color.set(args.color)

	if args.cmd in ("list", "install", "update", "clean", "set-version", "pgdist-update"):
		sys.path.insert(1, os.path.join(sys.path[0], "mng"))
		import conninfo
		import project


	# develop projects
	if args.cmd == "init" and len(args.args) in (1, 2,):
		(project_name, directory) = args_parse(args.args, 2)
		if not directory:
			directory = os.getcwd()
		project.project_init(project_name, directory)

	elif args.cmd == "create-schema" and len(args.args) in (1,):
		(schema_name,) = args_parse(args.args, 1)
		project.create_schema(schema_name)

	elif args.cmd == "status" and len(args.args) in (0,):
		project.status()

	elif args.cmd == "add":
		project.add(args.args, args.all)

	elif args.cmd ==  "rm":
		project.rm(args.args, args.all)

	elif args.cmd == "test-load" and len(args.args) in (0,):
		project.test_load(not args.no_clean)

	elif args.cmd == "create-version" and len(args.args) in (1, 2,):
		(version, git_tag) = args_parse(args.args, 2)
		project.create_version(version, git_tag, args.force)

	elif args.cmd == "create-update" and len(args.args) in (2,):
		(git_tag, new_version) = args_parse(args.args, 2)
		project.create_update(git_tag, new_version, args.force, args.gitversion)

	elif args.cmd == "test-update" and len(args.args) in (2,):
		(git_tag, new_version) = args_parse(args.args, 1)
		project.test_update(git_tag, new_version, args.gitversion, not args.no_clean)

	elif args.cmd == "diff-db" and len(args.args) in (1,):
		(pgconn,) = args_parse(args.args, 1)
		project.diff_pg(address.Address(pgconn), args.diff_raw, args.no_owner, args.no_acl)

	elif args.cmd == "role-list" and len(args.args) in (0,):
		project.role_list()

	elif args.cmd == "role-add" and len(args.args) in (1, 2, 3,):
		(name, arg1, arg2) = args_parse(args.args, 3)
		project.role_add(name, arg1, arg2)

	elif args.cmd == "role-change" and len(args.args) in (1, 2, 3,):
		(name, arg1, arg2) = args_parse(args.args, 3)
		project.role_change(name, arg1, arg2)

	elif args.cmd == "role-rm" and len(args.args) in (1,):
		(name,) = args_parse(args.args, 1)
		project.role_rm(name)

	elif args.cmd == "require-add" and len(args.args) in (3,):
		(project_name, git, git_tree_ish) = args_parse(args.args, 3)
		project.require_add(project_name, git, git_tree_ish)

	elif args.cmd == "require-rm" and len(args.args) in (1,):
		(project_name, ) = args_parse(args.args, 1)
		project.require_rm(project_name)

	# install projects
	elif args.cmd == "list" and len(args.args) in (0, 1, 2,):
		(project_name, dbname) = args_parse(args.args, 2)
		project.prlist(project_name, dbname, conninfo.ConnInfo(args), args.directory, args.showall)

	elif args.cmd == "install" and len(args.args) in (2, 3,):
		(project_name, dbname, version) = args_parse(args.args, 3)
		project.install(project_name, dbname, version, conninfo.ConnInfo(args), args.directory, args.verbose)

	elif args.cmd == "update" and len(args.args) in (0, 1, 2, 3,):
		(project_name, dbname, version) = args_parse(args.args, 3)
		project.update(project_name, dbname, version, conninfo.ConnInfo(args), args.directory, args.verbose)

	elif args.cmd == "clean" and len(args.args) in (1, 2,):
		(project_name, dbname) = args_parse(args.args, 2)
		project.clean(project_name, dbname, conninfo.ConnInfo(args))

	elif args.cmd == "set-version" and len(args.args) in (3,):
		(project_name, version, dbname) = args_parse(args.args, 3)
		project.set_version(project_name, dbname, version, conninfo.ConnInfo(args))

	elif args.cmd == "pgdist-update" and len(args.args) in (1,):
		(dbname,) = args_parse(args.args, 1)
		project.pgdist_update(dbname, conninfo.ConnInfo(args))

	else:
		parser.print_help()
		sys.exit(1)
	sys.exit(0)


def args_parse(args, n):
	return args + [None] * (n - len(args))

main()
