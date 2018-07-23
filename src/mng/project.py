
import os
import re
import sys
import logging
from distutils.version import LooseVersion

import pg

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

class ProjectVersionPart:
	def __init__(self, fname, directory, part):
		self.fname = fname
		self.part = part
		self.roles = []
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
					self.roles.append(Role(x.group("role"), x.group("param").split("--")[0].split(" ")))
				# end pgdist header
				x = re.match(r"--\s*end\s+pgdist\s+header", line)
				if x:
					break

class ProjectVersion:
	def __init__(self, version):
		self.version = LooseVersion(version)
		self.parts = []

	def cmp_text(self, version):
		return self.version == version

	def add_part(self, fname, directory, part):
		self.parts.insert(part, ProjectVersionPart(fname, directory, part))
		self.parts.sort(key=lambda x: x.part)


class ProjectUpdatePart:
	def __init__(self, fname, directory, part):
		self.fname = fname
		self.part = part
		self.roles = []
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
				x = re.match(r"--\s*end\s+header", line)
				if x:
					break

class ProjectUpdate:
	def __init__(self, version_old, version_new):
		self.version_new = LooseVersion(version_new)
		self.version_old = LooseVersion(version_old)
		self.parts = []

	def cmp_text(self, version_old, version_new):
		return self.version_old == version_old and self.version_new == version_new

	def add_part(self, fname, directory, part):
		self.parts.insert(part, ProjectUpdatePart(fname, directory, part))
		self.parts.sort(key=lambda x: x.part)

class  ProjectInstalated:
	def __init__(self, dbname, version, from_version, part, parts):
		self.dbname = dbname
		self.version = LooseVersion(version)
		self.from_version = LooseVersion(from_version)
		self.part = part
		self.parts = parts
		self.updates = []

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

	def install(self, dbname, version, conninfo, directory, verbose):
		for ver in self.versions:
			if ver.version == version:
				pg.install(dbname, self, ver, conninfo, directory, verbose)
				return
		
	def find_updates(self, version1, version2):
		best_updatest = []
		while True:
			update = self.find_updates2(version1, version2)
			if not update:
				if version2:
					return []
				else:
					return best_updatest
			best_updatest.append(update)
			if version2 and update.version_new == version2:
				return best_updatest
			version1 = update.version_new

	def find_updates2(self, version1, version2):
		if version2:
			v = [x for x in self.updates if x.version_old == version1 and x.version_new <= version2]
		else:
			v = [x for x in self.updates if x.version_old == version1]
		if v:
			return max(v, key=lambda x: x.version_new)
		return None

	def update(self, dbname, update, conninfo, directory, verbose):
		pg.update(dbname, self, update, conninfo, directory, verbose)

def get_projects(project_name, dbname, conninfo, directory):
	projects = {}
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
			(pr_name, version) = p
			part = 1
		# like: project--v1--p1.sql
		elif len(p) == 3 and re.match(r"p\d+$", p[2]):
			(pr_name, version) = p[0:2]
			part = int(p[2][1:])
		# like: project--v1--v2.sql
		elif len(p) == 3:
			(pr_name, version_old, version_new) = p
			part = 1
		# like: project--v1--v2--p1.sql
		elif len(p) == 4 and re.match(r"p\d+$", p[3]):
			(pr_name, version_old, version_new) = p[0:3]
			part = int(p[3][1:])
		else:
			continue

		if project_name and project_name != pr_name:
			continue

		if pr_name not in projects:
			projects[pr_name] = Project(pr_name)

		if version:
			projects[pr_name].add_version(directory, fname, version, part)

		if version_old and version_new:
			projects[pr_name].add_update(directory, fname, version_old, version_new, part)

	if dbname:
		dbs = [dbname]
	else:
		dbs = pg.list_database(conninfo)

	for db in dbs:
		conn = pg.connect(conninfo, dbname=db)
		if pg.check_pgdist_installed(conn):
			pg.check_pgdist_version(conn)
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


def prlist(project_name, dbname, conninfo, directory, show_all):
	projects = get_projects(project_name, dbname, conninfo, directory)
	find_projects = False
	if projects:
		print("Available projects:")
	for project in projects:
		if project.versions or project.updates:
			find_projects = True
			if show_all:
				print("%s\t%s\t(%s)" % (project.name, project.newest_version(), ', '.join([str(x.version) for x in project.versions])))
			else:
				print("%s\t%s" % (project.name, project.newest_version()))
			for update in project.updates:
				print("\tupdate\t%s -> %s" % (update.version_old, update.version_new))
	if not find_projects:
		print("No projects found")

	print("")

	if projects:
		print("Installed projects:")

	if dbname:
		dbs = [dbname]
	else:
		dbs = pg.list_database(conninfo)

	if show_all:
		print("dbname\tproject\tversion\tfrom_version\tpart/parts")
	else:
		print("dbname\tproject\tversion")
	for db in dbs:
		for project in projects:
			for ins in project.get_instalated(db):
				if show_all:
					print("%s\t%s\t%s\t%s\t%d/%d" % (ins.dbname, project.name, ins.version, ins.from_version, ins.part, ins.parts))
				else:
					print("%s\t%s\t%s" % (ins.dbname, project.name, ins.version))

	print("")

def install(project_name, dbname, version, conninfo, directory, verbose):
	projects = get_projects(project_name, dbname, conninfo, directory)
	projects = [x for x in projects if x.name == project_name]
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
		project.install(dbname, need_ver, conninfo, directory, verbose)
	elif need_ver > ins[0].version:
		update(project_name, dbname, version, conninfo, directory, verbose)
	else:
		logging.error("Project %s is installed." % (project_name,))
		sys.exit(1)

def update(project_name, dbname, version, conninfo, directory, verbose):
	projects = get_projects(project_name, dbname, conninfo, directory)
	if project_name and not projects:
		logging.error("Project %s not found" % (project_name,))
		sys.exit(1)

	check_succesfull_installed(projects)

	for project in projects:
		for ins in project.installed:
			updates = project.find_updates(ins.version, version)
			ins.updates = updates
			if updates:
				for update in updates:
					print("%s\t%s\tfrom: %s\tto: %s" % (ins.dbname, project.name, update.version_old, update.version_new))

	for project in projects:
		for ins in project.installed:
			for update in ins.updates:
				project.update(ins.dbname, update, conninfo, directory, verbose)

def check_succesfull_installed(projects):
	for project in projects:
		for ins in project.installed:
			if ins.part != ins.parts:
				logging.error("%s in db %s fail in upgrade from %s to %s ")
				# TODO, what do in this case?
				sys.exit(1)

def clean(project_name, dbname, conninfo):
	pg.clean(project_name, dbname, conninfo)

def set_version(project_name, dbname, version, conninfo):
	pg.set_version(project_name, dbname, version, conninfo)

def pgdist_update(dbname, conninfo):
	pg.pgdist_update(dbname, conninfo)


