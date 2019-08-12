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
	else:
		if os.path.isfile("/etc/pgdist/pgdist.ini"):
			load_file("/etc/pgdist/pgdist.ini")

def load_file(fname):
	logging.verbose("Load config: %s" % (fname,))
	global config
	try:
		config = configparser.ConfigParser()
		if not config.read(fname):
			logging.error("Load config: %s failed" % (fname))
			sys.exit(1)
	except Exception as e:
		logging.error("Load config: %s fail: %s" % (fname, str(e)))
		sys.exit(1)

def get_install_path():
	global config
	default_path = "/usr/share/pgdist/install"

	if config.has_section("pgdist") and config.has_option("pgdist", "install_path"):
		path = config.get("pgdist", "install_path")
	return path or default_path

def get_password_path():
	global config
	default_path = "/etc/lbox/postgresql/roles/"

	if config.has_section("pgdist") and config.has_option("pgdist", "password_path"):
		path = config.get("pgdist", "password_path")
	return path or default_path

def get_db_user():
	global config

	if config.has_section("pgdist") and config.has_option("pgdist", "db_user"):
		user = config.get("pgdist", "db_user")
	return user or "postgres"