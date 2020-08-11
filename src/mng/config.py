# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import logging

try:
	import configparser
except ImportError:
	import ConfigParser as configparser

config = None

def load(fname):
	global config
	if fname:
		load_file(fname)
	elif os.path.isfile("/etc/pgdist.conf"):
		load_file("/etc/pgdist.conf")
	else:
		logging.error("Load config: /etc/pgdist.conf failed: file not found" % ())
		sys.exit(1)

def load_file(fname):
	logging.verbose("Load config: %s" % (fname,))
	global config
	try:
		config = configparser.ConfigParser()
		if not config.read(fname):
			logging.error("Load config: %s failed" % (fname))
			sys.exit(1)
	except Exception as e:
		logging.error("Load config: %s failed: %s" % (fname, str(e)))
		sys.exit(1)

def get_install_path():
	global config
	default_path = "/usr/share/pgdist/install"
	path = None

	if config.has_section("pgdist") and config.has_option("pgdist", "install_path"):
		path = config.get("pgdist", "install_path")
	return path or default_path

def get_password_path():
	global config
	default_path = "/etc/lbox/postgresql/roles/"
	path = None

	if config.has_section("pgdist") and config.has_option("pgdist", "password_path"):
		path = config.get("pgdist", "password_path")
	return path or default_path

def get_pguser():
	global config
	user = None

	if config.has_section("pgdist") and config.has_option("pgdist", "pguser"):
		user = config.get("pgdist", "pguser")
	return user

def get_pgdatabase():
	global config
	database = None

	if config.has_section("pgdist") and config.has_option("pgdist", "pgdatabase"):
		database = config.get("pgdist", "pgdatabase")
	return database

def get_pghost():
	global config
	host = None

	if config.has_section("pgdist") and config.has_option("pgdist", "pghost"):
		host = config.get("pgdist", "pghost")
	return host

def get_pgport():
	global config
	port = None

	if config.has_section("pgdist") and config.has_option("pgdist", "pgport"):
		port = config.get("pgdist", "pgport")
	return port

def get_databases():
	global config
	databases_string = ""
	databases = []

	if config.has_section("pgdist") and config.has_option("pgdist", "databases"):
		databases_string = config.get("pgdist", "databases")

		if databases_string:
			databases = [database.strip() for database in databases_string.strip().split(",") if database.strip()]

	return databases
