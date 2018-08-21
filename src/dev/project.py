# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import os
import sys
import glob
import difflib
import tarfile
import logging
import io
import cStringIO
import subprocess

import color
import pgsql
import config
import pg_parser

class Part:
	def __init__(self):
		self.files = []
		self.single_transaction = True

class Role:
	def __init__(self, name, param):
		self.name = name
		self.password = "password" in param
		self.nologin = "nologin" in param
		self.login = "login" in param

	def __str__(self):
		p = [self.name]
		if self.password:
			p.append("password")
		if self.nologin:
			p.append("nologin")
		if self.login:
			p.append("login")
		return " ".join(p)

class Require:
	def __init__(self, project_name, git, tree_ish):
		self.project_name = project_name
		self.git = git
		self.tree_ish = tree_ish

class ProjectBase:
	def load_conf(self, file):
		for line in file:
			# project name
			x = re.match(r"-- name:\s*(?P<name>.*\S)", line)
			if x:
				self.name = x.group("name")
			# part of project
			x = re.match(r"-- part", line)
			if x:
				part = Part()
				self.parts.append(part)
			# single_transaction
			x = re.match(r"--\s*single_transaction", line)
			if x:
				part.single_transaction = True
			# not single_transaction
			x = re.match(r"--\s*not\s*single_transaction", line)
			if x:
				part.single_transaction = False
			# import file
			x = re.match(r"\\ir\s+(?P<file>.*\S)", line)
			if x:
				part.files.append(x.group("file"))
			# role
			x = re.match(r"--\s*role:\s+(?P<role>\S+)(\s+(?P<param>.*))?", line)
			if x:
				self.roles.append(Role(x.group("role"), x.group("param").split("--")[0].split(" ")))
			# requires
			x = re.match(r"--\s*require:\s+(?P<project_name>\S+)\s+(?P<git>\S+)\s+(?P<git_tree_ish>\S+)", line)
			if x:
				self.requires.append(Require(x.group("project_name"), x.group("git"), x.group("git_tree_ish")))
		file.close()

	def is_file(self, file):
		for part in self.parts:
			if file in part.files:
				return True
		return False

	def is_not_file(self, file):
		return not self.is_file(file)

	def get_files(self):
		files = []
		for part in self.parts:
			files += part.files
		return files

	def get_role(self, name):
		for role in self.roles:
			if role.name == name:
				return role
		return None

class ProjectFs(ProjectBase):
	def __init__(self, directory=None):
		if directory:
			self.directory = directory
		else:
			self.directory = find_directory()
		self.name = None
		self.parts = []
		self.roles = []
		self.requires = []
		self.git = False
		self.load_conf(open(os.path.join(self.directory, "sql", "pg_project.sql")))

	def get_file(self, fname):
		return open(os.path.join(self.directory, "sql", fname))

class ProjectGit(ProjectBase):
	def __init__(self, git_tag=None, git_remote=None, git_tree_ish=None, directory=None):
		if directory:
			self.directory = directory
		else:
			self.directory = find_directory()
		self.name = None
		self.parts = []
		self.roles = []
		self.requires = []
		self.git = True
		# TODO, archive only sql directory
		if git_tag:
			args = ["/usr/bin/git", "archive", "--format=tar", git_tag]
		elif git_remote:
			args = ["/usr/bin/git", "archive", "--format=tar", "--remote", git_remote, git_tree_ish]
		else:
			# TODO err msg
			sys.exit(1)
		process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, cwd=self.directory)
		output, err = process.communicate()
		retcode = process.poll()
		if retcode != 0:
			logging.error("Fail get git version: %s" % (err))
			sys.exit(1)
		self.tar = tarfile.open(fileobj=cStringIO.StringIO(output), bufsize=10240)
		self.load_conf(self.tar.extractfile("sql/pg_project.sql"))

	def get_file(self, fname):
		return self.tar.extractfile("sql/"+fname)

class UpdatePart:
	def __init__(self, fname):
		self.fname = fname
		self.single_transaction = True
		with(open(fname)) as f:
			for line in f:
				# single_transaction
				x = re.match(r"--\s*single_transaction", line)
				if x:
					self.single_transaction = True
				# not single_transaction
				x = re.match(r"--\s*not\s*single_transaction", line)
				if x:
					self.single_transaction = False
				# end header
				x = re.match(r"--\s*end\s+header", line)
				if x:
					break

class Update:
	def __init__(self, project_name, old_version, new_version, directory=None):
		if directory:
			self.directory = directory
		else:
			self.directory = find_directory()
		self.parts = []
		pattern = "%s--%s--%s.sql" % (to_fname(project_name), to_fname(old_version), to_fname(new_version))
		fname = os.path.join(self.directory, "sql_dist", pattern)
		if os.path.isfile(fname):
			logging.debug("Update find part: %s" % (fname,))
			self.parts.insert(1, UpdatePart(fname))
		pattern = "%s--%s--%s--p*.sql" % (to_fname(project_name), to_fname(old_version), to_fname(new_version))
		for fname in glob.glob(os.path.join(self.directory, "sql_dist", pattern)):
			x = re.match(r".*--p(?P<part>\d+)\.sql", fname)
			if x:
				logging.debug("Update find part: %s" % (fname,))
				part = int(x.group("part"))
				self.parts.insert(part, UpdatePart(fname))

class Version:
	def __init__(self, directory=None):
		pass

def to_fname(fname):
	return re.sub(r"[^a-zA-Z0-9.]", "_", fname)

def find_directory():
	d = os.getcwd()
	while d:
		logging.debug("Search base directory in: %s" % (d, ))
		if os.path.isdir(os.path.join(d, "sql")) and os.path.isfile(os.path.join(d, "sql", "pg_project.sql")):
			return d
		d1, x = os.path.split(d)
		if d1 == d:
			break
		d = d1
	logging.error("Base directory not found.")
	sys.exit(1)

def load_files(directory):
	files = []
	for schema_dir in os.listdir(os.path.join(directory, "sql")):
		if os.path.isdir(os.path.join(directory, "sql", schema_dir)):
			logging.debug("schema_dir: %s" % (schema_dir,))
			for type_dir in os.listdir(os.path.join(directory, "sql", schema_dir)):
				if os.path.isdir(os.path.join(directory, "sql", schema_dir, type_dir)):
					logging.debug("type_dir: %s" % (type_dir,))
					for file in os.listdir(os.path.join(directory, "sql", schema_dir, type_dir)):
						files.append(os.path.join(schema_dir, type_dir, file))
	files.sort()
	return files

def get_normal_fname(file):
	f = os.path.abspath(file)
	(t, fname) = os.path.split(f)
	(t, tname) = os.path.split(t)
	(t, sname) = os.path.split(t)
	return os.path.join(sname, tname, fname)

def project_init(name, directory):
	logging.debug("Init project: %s in %s" % (name, directory))
	if not os.path.isdir(os.path.join(directory, "sql")):
		os.makedirs(os.path.join(directory, "sql"))
	if not os.path.isdir(os.path.join(directory, "sql_dist")):
		os.makedirs(os.path.join(directory, "sql_dist"))
	with open(os.path.join(directory, "sql", "pg_project.sql"),"a+") as f:
		f.write("-- pgdist project\n")
		f.write("-- name: %s\n" % (name, ))
		f.write("-- end header\n")
		f.write("\n")
		f.write("-- part\n")
		f.write("-- single_transaction\n")
		f.write("\n")
	print("PGdist project inited in %s" % (directory,))

def create_schema(schema_name):
	directory = find_directory()
	for d in ("extensions", "functions", "schema", "tables", "triggers", "types", "views", "grants"):
		logging.debug("mkdir %s" % (d, ))
		os.makedirs(os.path.join(directory, "sql", schema_name, d))
	print("Schema %s created." % (schema_name,))

def status():
	directory = find_directory()
	project = ProjectFs(directory)
	files = load_files(directory)
	logging.debug("Files in project: %s" % (files, ))
	print("PROJECT: %s" % (project.name))
	change = False
	for file in files:
		if not project.is_file(file):
			change = True
			print("NEW FILE: %s" % (file))
	for part in project.parts:
		for file in part.files:
			if not file in files:
				change = True
				print("REMOVED FILE: %s" % (file))
	if not change:
		print("Not found new or removed files")

def add(files, all):
	directory = find_directory()
	project = ProjectFs(directory)
	loaded_files = load_files(directory)
	if all:
		files = list(filter(project.is_not_file, loaded_files))
	else:
		files_ok = []
		for file in files:
			if project.is_file(file):
				logging.error("File yet in project: %s" % (file,))
				continue
			if file in loaded_files:
				logging.debug("File %s is ok" % (file,))
				files_ok.append(file)
				continue
			if os.path.isfile(file):
				nname = get_normal_fname(file)
				if project.is_file(nname):
					logging.error("File yet in project: %s as %s" % (file, nname))
					continue
				logging.debug("File %s prepare to add as %s" % (file, nname))
				files_ok.append(get_normal_fname(file))
				continue
			logging.error("File %s not found." % (file,))
			sys.exit(1)
		files = files_ok
	with open(os.path.join(directory, "sql", "pg_project.sql"),"a+") as f:
		for file in files:
			print("adding to project: %s" % (file,))
			f.write("\\ir %s\n" % (file,))

def rm(files, all):
	directory = find_directory()
	project = ProjectFs(directory)
	new_conf = io.StringIO()
	if all:
		loaded_files = load_files(directory)
		files = [f for f in project.get_files() if f not in loaded_files]
	else:
		files_ok = []
		for file in files:
			if os.path.isfile(file):
				file = get_normal_fname(file)
			if not project.is_file(file):
				logging.error("File not in project: %s" % (file,))
				continue
			files_ok.append(file)
		files = files_ok
	with open(os.path.join(directory, "sql", "pg_project.sql")) as f:
		for line in f:
			line = unicode(line, "UTF8")
			x = re.match(r"\\ir\s+(?P<file>.*\S)", line)
			if x and x.group("file") in files:
				file = x.group("file")
				print("removing from project: %s" % (file,))
			else:
				new_conf.write(line)
	new_conf.seek(0)
	with open(os.path.join(directory, "sql", "pg_project.sql"), "w") as f:
		for l in new_conf:
			f.write(l)
	new_conf.close()


def create_version(version, git_tag, force):
	if git_tag:
		project = ProjectGit(git_tag)
	else:
		project = ProjectFs()
	if not os.path.isdir(os.path.join(project.directory, "sql_dist")):
		os.mkdir(os.path.join(project.directory, "sql_dist"))
	for i, part in enumerate(project.parts):
		if len(project.parts) == 1:
			fname = "%s--%s.sql" % (to_fname(project.name), to_fname(version))
		else:
			fname = "%s--%s--p%02d.sql" % (to_fname(project.name), to_fname(version), i+1)
		build_fname = os.path.join(project.directory, "sql_dist", fname)
		if os.path.isfile(build_fname) and not force:
			logging.error("Error file exists: %s" % (build_fname,))
			sys.exit(1)
		logging.debug("Create file: %s" % (build_fname,))
		with open(build_fname, "w") as build_file:
			build_file.write("--\n")
			build_file.write("-- pgdist project\n")
			build_file.write("-- name: %s\n" % (project.name,))
			build_file.write("-- version: %s\n" % (version))
			if i == 0 and project.roles:
				build_file.write("--\n")
				for user in project.roles:
					build_file.write("-- role: %s\n" % (user,))
			build_file.write("--\n")
			build_file.write("-- part: %s\n" % (i+1))
			if part.single_transaction:
				build_file.write("-- single_transaction\n")
			else:
				build_file.write("-- not single_transaction\n")
			build_file.write("-- end header\n")
			build_file.write("--\n")
			build_file.write("\n")
			for pfname in part.files:
				logging.debug("add file: %s" % (pfname))
				build_file.write("\n")
				build_file.write("--\n")
				build_file.write("-- sqldist file: %s\n" % (pfname))
				build_file.write("--\n")
				build_file.write("\n")
				src_file = project.get_file(pfname)
				for line in src_file:
					build_file.write(line)
				src_file.close()
			build_file.write("\n")
			build_file.write("\n")
			build_file.write("--\n")
			build_file.write("-- end sqldist project\n")
			build_file.write("--\n")
			build_file.write("\n")
		print("Created file: %s" % (fname))

def load_requires(project, pg, loop_detect=[]):
	loop2 = loop_detect + [project.name]
	for require in project.requires:
		if require.project_name in loop2:
			logging.error("Error: requires loop: %s" % (" > ".join(loop2)))
		if require.project_name not in pg.loaded_projects_name:
			p = ProjectGit(git_remote=require.git, git_tree_ish=require.tree_ish)
			load_requires(p, pg, loop_detect)
			pg.load_project(p)

def load_and_dump(project, clean=True, no_owner=False, no_acl=False, pre_load=None, post_load=None, updates=None):
	test_db = "pgdist_test_%s" % (project.name,)
	try:
		pg = pgsql.PG(config.test_db, dbname=test_db)
		pg.init()
		pg.load_file(pre_load)
		load_requires(project, pg)
		pg.load_project(project)
		if updates:
			for update in updates:
				pg_test.load_update(update)
		pg.load_file(post_load)
		dump = pg.dump(no_owner, no_acl)
	except pgsql.PgError as e:
		logging.error("Load project fail:")
		print(e.output)
		if clean:
			pg.clean()
		else:
			print("Check database: %s" % pg.dbname)
		sys.exit(1)
	if clean:
		pg.clean()
	else:
		print("Check database: %s" % pg.dbname)
	return dump

def load_dump_and_dump(dump_remote, project_name="undef", no_owner=False, no_acl=False, pre_load=None, post_load=None):
	test_db = "pgdist_test_%s" % (project_name,)
	try:
		pg = pgsql.PG(config.test_db, dbname=test_db)
		pg.init()
		pg.load_file(pre_load)
		pg.load_dump(dump_remote)
		pg.load_file(post_load)
		dump = pg.dump(no_owner, no_acl)
	except pgsql.PgError as e:
		logging.error("Load dump fail:")
		print(e.output)
		pg.clean()
		sys.exit(1)
	pg.clean()
	return dump

def test_load(clean=True, pre_load=None, post_load=None):
	project = ProjectFs()
	load_and_dump(project, clean=clean, pre_load=pre_load, post_load=post_load)

def create_update(git_tag, new_version, force, gitversion=None, pre_load=None, post_load=None):
	project_old = ProjectGit(git_tag)
	project_new = ProjectFs()
	if gitversion:
		old_version = gitversion
	else:
		old_version = re.sub(r"^[^\d]*", "", git_tag)

	dump_old = load_and_dump(project_old, pre_load=pre_load, post_load=post_load)
	dump_new = load_and_dump(project_new, pre_load=pre_load, post_load=post_load)

	if not os.path.isdir(os.path.join(project.project_old, "sql_dist")):
		os.mkdir(os.path.join(project.project_old, "sql_dist"))

	# first part can be without --p%02d (--p01)
	fname = "%s--%s--%s.sql" % (to_fname(project_old.name), to_fname(old_version), to_fname(new_version))
	build_fname = os.path.join(project_old.directory, "sql_dist", fname)
	if os.path.isfile(build_fname) and not force:
		logging.error("Error file exists: %s" % (build_fname,))
		sys.exit(1)
	logging.debug("Create file: %s" % (build_fname,))
	with open(build_fname, "w") as build_file:
		build_file.write("--\n")
		build_file.write("-- pgdist %s - update file\n" % (project_old.name,))
		build_file.write("-- name: %s\n" % (project_old.name,))
		build_file.write("-- old version: %s\n" % (old_version))
		build_file.write("-- new version: %s\n" % (new_version))
		if project_new.roles:
			build_file.write("--\n")
			for user in project_new.roles:
				build_file.write("-- role: %s\n" % (user,))
		build_file.write("--\n")
		build_file.write("-- part: 1\n")
		build_file.write("-- single_transaction\n")
		build_file.write("-- end header\n")
		build_file.write("--\n")
		build_file.write("\n")
		pr_old = pg_parser.parse(io.StringIO(dump_old))
		pr_new = pg_parser.parse(io.StringIO(dump_new))
		pr_old.gen_update(build_file, pr_new)

def test_update(git_tag, new_version, updates, gitversion=None, clean=True, pre_load=None, post_load=None):
	if gitversion:
		old_version = gitversion
	else:
		old_version = re.sub(r"^[^\d]*", "", git_tag)

	project_old = ProjectGit(git_tag)
	project_new = ProjectFs()
	upds = []
	if not updates:
		upds.append(Update(project_old.name, old_version, new_version))

	dump_updated = load_and_dump(project, pre_load=pre_load, post_load=post_load, updates=upds)
	dump_cur = load_and_dump(project_new, pre_load=pre_load, post_load=post_load)

	pr_cur = pg_parser.parse(io.StringIO(dump_cur))
	pr_updated = pg_parser.parse(io.StringIO(dump_updated))
	pr_updated.diff(pr_cur)

def diff_pg(addr, diff_raw, no_owner, no_acl, pre_load=None, post_load=None, pre_remoted_load=None, post_remoted_load=None):
	config.check_set_test_db()
	project = ProjectFs()

	dump_cur = load_and_dump(project, no_owner, no_acl, pre_load=pre_load, post_load=post_load)

	try:
		pg_remote = pgsql.PG(addr)
		dump_remote = pg_remote.dump(no_owner, no_acl)
	except pgsql.PgError as e:
		logging.error("Dump fail:")
		print(e.output)
		sys.exit(1)

	dump_remote = load_dump_and_dump(dump_remote, project.name, no_owner, no_acl, pre_load=pre_remoted_load, post_load=post_remoted_load)

	if diff_raw:
		diff_c = difflib.unified_diff(dump_remote.splitlines(1), dump_cur.splitlines(1), fromfile=addr.addr, tofile="project")
		for d in diff_c:
			if d.startswith("-"):
				sys.stdout.write(color.red(d))
			elif d.startswith("+"):
				sys.stdout.write(color.green(d))
			else:
				sys.stdout.write(d)
	else:
		pr_cur = pg_parser.parse(io.StringIO(dump_cur))
		pr_remote = pg_parser.parse(io.StringIO(dump_remote))
		pr_remote.diff(pr_cur, no_owner=no_owner, no_acl=no_acl)

def role_list():
	project = ProjectFs()
	for role in project.roles:
		p = [role.name]
		if role.login:
			p.append("login")
		if role.nologin:
			p.append("nologin")
		if role.password:
			p.append("password")
		print(" ".join(p))

def role_add(name, arg1, arg2):
	new_conf = io.StringIO()
	directory = find_directory()
	project = ProjectFs()
	if project.get_role(name):
		logging.error("Error: user %s exists" % (name,))
		sys.exit(1)

	with open(os.path.join(directory, "sql", "pg_project.sql")) as f:
		for line in f:
			line = unicode(line, "UTF8")
			x = re.match(r"--\s+end\s+header", line)
			if x:
				p = [name]
				if arg1 and arg1 in ("login", "nologin"):
					p.append(arg1)
				if arg2 and arg2 in ("login", "nologin"):
					p.append(arg2)
				if arg1 and arg1 in ("password"):
					p.append(arg1)
				if arg2 and arg2 in ("password"):
					p.append(arg2)
				new_conf.write("-- role: %s\n" % (u" ".join(p),))
			new_conf.write(line)
	new_conf.seek(0)
	with open(os.path.join(directory, "sql", "pg_project.sql"), "w") as f:
		for l in new_conf:
			f.write(l)
	new_conf.close()

def role_change(name, arg1, arg2):
	new_conf = io.StringIO()
	directory = find_directory()
	project = ProjectFs()
	if not project.get_role(name):
		logging.error("Error: user %s not exists" % (name,))
		sys.exit(1)

	with open(os.path.join(directory, "sql", "pg_project.sql")) as f:
		for line in f:
			line = unicode(line, "UTF8")
			x = re.match(r"--\s+role\s+%s(\s|$)" % (name,), line)
			if x:
				p = [name]
				if arg1 and arg1 in ("login", "nologin"):
					p.append(arg1)
				if arg2 and arg2 in ("login", "nologin"):
					p.append(arg2)
				if arg1 and arg1 in ("password"):
					p.append(arg1)
				if arg2 and arg2 in ("password"):
					p.append(arg2)
				new_conf.write("-- role: %s\n" % (p,))
			else:
				new_conf.write(line)
	new_conf.seek(0)
	with open(os.path.join(directory, "sql", "pg_project.sql"), "w") as f:
		for l in new_conf:
			f.write(l)
	new_conf.close()

def role_rm(name):
	new_conf = io.StringIO()
	directory = find_directory()
	project = ProjectFs()
	if project.get_role(name):
		logging.error("Error: user %s exists" % (name,))
		sys.exit(1)

	with open(os.path.join(directory, "sql", "pg_project.sql")) as f:
		for line in f:
			line = unicode(line, "UTF8")
			x = re.match(r"--\s+role\s+%s(\s|$)" % (name,), line)
			if not x:
				new_conf.write(line)
	new_conf.seek(0)
	with open(os.path.join(directory, "sql", "pg_project.sql"), "w") as f:
		for l in new_conf:
			f.write(l)
	new_conf.close()

def require_add(project_name, git, git_tree_ish):
	new_conf = io.StringIO()
	directory = find_directory()
	project = ProjectFs()

	with open(os.path.join(directory, "sql", "pg_project.sql")) as f:
		for line in f:
			line = unicode(line, "UTF8")
			x = re.match(r"--\s+end\s+header", line)
			if x:
				new_conf.write("-- require: %s %s %s\n" % (project_name, git, git_tree_ish))
			new_conf.write(line)
	new_conf.seek(0)
	with open(os.path.join(directory, "sql", "pg_project.sql"), "w") as f:
		for l in new_conf:
			f.write(l)
	new_conf.close()

def require_rm(project_name):
	new_conf = io.StringIO()
	directory = find_directory()
	project = ProjectFs()

	with open(os.path.join(directory, "sql", "pg_project.sql")) as f:
		for line in f:
			line = unicode(line, "UTF8")
			x = re.match(r"--\s+require\s*:\s*%s\s" % (project_name,), line)
			if not x:
				new_conf.write(line)
	new_conf.seek(0)
	with open(os.path.join(directory, "sql", "pg_project.sql"), "w") as f:
		for l in new_conf:
			f.write(l)
	new_conf.close()
