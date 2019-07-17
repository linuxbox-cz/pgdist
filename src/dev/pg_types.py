# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import sys
import difflib

import color
import table_print

def rmln(s):
	if s and s.endswith("\r\n"):
		return s[:-2]
	if s and s.endswith("\n"):
		return s[:-1]
	return s

class Element:
	def __init__(self, element_name, command=None, name=None):
		self.element_name = element_name
		self.name = name
		if "." in self.name:
			self.schema, ws_name = name.split(".")
			self.command = re.sub(re.escape(ws_name), name, command, 1)
		else:
			self.schema = None
			self.command = command
		self.owner = None
		self.comment = None
		self.grant = []
		self.revoke = []
		self.rule = []

	def __str__(self):
		return self.name

	def print_info(self):
		print("Element:", self.command)

	def diff(self, element2, no_owner, no_acl, ignore_space=False):
		self._diff(element2, ignore_space)
		if not no_owner and self.owner != element2.owner:
			print("%s %s change owner from: %s to: %s" % (self.element_name, self.name, self.owner, element2.owner))

		self.grant.sort()
		element2.grant.sort()
		self.revoke.sort()
		element2.revoke.sort()
		self.rule.sort()
		element2.rule.sort()

		if not no_acl and self.grant != element2.grant or self.revoke != element2.revoke or self.rule != element2.rule or self.comment != element2.comment:
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
			for rule in self.rule:
				if rule not in element2.rule:
					print(color.red("\t-"+rmln(rule)))
			for rule in element2.rule:
				if rule not in self.rule:
					print(color.green("\t+"+rmln(rule)))
			if self.comment:
				print(color.red("\t-"+rmln(self.comment)))
			if element2.comment:
				print(color.green("\t+"+rmln(element2.comment)))
			print("")

	def _diff(self, element2, ignore_space):
		command1 = self.command
		command2 = element2.command
		space = ""
		if ignore_space:
			command1 = re.sub(r"^(\t| )+", "", command1, flags=re.MULTILINE|re.DOTALL)
			command2 = re.sub(r"^(\t| )+", "", command2, flags=re.MULTILINE|re.DOTALL)
			command1 = re.sub(r"(\t| )+$", "", command1, flags=re.MULTILINE|re.DOTALL)
			command2 = re.sub(r"(\t| )+$", "", command2, flags=re.MULTILINE|re.DOTALL)
			command1 = re.sub(r"(\t| )+", " ", command1, flags=re.MULTILINE|re.DOTALL)
			command2 = re.sub(r"(\t| )+", " ", command2, flags=re.MULTILINE|re.DOTALL)
			space = "\t"
		if command1 != command2:
			print("%s %s is different" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(command1.splitlines(1), command2.splitlines(1), fromfile=self.name, tofile=element2.name)
			for d in diff_c:
				if d.startswith("-"):
					sys.stdout.write(color.red(space + d))
				elif d.startswith("+"):
					sys.stdout.write(color.green(space + d))
				else:
					sys.stdout.write(space + d)
			print("")

	def drop_info(self):
		return "--TODO DROP?\n" + re.sub(r"^", "--", self.command, flags=re.MULTILINE)

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
		self.operators = {}
		self.tables = {}
		self.table_data = {}

	def print_info(self):
		for schema in sorted(self.schemas):
			self.schemas[schema].print_info()
		for extention in sorted(self.extentions):
			self.extentions[extention].print_info()
		for type in sorted(self.types):
			self.types[type].print_info()

	def diff(self, project2, no_owner=False, no_acl=False, ignore_space=False):
		exclude_schemas = self.diff_elements([], "schemas", self.schemas, project2.schemas, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "extentions", self.extentions, project2.extentions, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "types", self.types, project2.types, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "tables", self.tables, project2.tables, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "sequences", self.sequences, project2.sequences, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "views", self.views, project2.views, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "operators", self.operators, project2.operators, no_owner, no_acl)
		self.diff_elements(exclude_schemas, "functions", self.functions, project2.functions, no_owner, no_acl, ignore_space)
		self.diff_data(project2)

	def diff_data(self, project2):
		for table in sorted(self.table_data.keys()):
			if not table in project2.table_data:
				continue
			d1 = self.table_data[table]
			d2 = project2.table_data[table]
			if sorted(d1[0]) != sorted(d2[0]):
				# Tables table have different columns!
				continue
			if d1[0] != d2[0]:
				m = map(lambda x: d1[0].index(x), d2[0])
				new_d = []
				for row in d2:
					new_r = []
					new_d.append(new_r)
					for i in m:
						new_r.append(row[i])
				d2 = new_d

			table_pr = table_print.TablePrint(d1[0])
			for i in xrange(1, len(d1)):
				row1 = d1[i]
				find = False
				for j in xrange(1, len(d2)):
					row2 = d2[j]
					if row1 == row2:
						find = True
						d2.remove(row2)
						break
				if not find:
					table_pr.add(row1, "- |")
			for j in xrange(1, len(d2)):
				row2 = d2[j]
				table_pr.add(row2, "+ |")
			table_pr.sort()
			if table_pr.data:
				print("Tables %s have different data:" % (table, ))
				for line in table_pr.format().splitlines():
					if line.startswith("+"):
						print(color.green("\t%s" % (line,)))
					elif line.startswith("-"):
						print(color.red("\t%s" % (line,)))
					else:
						print("\t%s" % (line,))
				print("\n")


	def diff_elements(self, exclude_schemas, elements_name, elements1, elements2, no_owner, no_acl, ignore_space=False):
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
				elements1[name].diff(elements2[name], no_owner, no_acl, ignore_space)
		return difference

	def gen_update(self, file, project2):
		self.update_elements(file, "schemas", self.schemas, project2.schemas)
		self.update_elements(file, "extentions", self.extentions, project2.extentions)
		self.update_elements(file, "types", self.types, project2.types)
		self.update_elements(file, "tables", self.tables, project2.tables)
		self.update_elements(file, "sequences", self.sequences, project2.sequences)
		self.update_elements(file, "views", self.views, project2.views)
		self.update_elements(file, "operators", self.operators, project2.operators)
		self.update_elements(file, "functions", self.functions, project2.functions)

	def update_elements(self, file, elements_name, elements1, elements2):
		for name in elements1:
			if name not in elements2:
				file.write(elements1[name].drop_info())
				file.write("\n\n")

		for name in elements2:
			if name not in elements1:
				file.write(elements2[name].command)
				file.write("\n")

		for name in elements1:
			if name in elements2:
				elements1[name].update_element(file, elements2[name])

	def set_data(self, data):
		if data is None:
			self.table_data = {}
		else:
			self.table_data = data

class Schema(Element):
	def __init__(self, command, name):
		Element.__init__(self, "Schema", command, name)

class Extention(Element):
	def __init__(self, command, name, schema_name):
		Element.__init__(self, "Extention", command, name)
		self.schema_name = schema_name

class Enum(Element):
	def __init__(self, command, name, labels):
		Element.__init__(self, "Enum", command, name)
		self.labels = labels

class Type(Element):
	def __init__(self, command, name, attributes):
		Element.__init__(self, "Type", command, name)
		self.attributes = attributes

class Table(Element):
	def __init__(self, command, name, columns):
		Element.__init__(self, "Table", command, name)
		self.columns = columns
		self.defaults = []
		self.indexes = []
		self.triggers = []
		self.constraints = []
		self.columns_comment = []
		self.columns_conf = []

	def _diff(self, table2, ignore_space):
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


		self.columns_comment.sort()
		table2.columns_comment.sort()
		if self.columns_comment != table2.columns_comment:
			print("%s %s have different columns comment:" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(self.columns_comment, table2.columns_comment, fromfile="removeline542358", tofile="removeline542358")
			for d in diff_c:
				if "removeline542358" in d:
					pass
				elif d.startswith("-"):
					print("\t"+color.red(d))
				elif d.startswith("+"):
					print("\t"+color.green(d))
			print("")

		self.columns_conf.sort()
		table2.columns_conf.sort()
		if self.columns_conf != table2.columns_conf:
			print("%s %s have different columns conf:" % (self.element_name, self.name))
			diff_c = difflib.unified_diff(self.columns_conf, table2.columns_conf, fromfile="removeline542358", tofile="removeline542358")
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
	def __init__(self, command, name):
		Element.__init__(self, "Range", command, name)

class Function(Element):
	def __init__(self, command, name, args):
		Element.__init__(self, "Function", command, name+args)
		self.fname = name
		self.args = args

	def update_element(self, file, element2):
		if self.command == element2.command:
			return
		file.write("\n")
		command = re.sub("^CREATE FUNCTION", "CREATE OR REPLACE FUNCTION", element2.command)
		file.write(command)
		file.write("\n")

	def drop_info(self):
		return "DROP FUNCTION %s%s;" % (self.fname, self.args)

class Sequence(Element):
	def __init__(self, command, name):
		Element.__init__(self, "Sequence", command, name)

class View(Element):
	def __init__(self, command, name):
		Element.__init__(self, "View", command, name)

class Operator(Element):
	def __init__(self, command, name, leftarg, rightarg):
		Element.__init__(self, "Operator", command, name+"("+leftarg+","+rightarg+")")

