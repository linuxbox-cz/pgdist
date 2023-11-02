# -*- coding: utf-8 -*-

import os
import re
import sys
import copy
import logging
from distutils.version import LooseVersion

import pg
import json
import print_table

class Role:
	def __init__(self, name, param):
		self.name = name
		self.password = "password" in param
		self.nologin = "nologin" in param
		self.login = "login" in param

	def __str__(self):
		p = [self.name]
		if self.nologin:
			p.append("nologin")
		if self.login:
			p.append("login")
		if self.password:
			p.append("password")
		return " ".join(p)

class ProjectVersionPart:
	def __init__(self, fname, directory, part):
		self.fname = fname
		self.part = part
		self.roles = []
		self.requires = []
		self.single_transaction = True
		self.dbparam = ""
		with(open(os.path.join(directory, fname))) as f:
			for line in f:
				# single_transaction
				x = re.match(r"--\s*single_transaction", line)
				if x:
					self.single_transaction = True
				# not single_transaction
				x = re.match(r"--\s*not\s*single_transaction", line)
				if x:
					self.single_transaction = False
				# role
				x = re.match(r"--\s*role:\s+(?P<role>\S+)(\s+(?P<param>.*))?", line)
				if x:
					self.roles.append(Role(x.group("role"), x.group("param").split("--")[0].split(" ")))
				# require
				x = re.match(r"--\s*require:\s+(?P<project_name>\S+)", line)
				if x:
					self.requires.append(x.group("project_name"))
				# dbparam
				x = re.match(r"--\s*dbparam:\s+(?P<param>.*)", line)
				if x:
					self.dbparam = x.group("param")
				# end pgdist header
				x = re.match(r"--\s*end\s+pgdist\s+header", line)
				if x:
					break

class ProjectVersion:
	def __init__(self, version):
		self.version = LooseVersion(version)
		self.parts = []

	def cmp_text(self, version):
		return self.version == LooseVersion(version)

	def add_part(self, fname, directory, part):
		self.parts.insert(part, ProjectVersionPart(fname, directory, part))
		self.parts.sort(key=lambda x: x.part)


class ProjectUpdatePart:
	def __init__(self, fname, directory, part):
		self.fname = fname
		self.part = part
		self.roles = []
		self.requires = []
		self.single_transaction = True
		with(open(os.path.join(directory, fname))) as f:
			for line in f:
				# single_transaction
				x = re.match(r"--\s*single_transaction", line)
				if x:
					self.single_transaction = True
				# not single_transaction
				x = re.match(r"--\s*not\s*single_transaction", line)
				if x:
					self.single_transaction = False
				# role
				x = re.match(r"--\s*role:\s+(?P<role>\S+)(\s+(?P<param>.*))?", line)
				if x:
					self.roles.append(Role(x.group("role"), x.group("param").split("--")[0].split(" ")))				# end header
				# require
				x = re.match(r"--\s*require:\s+(?P<project_name>\S+)", line)
				if x:
					self.requires.append(x.group("project_name"))
				x = re.match(r"--\s*end\s+header", line)
				if x:
					break

class ProjectUpdate:
	def __init__(self, version_old, version_new):
		self.version_new = LooseVersion(version_new)
		self.version_old = LooseVersion(version_old)
		self.parts = []
		self.failed = False
		self.failed_part = 0

	def __str__(self):
		return "%s -> %s" % (self.version_old, self.version_new)

	def cmp_text(self, version_old, version_new):
		return self.version_old == LooseVersion(version_old) and self.version_new == LooseVersion(version_new)

	def add_part(self, fname, directory, part):
		self.parts.insert(part, ProjectUpdatePart(fname, directory, part))
		self.parts.sort(key=lambda x: x.part)

class  ProjectInstalated:
	def __init__(self, dbname, version, from_version, part, parts):
		self.dbname = dbname
		self.version = LooseVersion(version)
		if from_version:
			self.from_version = LooseVersion(from_version)
		else:
			self.from_version = None
		self.part = part
		self.parts = parts
		self.updates = []
		self.update_failed:int = None

	def __str__(self):
		return "ProjectInstalated: %s, %s, updates: %s" % (self.dbname, self.version, ", ".join(self.updates))

class Project:
	def __init__(self, name):
		self.name = name
		self.updates = []
		self.versions = []
		self.installed = []

	def add_version(self, directory, fname, version, part):
		ver = self.get_version(version)
		if not ver:
			ver = ProjectVersion(version)
			self.versions.append(ver)
		ver.add_part(fname, directory, part)

	def add_update(self, directory, fname, version_old, version_new, part):
		upd = self.get_update(version_old, version_new)
		if not upd:
			upd = ProjectUpdate(version_old, version_new)
			self.updates.append(upd)
		upd.add_part(fname, directory, part)

	def get_version(self, version):
		for v in self.versions:
			if v.cmp_text(version):
				return v
		return None

	def get_update(self, version_old, version_new):
		for v in self.updates:
			if v.cmp_text(version_old, version_new):
				return v
		return None

	def add_installed(self, dbname, version, from_version, part, parts):
		self.installed.append(ProjectInstalated(dbname, version, from_version, part, parts))

	def sort(self):
		self.versions.sort(key=lambda x: x.version)
		self.updates.sort(key=lambda x: (x.version_old, x.version_new))

	def newest_version(self):
		if self.versions:
			return self.versions[-1].version
		else:
			return None

	def get_instalated(self, dbname):
		return [x for x in self.installed if x.dbname == dbname]

	def install(self, dbname, version, conninfo, directory, create_db, is_require):
		for ver in self.versions:
			if ver.version == version:
				pg.install(dbname, self, ver, conninfo, directory, create_db, is_require)
				return

	def find_updates(self, version1, version2):
		best_updatest = []
		while True:
			update = self.find_updates2(version1, version2)
			if update:
				best_updatest.append(update)
				version1 = update.version_new
				if version2 and update.version_new == version2:
					return best_updatest
			elif version2:
				return []
			else:
				return best_updatest

	def find_updates2(self, version1, version2):
		logging.verbose("project: %s find_updates from: %s, to: %s" % (self.name, version1, version2))
		if version2:
			v = [x for x in self.updates if x.version_old == version1 and x.version_new <= version2]
		else:
			v = [x for x in self.updates if x.version_old == version1]
		if v:
			ver = max(v, key=lambda x: x.version_new)
			logging.verbose("\tfound %s" % (ver,))
			return ver
		logging.verbose("\tnot found")
		return None

	def update(self, dbname, update, conninfo, directory):
		pg.update(dbname, self, update, conninfo, directory)

def get_project_name(directory, fname):
	with(open(os.path.join(directory, fname))) as f:
		for line in f:
			x = re.match(r"--\s*name:\s+(?P<name>\S+)", line)
			if x:
				return x.group("name")
			x = re.match(r"--\s*end\s+header", line)
			if x:
				break
	logging.error("Project name not found: %s" % (fname,))
	return None


def get_projects(project_name, dbname, conninfo, directory, check_db_exists=False):
	projects = {}

	if not os.path.isdir(directory):
		logging.info("No such projects directory: '%s'" % (directory,))
		return []

	for fname in os.listdir(directory):
		version = None
		version_old = None
		version_new = None
		(root, ext) = os.path.splitext(fname)
		if ext != ".sql":
			continue
		p = root.split("--")
		# like: project--v1.sql
		if len(p) == 2:
			(f_pr_name, version) = p
			part = 1
		# like: project--v1--p1.sql
		elif len(p) == 3 and re.match(r"p\d+$", p[2]):
			(f_pr_name, version) = p[0:2]
			part = int(p[2][1:])
		# like: project--v1--v2.sql
		elif len(p) == 3:
			(f_pr_name, version_old, version_new) = p
			part = 1
		# like: project--v1--v2--p1.sql
		elif len(p) == 4 and re.match(r"p\d+$", p[3]):
			(f_pr_name, version_old, version_new) = p[0:3]
			part = int(p[3][1:])
		else:
			continue

		pr_name = get_project_name(directory, fname)

		if project_name and project_name != pr_name:
			continue

		if pr_name not in projects:
			projects[pr_name] = Project(pr_name)

		if version:
			projects[pr_name].add_version(directory, fname, version, part)

		if version_old and version_new:
			projects[pr_name].add_update(directory, fname, version_old, version_new, part)

	if check_db_exists:
		if dbname in pg.list_database(conninfo):
			dbs = [dbname]
		else:
			dbs = []
	elif dbname:
		dbs = [dbname]
	else:
		dbs = pg.list_database(conninfo)

	for db in dbs:
		conn = pg.connect(conninfo, dbname=db)
		if pg.check_pgdist_installed(conn):
			pg.check_pgdist_version(db, conn)
			cursor = conn.cursor()
			cursor.execute("SELECT project, version, from_version, part, parts FROM pgdist.installed")
			for row in cursor:
				pr_name = row["project"]
				if not project_name or pr_name == project_name:
					if pr_name not in projects:
						projects[pr_name] = Project(pr_name)
					projects[pr_name].add_installed(db, row["version"], row["from_version"], row["part"], row["parts"])
		conn.close()

	for project in list(projects.values()):
		project.sort()
	return sorted(list(projects.values()),key=lambda x: x.name)


def prlist(project_name, dbname, conninfo, directory, show_all, show_json):
	projects = get_projects(project_name, dbname, conninfo, directory)
	find_projects = False
	list_project=[]

	if not show_json:
		print("")
		print("Available projects:")
		if show_all:
			header = ["project", "version", "all versions"]
		else:
			header = ["project", "version"]
		for project in projects:
			if project.versions or project.updates:
				find_projects = True
				if show_all:
					row_project=[]
					row_project.append(project.name)
					row_project.append(project.newest_version())
					row_project.append(', '.join([str(x.version) for x in project.versions]))
					list_project.append(row_project)
				else:
					row_project=[]
					row_project.append(project.name)
					row_project.append(project.newest_version())
					list_project.append(row_project)
				for update in project.updates:
					if show_all or (project.installed and update.version_old >= min([x.version for x in project.installed])):
						row_project=[]
						if show_all:
							row_project.append("")
						row_project.append("")
						row_project.append("update: {}".format(update))
						list_project.append(row_project)

		if not find_projects:
			print(" No projects found")
		else:
			print_table.table_print(list_project, header)
		print("")

		find_projects = False
		list_project = []

		print("Installed projects:")
		if dbname:
			dbs = [dbname]
		else:
			dbs = pg.list_database(conninfo)

		if show_all:
			header = ["project", "dbname", "version", "from", "part"]
		else:
			header = ["project", "dbname", "version"]
		for db in dbs:
			for project in projects:
				for ins in project.get_instalated(db):
					find_projects = True
					if show_all:
						if ins.from_version:
							fromv = str(ins.from_version)
						else:
							fromv = "-"
						row_project=[]
						row_project.append(project.name)
						row_project.append(ins.dbname)
						row_project.append(ins.version)
						row_project.append(fromv)
						row_project.append(str(ins.part)+"/"+str(ins.parts))
						list_project.append(row_project)
					else:
						row_project=[]
						row_project.append(project.name)
						row_project.append(ins.dbname)
						row_project.append(str(ins.version))
						list_project.append(row_project)

		if not find_projects:
			print(" No installed projects found")
		else:
			print_table.table_print(list_project, header)
		print("")

	else:
		if dbname:
			dbs = [dbname]
		else:
			dbs = pg.list_database(conninfo)

		dict_project = {}
		list_projects = []
		for db in dbs:
			for project in projects:
				for ins in project.get_instalated(db):
					dict_project["project"] = project.name
					dict_project["dbname"] = ins.dbname
					dict_project["version"] = str(ins.version)
					list_projects.append(dict_project.copy())

		json_projects = json.dumps(list_projects, indent = 4)
		print(json_projects)

def history(project_name, dbname, conninfo):
	pg.installed_history(project_name, dbname, conninfo)

def install(project_name, dbname, version, conninfo, directory, create_db, is_require):
	projects = get_projects(project_name, dbname, conninfo, directory, check_db_exists=create_db)

	if not projects:
		logging.error("Project %s not found" % (project_name,))
		sys.exit(1)

	project = projects[0]
	ins = project.get_instalated(dbname)

	if version:
		need_ver = LooseVersion(version)
	else:
		need_ver = project.newest_version()


	if not ins:
		project.install(dbname, need_ver, conninfo, directory, create_db, is_require)
		if not is_require:
			print("Complete!")
	elif need_ver > ins[0].version:
		update(project_name, dbname, version, conninfo, directory, False)
	else:
		logging.error("Project %s is installed." % (project_name,))
		sys.exit(1)

def check_update(project_name, dbname, version, conninfo, directory, show_json):
	update(project_name, dbname, version, conninfo, directory, show_json, check=True)

def update(project_name, dbname, version, conninfo, directory, show_json=False, check=False):
	if project_name == "-":
		project_name = None
	if dbname == "-":
		dbname = None

	projects = get_projects(project_name, dbname, conninfo, directory)
	if project_name and not projects:
		logging.error("Project %s not found" % (project_name,))
		sys.exit(1)

	exists_updates = False
	for project in projects:
		for ins in project.installed:

		# check if all parts in all projects are installed, if not, try to update not updated parts again
			if ins.part != ins.parts:
				for upd in project.updates:
					if upd.version_new == ins.version and upd.version_old == ins.from_version:
						ins_update = copy.deepcopy(upd)
						ins_update.failed = True
						ins_update.failed_part = ins.part
						ins.updates.append(ins_update)

			ins.updates += project.find_updates(ins.version, version)

			if ins.updates:
				exists_updates = True


	list_project = []
	if not show_json:
		if exists_updates:
			print("")
			print("Project updates:")
			header = ["project", "dbname", "update", ""]
			for project in projects:
				for ins in project.installed:
					if ins.updates:
						for update in ins.updates:
							row_project = []
							row_project.append(project.name)
							row_project.append(ins.dbname)
							row_project.append(update)
							if ins.part != ins.parts and update.failed:
								row_project.append(f"Update continue from part {ins.part + 1}/{ins.parts}.")
							list_project.append(row_project)

			print_table.table_print(list_project, header)
			print("")
		else:
			print("Nothing to do.")
	else:
		dict_project = {}
		list_projects = []
		for project in projects:
				for ins in project.installed:
					if ins.updates:
						for update in ins.updates:
							dict_project["project"] = project.name
							dict_project["dbname"] = ins.dbname
							dict_project["update"] = str(update)
							list_projects.append(dict_project.copy())

		json_projects = json.dumps(list_projects, indent = 4)
		print(json_projects)
	if check:
		return

	for project in projects:
		for ins in project.installed:
			for update in ins.updates:
				project.update(ins.dbname, update, conninfo, directory)
	print("Complete!")

def update_status(conninfo, directory, show_json):
	projects = get_projects(None, None, conninfo, directory)
	dbs = pg.list_database(conninfo)

	updates = 0
	installed_projects = 0
	for db in dbs:
		for project in projects:
			for ins in project.get_instalated(db):
				if ins.version < project.newest_version():
					updates += 1
				installed_projects += 1

	if show_json:
		json_count = { 'project_count': installed_projects, 'update_count':  updates}
		print(json.dumps(json_count))
	else:
		print('Installed projects count:', installed_projects)
		print('Projects update count:', updates)


def clean(project_name, dbname, conninfo):
	pg.clean(project_name, dbname, conninfo)

def set_version(project_name, dbname, version, conninfo):
	pg.set_version(project_name, dbname, version, conninfo)

def get_version(project_name, dbname, conninfo):
	version = pg.get_version(project_name, dbname, conninfo)
	if version:
		print(version)
	else:
		logging.error("Not found %s in db %s" % (project_name, dbname))
		sys.exit(1)

def pgdist_update(dbname, conninfo):
	pg.pgdist_update(dbname, conninfo)


