# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import re
import os
import sys
import glob
import getpass
import difflib
import tarfile
import logging
import io
import cStringIO
import subprocess

import color
import utils
import pg_conn
import config
import pg_parser

class Part:
	def __init__(self, single_transaction=True, number=1):
		self.files = []
		self.single_transaction = single_transaction
		self.data = ""
		self.number = number

	def add_data(self, data):
		self.data += data

	def add_file(self, fname):
		self.data += "\\ir %s\n" % (fname,)
		self.files.append(fname)

	def rm_file(self, fname):
		self.files.remove(fname)
		self.data = "\n".join(filter(lambda x: not re.match(r"\\ir\s+%s($|\s)" % (fname,), x), self.data.splitlines()))

class Role:
	def __init__(self, name, param=None):
		self.name = name
		self.password = param and "password" in param
		self.nologin = param and "nologin" in param
		self.login = param and "login" in param

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

	def __str__(self):
		return "%s %s %s" % (self.project_name, self.git, self.tree_ish)

class TableData:
	def __init__(self, table_name, columns=None):
		self.table_name = table_name
		if columns:
			self.columns = map(lambda x: x.strip(), columns)
		else:
			self.columns = None

	def __str__(self):
		if self.columns:
			return "%s (%s)" % (self.table_name, ", ".join(self.columns))
		else:
			return "%s" % (self.table_name)

	def __cmp__(self, other):
		return cmp(self.table_name, other.table_name)

class ProjectBase:
	def init(self, directory=None):
		if directory:
			self.directory = directory
		else:
			self.directory = find_directory()
		self.name = None
		self.parts = []
		self.roles = []
		self.requires = []
		self.table_data = []
		self.dbparam = None

	def load_conf(self, file):
		part = None
		part_num = 1
		for i, line in enumerate(file):
			# project name
			x = re.match(r"-- name:\s*(?P<name>.*\S)", line)
			if x:
				self.name = x.group("name")
				continue
			# part of project
			x = re.match(r"-- part(:\s+(?P<number>\d{1,2}))?", line)
			if x:
				part = Part(number=int(x.group("number") or part_num))
				part_num = part.number + 1
				self.parts.append(part)
				continue
			# single_transaction
			x = re.match(r"--\s*single_transaction", line)
			if x:
				part.single_transaction = True
				continue
			# not single_transaction
			x = re.match(r"--\s*not\s*single_transaction", line)
			if x:
				part.single_transaction = False
				continue
			# role
			x = re.match(r"--\s*role:\s+(?P<role>\S+)(\s+(?P<param>.*))?", line)
			if x:
				self.roles.append(Role(x.group("role"), x.group("param").split("--")[0].split(" ")))
				continue
			# requires
			x = re.match(r"--\s*require:\s+(?P<project_name>\S+)\s+(?P<git>\S+)\s+(?P<git_tree_ish>\S+)", line)
			if x:
				self.requires.append(Require(x.group("project_name"), x.group("git"), x.group("git_tree_ish")))
				continue
			# dbparam
			x = re.match(r"--\s*dbparam:\s+(?P<dbparam>.+)", line)
			if x:
				self.dbparam = x.group("dbparam")
				continue
			# table_data
			x = re.match(r"--\s*table_data:\s+(?P<table_name>\S+)(\s*\((?P<columns>.+)\))?", line)
			if x:
				if x.group("columns"):
					self.table_data.append(TableData(x.group("table_name"), x.group("columns").split(",")))
				else:
					self.table_data.append(TableData(x.group("table_name")))
				continue
			# part data
			# import file
			if part:
				x = re.match(r"\\ir\s+(?P<file>.*\S)", line)
				if x:
					part.add_data(line)
					part.files.append(x.group("file"))
		file.close()

	def save_conf(self):
		new_conf = io.StringIO()
		new_conf.write(utils.get_header(self.name, "project-config", roles=self.roles, requires=self.requires, dbparam=self.dbparam, tables_data=self.table_data))
		new_conf.write(utils.get_part_header(self.parts, "project-config"))
		new_conf.seek(0)
		with open(os.path.join(self.directory, "sql", "pg_project.sql"), "w") as file:
			for line in new_conf:
				file.write(line)
		new_conf.close()

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

	def get_require(self, project_name):
		for require in self.requires:
			if require.project_name == project_name:
				return require
		return None

	def get_tabledata(self, name):
		for td in self.table_data:
			if td.table_name == name:
				return td
		return None

	def check_n_repair_parts(self):
		for i, part in enumerate(self.parts):
			if part.number != i + 1:
				part.number = i + 1

	def add_part(self, single_transaction=True):
		self.parts.append(Part(single_transaction, len(self.parts)+1))
		self.check_n_repair_parts()

	def rm_part(self, number):
		part_index = None

		for i, part in enumerate(self.parts):
			if part.number == number:
				part_index = i
				break
		if not part_index:
			return None
		part = self.parts.pop(part_index)

		if not self.parts:
			self.add_part()
		self.check_n_repair_parts()
		return part

class ProjectNew(ProjectBase):
	def __init__(self, name, directory=None):
		self.init(directory)
		self.git = False
		self.name = name
		self.data = "\n"
		self.parts.append(Part())

class ProjectFs(ProjectBase):
	def __init__(self, directory=None):
		self.init(directory)
		self.git = False
		self.load_conf(open(os.path.join(self.directory, "sql", "pg_project.sql")))

	def get_file(self, fname):
		return open(os.path.join(self.directory, "sql", fname))

	def add_file(self, fname):
		if not self.parts:
			logging.error("Error: no part")
			sys.exit(1)
		self.parts[-1].add_file(fname)

	def rm_file(self, fname):
		for part in self.parts:
			if fname in part.files:
				part.rm_file(fname)
				return

class ProjectGit(ProjectBase):
	def __init__(self, git_tag=None, git_remote=None, git_tree_ish=None, directory=None):
		self.init(directory)
		self.git = True
		# TODO, archive only sql directory
		if git_tag:
			args = ["/usr/bin/git", "archive", "--format=tar", git_tag]
		elif git_remote:
			args = ["/usr/bin/git", "archive", "--format=tar", "--remote", git_remote, git_tree_ish]
		else:
			# TODO err msg
			sys.exit(1)
		logging.verbose("Git archive: %s" % (" ".join(args),))
		process = subprocess.Popen(args, bufsize=8192, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, cwd=self.directory or ".")
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
	def __init__(self, part, fname, single_transaction=True, new=False):
		self.number = part
		self.fname = fname
		self.single_transaction = single_transaction
		self.data = ""

		if not new:
			self.load_conf()

	def load_conf(self):
		with open(self.fname) as f:
			end_header = False
			end_header_comment = False
			data_start = False

			for line in f:
				if data_start:
					self.data += line
				else:
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
						end_header = True
					# end header comment
					x = re.match(r"--", line)
					if x and end_header:
						end_header_comment = True
					# end header line
					x = re.match(r"\n", line)
					if x and end_header_comment:
						data_start = True

	def save_conf(self, name, old_version, new_version):
		with open(self.fname, "w") as file:
			file.write(utils.get_header(name, "project-update", part=self, old_version=old_version, new_version=new_version))
			file.write(utils.get_part_header([self], "project-update"))

			if self.data:
				file.write("\n")
				file.write(self.data.strip())
				file.write("\n")

class Update:
	def __init__(self, project_name, old_version, new_version, directory=None):
		self.old_version = old_version
		self.new_version = new_version
		self.project_name = project_name
		if directory:
			self.directory = directory
		else:
			self.directory = find_directory()
		self.parts = []
		pattern = "%s--%s--%s.sql" % (to_fname(project_name), to_fname(old_version), to_fname(new_version))
		fname = os.path.join(self.directory, "sql_dist", pattern)
		if os.path.isfile(fname):
			logging.debug("Update find part: %s" % (fname,))
			self.parts.append(UpdatePart(1, fname))
		pattern = "%s--%s--%s--p*.sql" % (to_fname(project_name), to_fname(old_version), to_fname(new_version))
		for fname in glob.glob(os.path.join(self.directory, "sql_dist", pattern)):
			x = re.match(r".*--p(?P<part>\d+)\.sql", fname)
			if x:
				logging.debug("Update find part: %s" % (fname,))
				part = int(x.group("part"))
				self.parts.append(UpdatePart(part, fname))
		self.parts.sort(key=lambda x: x.number)

	def check_n_repair_parts(self):
		for i, part in enumerate(self.parts):
			if len(self.parts) == 1:
				pattern = os.path.join(self.directory, "sql_dist", "%s--%s--%s.sql" % (to_fname(self.project_name), to_fname(self.old_version), to_fname(self.new_version)))
			else:
				pattern = os.path.join(self.directory, "sql_dist", "%s--%s--%s--p%02d.sql" % (to_fname(self.project_name), to_fname(self.old_version), to_fname(self.new_version), i + 1))

			if part.fname != pattern:
				if os.path.isfile(os.path.join(pattern)):
					return
				os.rename(os.path.join(part.fname), os.path.join(pattern))
				part.fname = pattern

			if part.number != i + 1:
				part.number = i + 1
			part.save_conf(self.project_name, self.old_version, self.new_version)

	def add_part(self, single_transaction=True):
		self.check_n_repair_parts()

		if self.parts:
			new_part = self.parts[-1].number + 1
			fname = "%s--%s--%s--p%02d.sql" % (to_fname(self.project_name), to_fname(self.old_version), to_fname(self.new_version), new_part)
			build_fname = os.path.join(self.directory, "sql_dist", fname)
			self.parts.append(UpdatePart(new_part, build_fname, single_transaction, True))
			self.parts[-1].save_conf(self.project_name, self.old_version, self.new_version)
		self.check_n_repair_parts()

	def rm_part(self, number):
		part_index = None

		for i, part in enumerate(self.parts):
			if part.number == number:
				part_index = i
				break

		if not part_index:
			return

		part = self.parts.pop(part_index)
		os.unlink(os.path.join(part.fname))
		self.check_n_repair_parts()

	def __str__(self):
		return "%s > %s" % (self.old_version, self.new_version)

class Version:
	def __init__(self, directory=None):
		pass

def to_fname(fname):
	return re.sub(r"[^-a-zA-Z0-9.]", "_", fname)

def find_directory(whole_path=False):
	d = os.getcwd()
	dd = 0
	while d:
		logging.debug("Search base directory in: %s" % (d, ))
		if os.path.isdir(os.path.join(d, "sql")) and os.path.isfile(os.path.join(d, "sql", "pg_project.sql")):
			if whole_path:
				return os.path.join(d, 'sql')
			if dd == 0:
				return ''
			return os.path.join(*([".."]*dd))
		d1, x = os.path.split(d)
		if d1 == d:
			break
		d = d1
		dd += 1
	logging.error("Base directory not found.")
	sys.exit(1)

def load_files():
	files = []
	directory = find_directory(True)
	for root, x, files_paths in os.walk(directory):
		for file_name in files_paths:
			if os.path.isfile(os.path.join(root, file_name)) and file_name != 'pg_project.sql':
				files.append(os.path.relpath(os.path.join(root, file_name), directory))
	files.sort()
	return files

def get_normal_fname(file):
	f = os.path.abspath(file)
	(t, fname) = os.path.split(f)
	(t, tname) = os.path.split(t)
	(t, sname) = os.path.split(t)
	return os.path.join(sname, tname, fname)

def project_init(name, directory):
	logging.info("Init project: %s in %s" % (name, directory))
	if not os.path.isdir(os.path.join(directory, "sql")):
		os.makedirs(os.path.join(directory, "sql"))
	if not os.path.isdir(os.path.join(directory, "sql_dist")):
		os.makedirs(os.path.join(directory, "sql_dist"))

	project = ProjectNew(name, directory)
	project.save_conf()

	print("PGdist project inited in %s" % (directory,))

def create_schema(schema_name):
	directory = find_directory()
	for d in ("extensions", "functions", "schema", "tables", "triggers", "types", "views", "grants", "constraints", "data", "indexes"):
		logging.verbose("mkdir %s" % (d, ))
		os.makedirs(os.path.join(directory, "sql", schema_name, d))
	print("Schema %s created." % (schema_name,))

def status():
	absolute_path = find_directory(True)
	project = ProjectFs(find_directory())
	files = load_files()
	logging.debug("Files in project: %s" % (files, ))
	print("PROJECT: %s" % (project.name))
	change = False
	for file in files:
		if not project.is_file(file):
			change = True
			print("NEW FILE: %s" % (os.path.relpath(os.path.join(absolute_path, file), os.getcwd())))

	for part in project.parts:
		for file in part.files:
			if not file in files:
				change = True
				print("REMOVED FILE: %s" % (os.path.relpath(os.path.join(absolute_path, file), os.getcwd())))
	if not change:
		print("Not found new or removed files")

def add(files, all):
	directory = find_directory()
	project = ProjectFs(directory)
	loaded_files = load_files()
	if all:
		files = list(filter(project.is_not_file, loaded_files))
	else:
		files_ok = []
		for file in files:
			if project.is_file(file):
				logging.error("File already in project: %s" % (file,))
				continue
			if file in loaded_files:
				logging.debug("File %s is ok" % (file,))
				files_ok.append(file)
				continue
			if os.path.isfile(file):
				nname = get_normal_fname(file)
				if project.is_file(nname):
					logging.error("File already in project: %s as %s" % (file, nname))
					continue
				logging.debug("File %s prepare to add as %s" % (file, nname))
				files_ok.append(get_normal_fname(file))
				continue
			logging.error("File %s not found." % (file,))
			sys.exit(1)
		files = files_ok
	for file in files:
		print("Added to project:")
		print("\t%s" % (file,))
		project.add_file(file)
	if files:
		print("")
		print("If you need, change order of files in project file sql/pg_project.sql")
		print("")
	project.save_conf()

def rm(files, all):
	directory = find_directory()
	project = ProjectFs(directory)
	if all:
		loaded_files = load_files()
		files = [f for f in project.get_files() if f not in loaded_files]
	else:
		files_ok = []
		for file in files:
			if os.path.isfile(file):
				file = get_normal_fname(file)
			if not project.is_file(file):
				file = os.path.relpath(os.path.join(os.getcwd(), file), os.path.join(directory, 'sql'))

				if not project.is_file(file):
					logging.error("File not in project: %s" % (file,))
					continue
			files_ok.append(file)
		files = files_ok
	for file in files:
		print("Removed from project:")
		print("\t%s" % (file,))
		project.rm_file(file)
	project.save_conf()

def part_add(transaction_type):
	directory = find_directory()
	project = ProjectFs(directory)
	project.add_part(single_transaction=not (transaction_type == "not-single-transaction"))
	project.save_conf()

def part_rm(number, force):
	directory = find_directory()
	project = ProjectFs(directory)
	part = project.rm_part(number)

	if not force and part:
		project.parts[-1].files += part.files
		project.parts[-1].data += part.data

	project.save_conf()

def create_version(version, git_tag, force):
	if git_tag:
		project = ProjectGit(git_tag)
	else:
		project = ProjectFs()
	if not os.path.isdir(os.path.join(project.directory, "sql_dist")):
		os.mkdir(os.path.join(project.directory, "sql_dist"))
	for part in project.parts:
		if len(project.parts) == 1:
			fname = "%s--%s.sql" % (to_fname(project.name), to_fname(version))
		else:
			fname = "%s--%s--p%02d.sql" % (to_fname(project.name), to_fname(version), part.number)
		build_fname = os.path.join(project.directory, "sql_dist", fname)
		if os.path.isfile(build_fname) and not force:
			logging.error("Error file exists: %s" % (build_fname,))
			sys.exit(1)
		logging.verbose("Create file: %s" % (build_fname,))
		with open(build_fname, "w") as build_file:
			if part.number == 1:
				build_file.write(utils.get_header(project.name, "project-version", part=part, roles=project.roles, requires=project.requires, version=version, dbparam=project.dbparam))
			else:
				build_file.write(utils.get_header(project.name, "project-version", part=part, version=version))
			build_file.write(utils.get_part_header([part], "project-version"))

			for pfname in part.files:
				logging.verbose("add file: %s" % (pfname))
				src_file = project.get_file(pfname)
				build_file.write(utils.get_command(src_file.read(), pfname))
				src_file.close()

			build_file.write("\n")
			build_file.write("--\n")
			build_file.write("-- end sqldist project\n")
			build_file.write("--\n")
		print("Created file: %s" % (fname))

def load_requires(project, pg, loop_detect=[]):
	loop2 = loop_detect + [project.name]
	for require in project.requires:
		if require.project_name in loop2:
			logging.error("Error: requires loop: %s" % (" > ".join(loop2)))
		if require.project_name not in pg.loaded_projects_name:
			p = ProjectGit(git_remote=require.git, git_tree_ish=require.tree_ish)
			load_requires(p, pg, loop_detect)
			print("load require project %s to test pg" % (p.name,), file=sys.stderr)
			pg.load_project(p)

def get_test_dbname(project_name, dbs=None):
	if dbs:
		return "pgdist_test_%s_%s_%s" % (getpass.getuser(), project_name, dbs)
	else:
		return "pgdist_test_%s_%s" % (getpass.getuser(), project_name)

def load_and_dump(project, clean=True, no_owner=False, no_acl=False, pre_load=None, post_load=None, updates=None, dbs=None, pg_extractor=None):
	try:
		pg = pg_conn.PG(config.test_db, dbname=get_test_dbname(project.name, dbs))
		pg.init()
		pg.load_file(pre_load)
		load_requires(project, pg)
		print("load project %s to test pg" % (project.name,), file=sys.stderr)
		pg.load_project(project)
		if updates:
			for update in updates:
				print("load update %s %s to test pg" % (project.name, update), file=sys.stderr)
				pg.load_update(update)
		pg.load_file(post_load)
		print("dump structure and data from test pg", file=sys.stderr)
		dump = pg.dump(no_owner, no_acl)
		table_data = pg.dump_data(project)
		if pg_extractor:
			pg.pg_extractor(pg_extractor, no_owner, no_acl)
	except pg_conn.PgError as e:
		logging.error("Load project fail:\n%s" % (e.output))
		if clean:
			pg.clean()
		else:
			print("Check database: %s" % pg.dbname)
		sys.exit(1)
	if clean:
		pg.clean()
	else:
		print("Check database: %s" % pg.dbname)
	return dump, table_data

def load_dump_and_dump(dump_remote, project, table_data=None, clean=True, no_owner=False, no_acl=False, pre_load=None, post_load=None, dbs=None, pg_extractor=None, project_name=None):
	try:
		if not project_name:
			project_name = project.name
		pg = pg_conn.PG(config.test_db, dbname=get_test_dbname(project_name, dbs))
		pg.init()
		pg.load_file(pre_load)
		print("load dump to test pg", file=sys.stderr)
		pg.load_dump(dump_remote)
		if project and table_data:
			pg.load_data(project, table_data)
		pg.load_file(post_load)
		print("dump structure and data from test pg", file=sys.stderr)
		dump = pg.dump(no_owner, no_acl)
		table_data_new = None
		if project:
			table_data_new = pg.dump_data(project)
		if pg_extractor:
			pg.pg_extractor(pg_extractor, no_owner, no_acl)
	except pg_conn.PgError as e:
		logging.error("Load dump fail:\n%s" % (e.output))
		if clean:
			pg.clean()
		else:
			print("Check database: %s" % pg.dbname)
		sys.exit(1)
	if clean:
		pg.clean()
	else:
		print("Check database: %s" % pg.dbname)
	return dump, table_data_new

def load_file_and_dump(fname, project_name="undef", clean=True, no_owner=False, no_acl=False, pre_load=None, post_load=None, dbs=None, pg_extractor=None):
	try:
		pg = pg_conn.PG(config.test_db, dbname=get_test_dbname(project_name, dbs))
		pg.init()
		pg.load_file(pre_load)
		print("load file %s to test pg" % (fname,), file=sys.stderr)
		pg.load_file(fname)
		pg.load_file(post_load)
		print("dump structure and data from test pg", file=sys.stderr)
		dump = pg.dump(no_owner, no_acl)
		if pg_extractor:
			pg.pg_extractor(pg_extractor, no_owner, no_acl)
	except pg_conn.PgError as e:
		logging.error("Load dump fail:\n%s" % (e.output))
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

def test_load(clean=True, pre_load=None, post_load=None, pg_extractor=None, no_owner=False):
	project = ProjectFs()
	dump, x = load_and_dump(project, clean=clean, pre_load=pre_load, post_load=post_load, pg_extractor=pg_extractor)
	if not no_owner:
		logging.info("checking element owners")
		project_types = pg_parser.parse(io.StringIO(dump))
		project_types.check_elements_owner()
	if pg_extractor:
		pg_extractor.print_dump_info()
	print("")
	print("Project %s was loaded successfully." % (project.name))
	print("")

def create_update(git_tag, new_version, force, gitversion=None, clean=True, pre_load=None, post_load=None,
		pre_load_old=None, pre_load_new=None, post_load_old=None, post_load_new=None, part_count=None):
	if not pre_load_old:
		pre_load_old = pre_load
	if not pre_load_new:
		pre_load_new = pre_load

	if not post_load_old:
		post_load_old = post_load
	if not post_load_new:
		post_load_new = post_load

	part_count = int(part_count)
	project_old = ProjectGit(git_tag)
	project_new = ProjectFs()
	if gitversion:
		old_version = gitversion
	else:
		old_version = re.sub(r"^[^\d]*", "", git_tag)
	new_version = re.sub(r"^[^\d]*", "", new_version)

	diff_files = []

	if config.git_diff:
		old_files = project_old.get_files()
		new_files = project_new.get_files()

		for file_name in old_files:
			if file_name not in new_files:
				logging.info("old file removed: %s" % (file_name))

		for file_name in new_files:
			new_file = project_new.get_file(file_name)
			new_string = new_file.read()
			new_file.close()

			if file_name not in old_files:
				diff_files.append([file_name, new_string])
				logging.verbose("new file added: %s" % (file_name))
			else:
				old_file = project_old.get_file(file_name)
				old_string = old_file.read()
				old_file.close()

				if old_string != new_string:
					element = os.path.basename(os.path.dirname(file_name))

					if element == "table" or element == "tables":
						x = re.search(r"CREATE( UNLOGGED)?( FOREIGN)? TABLE (?P<name>\S+) ?\(", new_string)
						print("TODO - table: %s has changed" % (x.group('name')))
						print(utils.diff(old_string.splitlines(), new_string.splitlines(), "\t", True))
					else:
						diff_files.append([file_name, new_string])
						logging.verbose("file changed: %s" % (file_name))

	if not os.path.isdir(os.path.join(project_old.directory, "sql_dist")):
		os.mkdir(os.path.join(project_old.directory, "sql_dist"))

	# first part can be without --p%02d (--p01)
	for part in xrange(part_count):
		if part_count == 1:
			fname_part = ""
		else:
			fname_part = "--p%02d" % (part+1)

		fname = "%s--%s--%s%s.sql" % (to_fname(project_old.name), to_fname(old_version), to_fname(new_version), fname_part)
		build_fname = os.path.join(project_old.directory, "sql_dist", fname)

		if os.path.isfile(build_fname) and not force:
			logging.error("Error file exists: %s" % (build_fname,))
			sys.exit(1)

		logging.verbose("Create file: %s" % (build_fname,))
		update_part = Part(True, part+1)

		with open(build_fname, "w") as build_file:
			build_file.write(utils.get_header(project_new.name, "project-update", part=update_part, roles=project_new.roles, requires=project_new.requires, old_version=old_version, new_version=new_version))
			build_file.write(utils.get_part_header([update_part], "project-update"))

			if config.git_diff and part == 0:
				for diff_file in diff_files:
					build_file.write("-- %s\n\n" % (diff_file[0]))
					build_file.write(diff_file[1])
			elif part == 0:
				dump_old, x = load_and_dump(project_old, clean=clean, pre_load=pre_load_old, post_load=post_load_old, dbs="old")
				dump_new, x = load_and_dump(project_new, clean=clean, pre_load=pre_load_new, post_load=post_load_new, dbs="new")
				pr_old = pg_parser.parse(io.StringIO(dump_old))
				pr_new = pg_parser.parse(io.StringIO(dump_new))
				pr_old.gen_update(build_file, pr_new)
		print("Edit created file: %s" % (build_fname))
		print("and test it by 'pgdist test-update %s %s'" % (git_tag, new_version))

def part_update_add(old_version, new_version, transaction_type=None):
	project = ProjectFs()
	update = Update(project.name, old_version, new_version)
	update.add_part(single_transaction=not (transaction_type == "not-single-transaction"))

def part_update_rm(old_version, new_version, number):
	project = ProjectFs()
	update = Update(project.name, old_version, new_version)
	update.rm_part(number)

def test_update(git_tag, new_version, clean=True, gitversion=None, pre_load=None, post_load=None,
		pre_load_old=None, pre_load_new=None, post_load_old=None, post_load_new=None, pg_extractor=None, no_owner=False):

	if not pre_load_old:
		pre_load_old = pre_load
	if not pre_load_new:
		pre_load_new = pre_load

	if not post_load_old:
		post_load_old = post_load
	if not post_load_new:
		post_load_new = post_load

	if gitversion:
		old_version = gitversion
	else:
		old_version = re.sub(r"^[^\d]*", "", git_tag)
	new_version = re.sub(r"^[^\d]*", "", new_version)

	project_old = ProjectGit(git_tag)
	project_new = ProjectFs()
	upds = []
	upds.append(Update(project_old.name, old_version, new_version))

	dump_updated, table_data_updated = load_and_dump(project_old, clean=clean, pre_load=pre_load_old, post_load=post_load_old, updates=upds, dbs="updated",
		pg_extractor=pg_extractor)
	dump_cur, table_data_cur = load_and_dump(project_new, clean=clean, pre_load=pre_load_new, post_load=post_load_new,
		pg_extractor=pg_extractor)

	if pg_extractor:
		pg_extractor.print_diff()
		pg_extractor.clean()
	else:
		pr_cur = pg_parser.parse(io.StringIO(dump_cur))
		pr_updated = pg_parser.parse(io.StringIO(dump_updated))
		if not no_owner:
			logging.info("checking element owners")
			pr_updated.check_elements_owner()
		pr_updated.diff(pr_cur)

def dump_remote(addr, no_owner, no_acl, cache):
	try:
		pg = pg_conn.PG(addr)
		print("dump remote", file=sys.stderr)
		return pg.dump(no_owner, no_acl, cache=cache)
	except pg_conn.PgError as e:
		logging.error("Dump fail:\n%s" % (e.output))
		sys.exit(1)

def dump_remote_data(project, addr, cache):
	try:
		pg = pg_conn.PG(addr)
		return pg.dump_data(project, cache=cache)
	except pg_conn.PgError as e:
		logging.error("Dump data fail:\n%s" % (e.output))
		sys.exit(1)

def get_roles(addr, cache):
	try:
		pg = pg_conn.PG(addr)
		return pg.get_roles(cache)
	except pg_conn.PgError as e:
		logging.error("Get roles fail:\n%s" % (e.output))
		sys.exit(1)

def create_roles(roles):
	try:
		pg = pg_conn.PG(config.test_db)
		return pg.create_roles(roles=roles)
	except pg_conn.PgError as e:
		logging.error("Create roles fail:\n%s" % (e.output))
		sys.exit(1)

def read_file(fname):
	data = io.StringIO()
	with open(fname, "r") as f:
		data.write(unicode(f.read(), "UTF8"))
	return data.getvalue()

def print_diff(dump1, dump2, data1, data2, diff_raw, no_owner, no_acl, fromfile, tofile, swap=False, ignore_space=False):
	if swap:
		dump1, dump2 = dump2, dump1
		fromfile, tofile = tofile, fromfile
		data1, data2 = data2, data1
	if diff_raw:
		sys.stdout.write(utils.diff(dump1.splitlines(1), dump2.splitlines(1), "", True, fromfile, tofile))
	else:
		pr1 = pg_parser.parse(io.StringIO(dump1))
		pr1.set_data(data1)
		pr2 = pg_parser.parse(io.StringIO(dump2))
		pr2.set_data(data2)
		pr1.diff(pr2, no_owner=no_owner, no_acl=no_acl, ignore_space=ignore_space)

def diff_pg(addr, git_tag, diff_raw, clean, no_owner, no_acl, pre_load=None, post_load=None, pre_remoted_load=None, post_remoted_load=None, swap=False, pg_extractor=None, cache=False, ignore_space=False):
	config.check_set_test_db()
	if git_tag:
		project = ProjectGit(git_tag)
	else:
		project = ProjectFs()

	roles_remote = get_roles(addr, cache)
	sql_remote = dump_remote(addr, no_owner, no_acl, cache)
	create_roles(roles_remote)
	table_data_remote_old = dump_remote_data(project, addr, cache)

	dump_r, table_data_remote_new = load_dump_and_dump(sql_remote, project, table_data_remote_old, clean, no_owner, no_acl, pre_load=pre_remoted_load, post_load=post_remoted_load, dbs="remote", pg_extractor=pg_extractor)

	dump_cur, table_data_cur = load_and_dump(project, clean, no_owner, no_acl, pre_load=pre_load, post_load=post_load, pg_extractor=pg_extractor)

	if pg_extractor:
		pg_extractor.print_diff(swap, ignore_space)
		pg_extractor.clean()
	else:
		print_diff(dump_r, dump_cur, table_data_remote_new, table_data_cur, diff_raw, no_owner, no_acl, fromfile=addr.addr, tofile="local project", swap=swap, ignore_space=ignore_space)

def diff_pg_file(addr, fname, diff_raw, clean, no_owner, no_acl, pre_load=None, post_load=None, pre_remoted_load=None, post_remoted_load=None, swap=False, pg_extractor=None, cache=False, ignore_space=False):
	config.check_set_test_db()

	roles_remote = get_roles(addr, cache)
	sql_remote = dump_remote(addr, no_owner, no_acl, cache)
	create_roles(roles_remote)
	dump_r, x = load_dump_and_dump(sql_remote, None, None, clean, no_owner, no_acl, pre_load=pre_remoted_load, post_load=post_remoted_load, dbs="remote", pg_extractor=pg_extractor, project_name="project")

	dump_file = load_file_and_dump(fname, "project", clean, no_owner, no_acl, pre_load=pre_load, post_load=post_load, dbs="file", pg_extractor=pg_extractor)

	if pg_extractor:
		pg_extractor.print_diff(swap, ignore_space)
		pg_extractor.clean()
	else:
		print_diff(dump_r, dump_file, None, None, diff_raw, no_owner, no_acl, fromfile=addr.addr, tofile=fname, swap=swap, ignore_space=ignore_space)

def role_list():
	project = ProjectFs()
	for role in project.roles:
		print(role)

def role_add(name, arg1, arg2):
	project = ProjectFs()
	if project.get_role(name):
		logging.error("Error: user %s exists" % (name,))
		sys.exit(1)
	role = Role(name)
	role.password = "password" in (arg1, arg2)
	role.login = "login" in (arg1, arg2)
	role.nologin = "nologin" in (arg1, arg2)
	project.roles.append(role)
	project.save_conf()

def role_change(name, arg1, arg2):
	project = ProjectFs()
	role = project.get_role(name)
	if not role:
		logging.error("Error: user %s not exists" % (name,))
		sys.exit(1)
	role.password = "password" in (arg1, arg2)
	role.login = "login" in (arg1, arg2)
	role.nologin = "nologin" in (arg1, arg2)
	project.save_conf()

def role_rm(name):
	project = ProjectFs()
	role = project.get_role(name)
	if not role:
		logging.error("Error: role %s not exists" % (name,))
		sys.exit(1)
	project.roles.remove(role)
	project.save_conf()

def require_add(project_name, git, git_tree_ish):
	project = ProjectFs()
	if project.get_require(project_name):
		logging.error("Error: require %s exists" % (project_name,))
		sys.exit(1)
	project.requires.append(Require(project_name, git, git_tree_ish))
	project.save_conf()

def require_rm(project_name):
	project = ProjectFs()
	require = project.get_require(project_name)
	if not require:
		logging.error("Error: require %s not exists" % (project_name,))
		sys.exit(1)
	project.requires.remove(require)
	project.save_conf()

def dbparam_set(dbparam):
	project = ProjectFs()
	project.dbparam = dbparam
	project.save_conf()

def dbparam_get():
	project = ProjectFs()
	if project.dbparam:
		print(project.dbparam)
	else:
		print("No dbparam.")

def tabledata_add(name, columns):
	project = ProjectFs()
	td = project.get_tabledata(name)
	if td:
		td.columns = columns
	else:
		td = TableData(name, columns)
		project.table_data.append(td)
		project.table_data.sort()
	project.save_conf()

def tabledata_rm(name):
	project = ProjectFs()
	td = project.get_tabledata(name)
	if not td:
		logging.error("Error: data %s not exists" % (name,))
		sys.exit(1)
	project.table_data.remove(td)
	project.save_conf()

def tabledata_list():
	project = ProjectFs()
	for td in project.table_data:
		print(td)
