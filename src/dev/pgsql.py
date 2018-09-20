# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import logging
import re
import io
import subprocess

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

	def psql(self, cmd=None, single_transaction=True, change_db=False, file=None, cwd=None, tuples_only=False):
		return self.run(c='psql', cmd=cmd, single_transaction=single_transaction, change_db=change_db, file=file, cwd=cwd, tuples_only=tuples_only)

	def pg_dump(self, change_db=False, no_owner=False, no_acl=False):
		return self.run(c='pg_dump', single_transaction=False, change_db=change_db, no_owner=no_owner, no_acl=no_acl)

	def run(self, c, cmd=None, single_transaction=True, change_db=False, file=None, cwd=None, no_owner=False, no_acl=False, tuples_only=False):
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
		if single_transaction:
			args.append("--single-transaction")
		if file:
			args.append("--file")
			args.append(file)
		if c == "pg_dump":
			args.append("--schema-only")
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
			args.append(self.address.ssh)
			args.append(" ".join(ssh_args))
		logging.debug(args)
		process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=cwd or ".")
		if cmd:
			cmd = cmd.encode(encoding="UTF8")
		output, unused_err = process.communicate(cmd)
		retcode = process.poll()
		if retcode != 0:
			output = "\n".join(output.split("\n")[-40:])
			raise PgError(retcode, cmd, output=output)
		return (retcode, output)

	def init(self):
		self.clean()
		try:
			logging.debug("Init test database.")
			self.psql("CREATE DATABASE %s;" % (self.dbname,), single_transaction=False)
		except PgError as e:
			logging.error("Create database fail:")
			print(e.output)
			sys.exit(1)


	def clean(self):
		if "_test_" in self.dbname:
			logging.debug("Clean test database.")
			try:
				self.psql("DROP DATABASE IF EXISTS %s;" % (self.dbname,), single_transaction=False)
			except PgError as e:
				logging.error("Clean database fail:")
				print(e.output)
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
					IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '%s') THEN
						CREATE ROLE %s NOLOGIN;
					END IF;""" % (role, role))

			cmd = """DO $do$ BEGIN %s END $do$;""" % ("\n".join(creates),)
			self.psql(cmd=cmd)

	def get_roles(self):
		cmd = """SELECT string_agg(rolname, ',') FROM pg_roles;"""
		(retcode, output) = self.psql(cmd=cmd, tuples_only=True)
		return output.strip().split(",")

	def load_project(self, project):
		self.create_roles(project)
		if project.git:
			return self.load_project_git(project)
		else:
			return self.load_project_fs(project)
		self.loaded_projects_name.append(project.name)

	def load_project_git(self, project):
		for part in project.parts:
			cmd = io.StringIO()
			for file in part.files:
				for l in project.get_file(file):
					cmd.write(unicode(l, "UTF8"))
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
			self.psql(single_transaction=part.single_transaction, file=part.fname, change_db=True)

	def load_dump(self, dump):
		self.psql(cmd=dump, single_transaction=False, change_db=True)

	def dump(self, no_owner=False, no_acl=False):
		(retcode, output) = self.pg_dump(change_db=True, no_owner=no_owner, no_acl=no_acl)
		return unicode(output, "UTF8")

	def load_file(self, filename):
		if filename:
			self.psql(single_transaction=True, file=filename, change_db=True)
