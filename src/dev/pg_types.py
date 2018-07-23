
import re
import sys
import difflib

import color

def rmln(s):
	if s and s.endswith("\r\n"):
		return s[:-2]
	if s and s.endswith("\n"):
		return s[:-1]
	return s

class Element:
	def __init__(self, command=None, name=None):
		self.command = command
		self.name = name
		if "." in self.name:
			self.schema = name.split(".")[0]
		else:
			self.schema = None
		self.owner = None
		self.grant = []
		self.revoke = []

	def __str__(self):
		return self.name

	def print_info(self):
		print("Element:", self.command)

	def diff(self, element2, no_owner, no_acl):
		self._diff(element2)
		if not no_owner and self.owner != element2.owner:
			print("%s %s change owner from: %s to: %s" % (self.element_name, self.name, self.owner, element2.owner))

		self.grant.sort()
		element2.grant.sort()
		self.revoke.sort()
		element2.revoke.sort()

		if not no_acl and self.grant != element2.grant or self.revoke != element2.revoke:
			print("%s %s change privileges:" % (self.element_name, self.name))
			for grant in self.grant:
				if grant not in element2.grant:
					print(color.red("\t-"+rmln(grant)))
			for grant in element2.grant:
				if grant not in self.grant:
					print(color.green("\t+"+rmln(grant)))
			for revoke in self.revoke:
				if revoke not in element2.revoke:
					print(color.red("\t-"+rmln(revoke)))
			for revoke in element2.revoke:
				if revoke not in self.revoke:
					print(color.green("\t+"+rmln(revoke)))
			print("")

	def _diff(self, element2):
		if self.command != element2.command:
			print("%s %s is different" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(self.command.splitlines(1), element2.command.splitlines(1), fromfile=self.name, tofile=element2.name)
			for d in diff_c:
				if d.startswith("-"):
					sys.stdout.write(color.red(d))
				elif d.startswith("+"):
					sys.stdout.write(color.green(d))
				else:
					sys.stdout.write(d)
			print("")

	def drop_info(self):
		return re.sub(r"^", "--", self.command, flags=re.MULTILINE)

	def update_element(self, file, element2):
		if self.command == element2.command:
			return
		file.write("--TODO ALTER OR DROP?\n")
		file.write(re.sub(r"^", "--", self.command, flags=re.MULTILINE))
		file.write("\n\n")
		file.write(element2.command)
		file.write("\n")

class Project:
	def __init__(self):
		self.schemas = {}
		self.extentions = {}
		self.types = {}
		self.functions = {}
		self.sequences = {}
		self.views = {}
		self.tables = {}

	def print_info(self):
		for schema in sorted(self.schemas):
			self.schemas[schema].print_info()
		for extention in sorted(self.extentions):
			self.extentions[extention].print_info()
		for type in sorted(self.types):
			self.types[type].print_info()

	def diff(self, project2, no_owner=False, no_acl=False):
		exclude_schemas = self.diff_elements([], "schemas", self.schemas, project2.schemas, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "extentions", self.extentions, project2.extentions, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "types", self.types, project2.types, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "tables", self.tables, project2.tables, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "sequences", self.sequences, project2.sequences, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "views", self.views, project2.views, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "functions", self.functions, project2.functions, no_owner, no_acl)

	def diff_elements(self, exclude_schemas, elements_name, elements1, elements2, no_owner, no_acl):
		difference = []

		new_elements = []
		for name in sorted(elements2):
			if elements2[name].schema not in exclude_schemas and name not in elements1:
				difference.append(name)
				new_elements.append(elements2[name])
		if new_elements:
			print("New %s:" % (elements_name,))
			for new_element in new_elements:
				print(color.green("\t%s" % (new_element,)))
			print("")

		removed_elements = []
		for name in sorted(elements1):
			if elements1[name].schema not in exclude_schemas and name not in elements2:
				difference.append(name)
				removed_elements.append(elements1[name])
		if removed_elements:
			print("Removed %s:" % (elements_name,))
			for removed_element in removed_elements:
				print(color.red("\t%s" % (removed_element,)))
			print("")

		for name in sorted(elements1):
			if elements1[name].schema not in exclude_schemas and name in elements2:
				elements1[name].diff(elements2[name], no_owner, no_acl)
		return difference

	def gen_update(self, file, project2):
		self.update_elements(file, "schemas", self.schemas, project2.schemas)
		self.update_elements(file, "extentions", self.extentions, project2.extentions)
		self.update_elements(file, "types", self.types, project2.types)
		self.update_elements(file, "tables", self.tables, project2.tables)
		self.update_elements(file, "sequences", self.sequences, project2.sequences)
		self.update_elements(file, "views", self.views, project2.views)
		self.update_elements(file, "functions", self.functions, project2.functions)

	def update_elements(self, file, elements_name, elements1, elements2):
		for name in elements1:
			if name not in elements2:
				file.write("--TODO DROP?\n")
				#file.write(re.sub(r"^", "--", elements1[name].command, flags=re.MULTILINE))
				file.write(elements1[name].drop_info())
				file.write("\n\n")

		for name in elements2:
			if name not in elements1:
				file.write(elements2[name].command)
				file.write("\n")

		for name in elements1:
			if name in elements2:
				elements1[name].update_element(file, elements2[name])

class Schema(Element):
	def __init__(self, command, name):
		Element.__init__(self, command, name)
		self.element_name = "Schema"

class Extention(Element):
	def __init__(self, command, name, schema_name):
		Element.__init__(self, command, name)
		self.element_name = "Extention"
		self.schema_name = schema_name

class Enum(Element):
	def __init__(self, command, name, labels):
		Element.__init__(self, command, name)
		self.element_name = "Enum"
		self.labels = labels

class Type(Element):
	def __init__(self, command, name, attributes):
		Element.__init__(self, command, name)
		self.element_name = "Type"
		self.attributes = attributes

class Table(Element):
	def __init__(self, command, name, columns):
		Element.__init__(self, command, name)
		self.element_name = "Table"
		self.columns = columns
		self.defaults = []
		self.indexes = []
		self.triggers = []
		self.constraints = []

	def _diff(self, table2):
		columns1 = sorted(self.columns)
		columns2 = sorted(table2.columns)
		if columns1 != columns2:
			print("%s %s is different:" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(columns1, columns2, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					print("\t"+color.red(d))
				elif d.startswith("+"):
					print("\t"+color.green(d))
			print("")

		self.constraints.sort()
		table2.constraints.sort()
		if self.constraints != table2.constraints:
			print("%s %s have different constraints:" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(self.constraints, table2.constraints, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					print("\t"+color.red(d))
				elif d.startswith("+"):
					print("\t"+color.green(d))
			print("")

		self.defaults.sort()
		table2.defaults.sort()
		if self.defaults != table2.defaults:
			print("%s %s have different defaults:" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(self.defaults, table2.defaults, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					print("\t"+color.red(d))
				elif d.startswith("+"):
					print("\t"+color.green(d))
			print("")

		self.indexes.sort()
		table2.indexes.sort()
		if self.indexes != table2.indexes:
			print("%s %s have different indexes:" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(self.indexes, table2.indexes, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					print("\t"+color.red(d))
				elif d.startswith("+"):
					print("\t"+color.green(d))
			print("")

		self.triggers.sort()
		table2.triggers.sort()
		if self.triggers != table2.triggers:
			print("%s %s have different triggers:" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(self.triggers, table2.triggers, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					print("\t"+color.red(d))
				elif d.startswith("+"):
					print("\t"+color.green(d))
			print("")

	def update_element(self, file, table2):
		if self.command == table2.command:
			return
		file.write("--TODO ALTER TABLE %s\n" % (self.name,))
		columns1 = sorted(self.columns)
		columns2 = sorted(table2.columns)
		if columns1 != columns2:
			diff_c = difflib.unified_diff(columns1, columns2, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					file.write(d+"\n")
				elif d.startswith("+"):
					file.write(d+"\n")
			file.write("\n")

		self.constraints.sort()
		table2.constraints.sort()
		if self.constraints != table2.constraints:
			diff_c = difflib.unified_diff(self.constraints, table2.constraints, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					file.write(d+"\n")
				elif d.startswith("+"):
					file.write(d+"\n")
			file.write("\n")

		self.defaults.sort()
		table2.defaults.sort()
		if self.defaults != table2.defaults:
			diff_c = difflib.unified_diff(self.defaults, table2.defaults, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					file.write(d+"\n")
				elif d.startswith("+"):
					file.write(d+"\n")
			file.write("\n")

		self.indexes.sort()
		table2.indexes.sort()
		if self.indexes != table2.indexes:
			diff_c = difflib.unified_diff(self.indexes, table2.indexes, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					file.write(d+"\n")
				elif d.startswith("+"):
					file.write(d+"\n")
			file.write("\n")

		self.triggers.sort()
		table2.triggers.sort()
		if self.triggers != table2.triggers:
			diff_c = difflib.unified_diff(self.triggers, table2.triggers, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					file.write(d+"\n")
				elif d.startswith("+"):
					file.write(d+"\n")
			file.write("\n")
		file.write("\n")

class Range(Element):
	pass

class Function(Element):
	def __init__(self, command, name, args):
		Element.__init__(self, command, name+args)
		self.element_name = "Function"
		self.fname = name
		self.args = args

	def update_element(self, file, element2):
		if self.command == element2.command:
			return
		file.write("--TODO ALTER OR DROP?\n")
		file.write(re.sub(r"^", "--", re.sub(r"\s*AS\s*[$]\S*[$].*", "", self.command, flags=re.MULTILINE|re.DOTALL), flags=re.MULTILINE))
		file.write("\n\n")
		file.write(element2.command)
		file.write("\n")

	def drop_info(self):
		return re.sub(r"^", "--", re.sub(r"\s*AS\s*[$]\S*[$].*", "", self.command, flags=re.MULTILINE|re.DOTALL), flags=re.MULTILINE)

class Sequence(Element):
	pass

class View(Element):
	pass


