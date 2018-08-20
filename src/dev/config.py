# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import logging

try:
	import configparser
except ImportError:
	import ConfigParser as configparser

import address

test_db = None

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
	logging.debug("Load config: %s" % (fname,))
	global test_db
	try:
		config = configparser.ConfigParser()
		config.read(fname)
		if config.get('pgdist', 'test_db'):
			test_db = address.Address(config.get('pgdist', 'test_db'))
		#if "test_db" in config["pgdist"]:
		#	test_db = address.Address(config["pgdist"].get("test_db"))
	except Exception as e:
		logging.error("Load config: %s fail: %s" % (fname, str(e)))
		sys.exit(1)

def check_set_test_db():
	global test_db
	if not test_db:
		logging.error("Error not set test_db connection")
		sys.exit(1)
