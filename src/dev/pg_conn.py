# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import sys
import logging
import re
import io
import subprocess
import csv
import os
import json
import time

import config

class PgError(Exception):
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

class PG:
	def __init__(self, addr, dbname=None):
		self.address = addr
		if dbname:
			self.dbname = re.sub(r"\W", "", dbname)
		else:
			self.dbname = None
		self.loaded_projects_name = []

	def psql(self, cmd=None, single_transaction=True, change_db=False, file=None, cwd=None, tuples_only=False, exit_on_fail=True):
		return self.run(c='psql', cmd=cmd, single_transaction=single_transaction, change_db=change_db, file=file, cwd=cwd, tuples_only=tuples_only, exit_on_fail=exit_on_fail)

	def pg_dump(self, change_db=False, no_owner=False, no_acl=False):
		return self.run(c='pg_dump', single_transaction=False, change_db=change_db, no_owner=no_owner, no_acl=no_acl)

	def run(self, c, cmd=None, single_transaction=True, change_db=False, file=None, cwd=None, no_owner=False, no_acl=False, tuples_only=False, exit_on_fail=True):
		args = [c]
		if c == "psql":
			args.append("--no-psqlrc")
			if not tuples_only:
				args.append("--echo-queries")
			args.append("--set")
			args.append("ON_ERROR_STOP=1")
		if change_db and self.dbname:
			args.append(self.address.get_pg(self.dbname))
		else:
			args.append(self.address.get_pg())
		if not self.address.get_password():
			args.append("-w")
		if single_transaction:
			args.append("--single-transaction")
		if file:
			args.append("--file")
			args.append(file)
		if c == "pg_dump":
			args.append("--schema-only")
			args.append("--exclude-schema=pgdist")
		if no_owner:
			args.append("--no-owner")
		if no_acl:
			args.append("--no-acl")
		if tuples_only:
			args.append("--tuples-only")
			args.append("--no-align")

		if self.address.ssh:
			ssh_args = []
			for arg in args:
				ssh_args.append("'%s'" % (arg.replace("\\", "\\\\").replace("'", "\\'"),))
			args = ["ssh"]
			if self.address.ssh_port:
				args += ["-p", self.address.ssh_port]
			args.append(self.address.ssh)
			args.append(" ".join(ssh_args))
		logging.verbose("run: %s" % (" ".join(args),))
		process = subprocess.Popen(args, bufsize=8192, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=cwd or ".")
		if cmd:
			cmd = cmd.encode(encoding="UTF8")
		output, unused_err = process.communicate(cmd)
		retcode = process.poll()
		if exit_on_fail and retcode != 0:
			output = "\n".join(output.split("\n")[-40:])
			raise PgError(retcode, cmd, output=output)
		return (retcode, output)

	def init(self):
		self.clean()
		try:
			logging.debug("Init test database.")
			self.psql("CREATE DATABASE %s;" % (self.dbname,), single_transaction=False)
		except PgError as e:
			logging.error("Create database fail:\n%s" % (e.output))
			sys.exit(1)


	def clean(self):
		if "_test_" in self.dbname:
			logging.debug("Clean test database.")
			try:
				self.psql("DROP DATABASE IF EXISTS %s;" % (self.dbname,), single_transaction=False)
			except PgError as e:
				logging.error("Clean database fail:\n%s" % (e.output))
				sys.exit(1)
		else:
			logging.error("Error: clean only test database")
			sys.exit(1)

	def create_roles(self, project=None, roles=None):
		if project:
			roles = map(lambda x: x.name, project.roles)
		if roles:
			creates = []
			for role in roles:
				creates.append("""
					IF NOT EXISTS (SELECT * FROM pg_catalog.pg_roles WHERE rolname = '%s') THEN
						CREATE ROLE %s NOLOGIN;
					END IF;""" % (role, role))

			cmd = """DO $do$ BEGIN %s END $do$;""" % ("\n".join(creates),)
			self.psql(cmd=cmd)

	def get_roles(self, cache):
		if cache and self.test_cache_file("roles"):
			logging.verbose("load roles from cache file")
			return json.load(open(self.address.cache_file("roles")))
		cmd = """SELECT string_agg(rolname, ',') FROM pg_roles;"""
		(retcode, output) = self.psql(cmd=cmd, tuples_only=True)
		r = output.strip().split(",")
		if cache:
			json.dump(r, open(self.address.cache_file("roles"), "w"))
		return r

	def load_project(self, project):
		self.create_roles(project)
		if project.git:
			r = self.load_project_git(project)
		else:
			r = self.load_project_fs(project)
		self.loaded_projects_name.append(project.name)
		return r

	def load_project_git(self, project):
		for part in project.parts:
			cmd = io.StringIO()
			for file in part.files:
				for l in project.get_file(file):
					cmd.write(unicode(l, "UTF8"))
				cmd.write(";\n")
			self.psql(cmd=cmd.getvalue(), single_transaction=part.single_transaction, change_db=True)
			cmd.close()

	def load_project_fs(self, project):
		for part in project.parts:
			cmd = ""
			for file in part.files:
				cmd += "\\ir sql/%s\n" % (file,)
			self.psql(cmd=cmd, single_transaction=part.single_transaction, change_db=True, cwd=project.directory)

	def load_update(self, update):
		for part in update.parts:
			logging.verbose("load update %s" % (part.fname,))
			self.psql(single_transaction=part.single_transaction, file=part.fname, change_db=True)

	def load_dump(self, dump):
		self.psql(cmd=dump, single_transaction=False, change_db=True)

	def dump(self, no_owner=False, no_acl=False, cache=False):
		if cache and self.test_cache_file("struct"):
			logging.verbose("load struct from cache file")
			return open(self.address.cache_file("struct")).read()
		(retcode, output) = self.pg_dump(change_db=True, no_owner=no_owner, no_acl=no_acl)
		r = unicode(output, "UTF8")
		if cache:
			open(self.address.cache_file("struct"), "w").write(r)
		return r


	def load_file(self, filename):
		if filename:
			logging.verbose("load file: %s" % (filename,))
			self.psql(single_transaction=True, file=filename, change_db=True)

	def load_data(self, project, table_data):
		for table in project.table_data:
			csv_data = io.BytesIO()
			writer = csv.writer(csv_data, delimiter=";".encode("utf8"))
			for row in table_data[table.table_name][1:]:
				r = []
				for v in row:
					if v is None:
						r.append("NULL@15#7&679")
					else:
						r.append(v)
				writer.writerow(r)
			self.psql(cmd="COPY %s (%s) FROM STDIN WITH(FORMAT CSV, DELIMITER E';', NULL 'NULL@15#7&679');\n%s" % (table.table_name, ", ".join(table_data[table.table_name][0]), csv_data.getvalue()), change_db=True)

	def dump_data(self, project, cache=False):
		if cache and self.test_cache_file("data"):
			logging.verbose("load data from cache file")
			return json.load(open(self.address.cache_file("data")))
		r = {}
		c = []
		for tb in project.table_data:
			c.append("COPY %s TO STDOUT WITH(FORMAT CSV, HEADER, FORCE_QUOTE *, NULL 'NULL@15#7&679');" % (tb,))
		(retcode, output) = self.psql(cmd="\n".join(c), change_db=True, exit_on_fail=False)
		data = io.StringIO(unicode(output, "utf8"))

		line = data.readline()
		while True:
			if not line:
				break
			x = re.match(r"COPY (?P<table>\S*) .*TO STDOUT.*NULL@15#7&679", line)
			if x:
				data_table = []
				table_name = x.group("table")
				line = data.readline()
				if line.startswith("ERROR: "):
					logging.warning(line)
					continue
				if line != "\n":
					data_table.append(line)
				while True:
					line = data.readline()
					if not line:
						break
					if re.match(r"COPY (?P<table>\S*) .*TO STDOUT.*NULL@15#7&679", line):
						break
					data_table.append(line)
				dt = list(csv.reader(data_table))
				for row in dt:
					for i in xrange(len(row)):
						if row[i] == "NULL@15#7&679":
							row[i] = None
				r[table_name] = dt
			else:
				line = data.readline()
		if cache:
			json.dump(r, open(self.address.cache_file("data"), "w"))
		return r

	def pg_extractor(self, pg_extractor, no_owner=False, no_acl=False):
		args = ["pg_extractor", "--getall", "--gettriggers", "--basedir", pg_extractor.get_dumpdir()]
		env = None
		if self.address.get_user(self.dbname):
			args.append("--username")
			args.append(self.address.get_user(self.dbname))
		if self.address.get_password(self.dbname):
			env = os.environ.copy()
			env["PGPASSWORD"] = self.address.get_password(self.dbname)
		if self.address.get_host(self.dbname):
			args.append("--host")
			args.append(self.address.get_host(self.dbname))
		if self.address.get_port(self.dbname):
			args.append("--port")
			args.append(self.address.get_port(self.dbname))
		if self.address.get_dbname(self.dbname):
			args.append("--dbname")
			args.append(self.address.get_dbname(self.dbname))
		if no_owner:
			args.append("--no_owner")
		if no_acl:
			args.append("--no_acl")
		logging.verbose("run pg_extractor: %s" % (" ".join(args),))
		process = subprocess.Popen(args, bufsize=8192, cwd=pg_extractor.get_dumpdir(), env=env)
		retcode = process.wait()
		pg_extractor.add_db(self.address.get_dbname(self.dbname))

	def test_cache_file(self, cache_type):
		fname = self.address.cache_file(cache_type)
		if os.path.isfile(fname):
			return time.time() - os.path.getmtime(fname) < 4 * 60 * 60
		return False
