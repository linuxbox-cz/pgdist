# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import os
import re
import sys
import logging
import subprocess
from distutils.version import LooseVersion

try:
	import configparser
except ImportError:
	import ConfigParser as configparser

import address

test_db = None
config = None
git_diff = False

def load(fname):
	global config
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

		if not config:
			logging.error("Load config: .pgdist failed")
			sys.exit(1)

def load_file(fname):
	logging.verbose("Load config: %s" % (fname,))
	global test_db
	global config
	try:
		config = configparser.ConfigParser()
		config.read(fname)
		if config.get('pgdist', 'test_db'):
			test_db = address.Address(config.get('pgdist', 'test_db'))
		else:
			logging.error("Load config: %s failed" % (fname))
			sys.exit(1)
	except Exception as e:
		logging.error("Load config: %s fail: %s" % (fname, str(e)))
		sys.exit(1)

def check_set_test_db():
	global test_db
	if not test_db:
		logging.error("Error not set test_db connection")
		sys.exit(1)
