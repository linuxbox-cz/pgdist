# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import logging

try:
	import configparser
except ImportError:
	import ConfigParser as configparser

def load(fname):
	if fname:
		load_file(fname)
	else:
		if os.path.isfile(os.path.join(os.environ['HOME'], ".pgdist")):
			load_file(os.path.join(os.environ['HOME'], ".pgdist"))
		
		path = os.getcwd()
		paths = []
		while 1:
			paths.append(path)
			path, x = os.path.split(path)
			if x == "":
				break
		paths.reverse()
		for path in paths:
			if os.path.isfile(os.path.join(path, ".pgdist")):
				load_file(os.path.join(path, ".pgdist"))

def load_file(fname):
	logging.verbose("Load config: %s" % (fname,))
	global test_db
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

	if config.has_section("pgdist") and config.has_option("pgdist", "install_path"):
		path = config.get("pgdist", "install_path")
		if not path:
			return "/usr/share/pgdist/install"
		return path
