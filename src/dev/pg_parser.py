# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import re
import logging
import io

from pg_types import *

def schema(set_schema, object_name):
	if '.' in object_name:
		return object_name
	return set_schema +'.'+ object_name

class Tokens:
	def __init__(self, stream):
		self.stream = stream
		self.buf = io.StringIO()
		self.comment_stop_pos = -1
		self.next_char0 = ''
		self.next_char1 = self.stream.read(1)
		self.next_char2 = self.stream.read(1)

	def __iter__(self):
		return next(self)

	def read_next(self):
		self.buf.write(self.next_char1)
		self.next_char0 = self.next_char1
		self.next_char1 = self.next_char2
		self.next_char2 = self.stream.read(1)

	def comment_stop(self):
		self.comment_stop_pos = self.buf.tell()

	def read_multi_comment(self):
		while True:
			if self.next_char1 == '/' and self.next_char2 == '*':
				self.read_next()
				self.read_multi_comment()
			if self.next_char1 == '*' and self.next_char2 == '/':
				self.read_next()
				return
			if self.next_char1 == '':
				return
			self.read_next()


	def next(self):
		buf = io.StringIO()
		while True:
			# command
			if self.next_char0 in ('\n', '') and self.next_char1 == '\\':
				if self.comment_stop_pos == -1:
					self.comment_stop()
				while self.next_char1 != '\n' and self.next_char1 != '':
					self.read_next()
				self.read_next()
				self.buf.seek(0)
				if self.comment_stop_pos == -1:
					yield '', self.buf.getvalue()
				else:
					yield self.buf.getvalue()[:self.comment_stop_pos], self.buf.getvalue()[self.comment_stop_pos:]
				self.buf.truncate()
				self.comment_stop_pos = -1

			# skip space
			if self.next_char1 in ' \n\r\t' and self.next_char1 != '':
				self.read_next()
				continue
			# line comment
			if self.next_char1 == '-' and self.next_char2 == '-':
				while self.next_char1 != '\n' and self.next_char1 != '':
					self.read_next()
				continue
			# multi line comment
			# TODO multi /* /* */ */
			if self.next_char1 == '/' and self.next_char2 == '*':
				self.read_next()
				self.read_multi_comment()
				self.read_next()
				continue
			# text 'blabla'
			if self.next_char1 == "'":
				self.read_next()
				while True:
					if self.next_char1 == "'" and self.next_char2 == "'":
						self.read_next()
						self.read_next()
						continue
					if self.next_char1 == "'" or self.next_char1 == '':
						self.read_next()
						break
					self.read_next()
				continue
			# text $$ or $...$
			if self.next_char1 == '$':
				# find stop str
				stop = ''
				while  True:
					self.read_next()
					#print 'xxxx', self.next_char1
					if self.next_char1 == '$' or self.next_char1 == '':
						self.read_next()
						break
					stop += self.next_char1
				#print 'stop', stop
				stop_test = ''
				end = False
				while True:
					#print 'cekam na konec...', self.next_char1
					if self.next_char1 == '$':
						self.read_next()
						while True:
							#print 'cekam na konec konce...', self.next_char1
							#print 'stop_test', stop_test
							if self.next_char1 == '$':
								#print 'zeby konec konce?', stop, stop_test, stop == stop_test
								#print '1 end '*5
								if stop == stop_test:
									end = True
									break
								self.read_next()
								stop_test = ''
							stop_test += self.next_char1
							self.read_next()
					self.read_next()
					#print 'end?'
					if end:
						#print '2 end '*5
						break
				continue


			if self.next_char1 != ';' and self.next_char1 != '':
				if self.comment_stop_pos == -1:
					self.comment_stop()
				self.read_next()
				continue
			self.read_next()
			if self.next_char1 == '\n':
				self.read_next()
			self.buf.seek(0)
			if self.comment_stop_pos == -1:
				yield self.buf.getvalue(), ''
			else:
				yield self.buf.getvalue()[:self.comment_stop_pos], self.buf.getvalue()[self.comment_stop_pos:]
			self.buf.truncate()
			self.comment_stop_pos = -1
			if self.next_char1 == '':
				return

def remove_default(args):
	# remove from functions arguments
	args = args[1:-1]
	parsed = []
	s = 0
	i = 0
	while i<len(args):
		if args[i] == "'":
			i += 1
			while True:
				if i+1<len(args) and args[i] == "'" and args[i+1] == "'":
					i += 2
					continue
				if args[i] == "'":
					i += 1
					break
				i += 1
			continue
		if args[i] == "(":
			i = skip_exp(args, i+1)
			continue
		if args[i] == ",":
			parsed.append(args[s:i].split(' DEFAULT')[0])
			i += 1
			s = i
			continue
		if args[i] == " " and s == i:
			s = i + 1
		i += 1
	if i > s:
		parsed.append(args[s:i].split(' DEFAULT')[0])

	return parsed

def skip_exp(args, i):
	while i<len(args):
		if args[i] == "'":
			i += 1
			while True:
				if i+1<len(args) and args[i] == "'" and args[i+1] == "'":
					i += 2
					continue
				if args[i] == "'":
					i += 1
					break
				i += 1
			continue
		if args[i] == "(":
			i = skip_exp(args, i+1)
			continue
		if args[i] == ")":
			return i + 1
		i += 1

def parse_test(dump_stream):
	project = Project()
	tokens = Tokens(dump_stream).__iter__()
	set_schema = None

	for token in tokens:
		print('v'*80)
		print(token)
		print('^'*80)

def parse(dump_stream):
	project = Project()
	tokens = Tokens(dump_stream).__iter__()
	set_schema = None

	project.schemas['public'] = Schema(None, 'public')

	for comment, command in tokens:
		try:
			if command == '':
				continue

			# CONFIGURATION

			x = re.match(r"SET (?P<configuration_parameter>\S+) = '?(?P<value>[^']*)'?;$", command)
			if x:
				if x.group('configuration_parameter') == 'search_path':
					set_schema = x.group('value').split(",")[0]
				continue

			x = re.match(r"SELECT pg_catalog.set_config\('(?P<configuration_parameter>\S+)',\s*'(?P<value>[^']*)',\s*.*\);", command)
			if x:
				if x.group('configuration_parameter') == 'search_path':
					set_schema = x.group('value').split(",")[0]
				continue

			# SCHEMA

			x = re.match(r'CREATE SCHEMA (?P<schema_name>\S+);$', command)
			if x:
				project.schemas[x.group('schema_name')] = Schema(command, x.group('schema_name'))
				continue

			x = re.match(r'ALTER SCHEMA (?P<name>\S+) OWNER TO (?P<new_owner>\S+);$', command)
			if x:
				project.schemas[x.group('name')].owner = x.group('new_owner')
				continue

			# EXTENSION

			x = re.match(r'CREATE EXTENSION IF NOT EXISTS (?P<extension_name>\S+) WITH SCHEMA (?P<schema_name>\S+);$', command)
			if x:
				project.extentions[x.group('extension_name')] = Extention(command, x.group('extension_name'), x.group('schema_name'))
				continue

			# TYPE ENUM

			x = re.match(r"CREATE TYPE (?P<name>\S+) AS ENUM \(", command)
			if x:
				labels = []
				for line in command.split('\n'):
					y = re.match(r"CREATE TYPE (?P<name>\S+) AS ENUM \(", line)
					if y:
						continue
					y = re.match(r"\);", line)
					if y:
						continue
					y = re.match(r"\s*$", line)
					if y:
						continue
					y = re.match(r"\s*(?P<label>[^,]+),?$", line)
					if y:
						labels.append(y.group('label'))
						continue
					logging.error('ERROR: ' + command)
				project.types[schema(set_schema, x.group('name'))] = Enum(command, schema(set_schema, x.group('name')), labels)
				continue

			# TYPE

			x = re.match(r"CREATE TYPE (?P<name>\S+) AS \(", command)
			if x:
				attributes = []
				for line in command.split('\n'):
					y = re.match(r"CREATE TYPE (?P<name>\S+) AS \(", line)
					if y:
						continue
					y = re.match(r"\);", line)
					if y:
						continue
					y = re.match(r"\s*$", line)
					if y:
						continue
					y = re.match(r"\s*(?P<attribute>.*[^,]),?$", line)
					if y:
						attributes.append(y.group('attribute'))
						continue
					logging.error('ERROR: ' + command)
				project.types[schema(set_schema, x.group('name'))] = Type(command, schema(set_schema, x.group('name')), attributes)
				continue

			# TYPE RANGE

			x = re.match(r"CREATE TYPE (?P<name>\S+) AS RANGE \(", command)
			if x:
				project.types[schema(set_schema, x.group('name'))] = Range(command, schema(set_schema, x.group('name')))
				continue

			x = re.match(r"ALTER TYPE (?P<name>\S+) OWNER TO (?P<new_owner>\S+);$", command)
			if x:
				project.types[schema(set_schema, x.group('name'))].owner = x.group('new_owner')
				continue

			# FUNCTION

			x = re.match(r"CREATE( OR REPLACE)? FUNCTION\s+(?P<name>[^\(]+)(?P<args>\(.*\))\s+RETURNS(\s+SETOF)?\s+(?P<returns>\S.*\S)\s+", command)
			if x:
				args = remove_default(x.group('args'))
				project.functions[schema(set_schema, x.group('name')) + str(args)] = Function(command, schema(set_schema, x.group('name')), x.group('args'), args)
				continue

			# ALTER FUNCTION lbadmin.permission_unpack(text[]) OWNER TO lbadmin;
			x = re.match(r'ALTER FUNCTION (?P<name>[^()]+)(?P<args>\(.*\)) OWNER TO (?P<new_owner>\S+);$', command)
			if x:
				args = remove_default(x.group('args'))
				project.functions[schema(set_schema, x.group('name')) + str(args)].owner = x.group('new_owner')
				continue

			# TABLE

			x = re.match(r"CREATE( UNLOGGED)?( FOREIGN)? TABLE (?P<name>\S+) ?\(", command)
			if x:
				columns = []
				for line in command.split('\n'):
					y = re.match(r"CREATE( UNLOGGED)?( FOREIGN)? TABLE (?P<name>\S+) ?\(", line)
					if y:
						continue
					y = re.match(r"\);", line)
					if y:
						continue
					y = re.match(r"\s*$", line)
					if y:
						continue
					y = re.match(r"\s*(?P<column>.*[^,]),?$", line)
					if y:
						columns.append(y.group('column'))
						continue
					logging.error('ERROR: ' + command)
				project.tables[schema(set_schema, x.group('name'))] = Table(command, schema(set_schema, x.group('name')), columns)
				continue

			x = re.match(r"ALTER( FOREIGN)? TABLE (?P<name>\S+) OWNER TO (?P<new_owner>\S+);$", command)
			if x:
				if schema(set_schema, x.group('name')) in project.tables:
					project.tables[schema(set_schema, x.group('name'))].owner = x.group('new_owner')
					continue
				elif schema(set_schema, x.group('name')) in project.sequences:
					project.sequences[schema(set_schema, x.group('name'))].owner = x.group('new_owner')
					continue
				elif schema(set_schema, x.group('name')) in project.views:
					project.views[schema(set_schema, x.group('name'))].owner = x.group('new_owner')
					continue
				else:
					logging.warning("Parser warning, element '%s' not found, command: %s" % (schema(set_schema, x.group('name')), command))
					continue

			x = re.match(r"ALTER TABLE( ONLY)? (?P<name>\S+) ALTER (?P<default>COLUMN (?P<column>\S+) SET DEFAULT .*);$", command)
			if x:
				project.tables[schema(set_schema, x.group('name'))].defaults.append(x.group('default'))
				continue

			x = re.match(r"ALTER TABLE( ONLY)? (?P<name>\S+)\s*ADD (?P<constraint>CONSTRAINT.*);", command, re.M)
			if x:
				project.tables[schema(set_schema, x.group('name'))].constraints.append(x.group('constraint'))
				continue

			x = re.match(r"ALTER TABLE( ONLY)? (?P<name>\S+)\s*ALTER (?P<conf>COLUMN.*);", command, re.M)
			if x:
				project.tables[schema(set_schema, x.group('name'))].columns_conf.append(x.group('conf'))
				continue

			x = re.match(r"CREATE (?P<index>(UNIQUE)?\s?INDEX (?P<name>\S+)?\s?ON (?P<table_name>\S+).*);$", command)
			if x:
				table_name = schema(set_schema, x.group('table_name'))
				index = x.group('index')
				if table_name not in index:
					index = re.sub(r"ON\s+" + x.group('table_name'), "ON " + table_name, index, 1)
				project.tables[table_name].indexes.append(index)
				continue

			x = re.match(r"CREATE (?P<trigger>TRIGGER (?P<name>\S+) .* ON (?P<table_name>\S+) .*);$", command)
			if x:
				project.tables[schema(set_schema, x.group('table_name'))].triggers.append(x.group('trigger'))
				continue

			x = re.match(r"ALTER TABLE (?P<table_name>\S+) (?P<trigger>DISABLE TRIGGER \S+);$", command)
			if x:
				project.tables[schema(set_schema, x.group('table_name'))].triggers.append(x.group('trigger'))
				continue

#			x = re.match(r"ALTER TABLE ONLY \S+ FORCE ROW LEVEL SECURITY;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER TABLE \S+ CLUSTER ON \S+;$", command)
#			if x:
#				# TODO
#				continue

			# SEQUENCE

			x = re.match(r"CREATE SEQUENCE (?P<name>\S+)", command)
			if x:
				project.sequences[schema(set_schema, x.group('name'))] = Sequence(command, schema(set_schema, x.group('name')))
				continue

			x = re.match(r"ALTER SEQUENCE (?P<name>\S+) OWNER TO (?P<new_owner>\S+);$", command)
			if x:
				project.sequences[schema(set_schema, x.group('name'))].owner = x.group('new_owner')
				continue

			x = re.match(r"ALTER SEQUENCE (?P<name>\S+) OWNED BY (?P<table_column>\S+);$", command)
			if x:
				table_column = x.group('table_column')
				y = re.match(r"\w+\.\w+\.", table_column)
				if not y:
					table_column = "%s.%s" % (set_schema, x.group('table_column'))
				project.sequences[schema(set_schema, x.group('name'))].owned_by = table_column
				continue

			# VIEW

			x = re.match(r"CREATE( MATERIALIZED)?( OR REPLACE)? VIEW (?P<name>\S+) AS", command)
			if x:
				project.views[schema(set_schema, x.group('name'))] = View(command, schema(set_schema, x.group('name')))
				continue

			# PERMISSIONS

			x = re.match(r"REVOKE .* ON SCHEMA (?P<schema_name>\S+) FROM (?P<role>\S+);$", command)
			if x:
				project.schemas[x.group('schema_name')].revoke.append(command.strip())
				continue

			x = re.match(r"GRANT .* ON SCHEMA (?P<schema_name>\S+) TO (?P<role>\S+);$", command)
			if x:
				project.schemas[x.group('schema_name')].grant.append(command.strip())
				continue

			x = re.match(r"REVOKE .* ON TABLE (?P<table_name>\S+) FROM (?P<role>\S+);$", command)
			if x:
				if schema(set_schema, x.group('table_name')) in project.tables:
					project.tables[schema(set_schema, x.group('table_name'))].revoke.append(command.strip())
				else:
					project.views[schema(set_schema, x.group('table_name'))].revoke.append(command.strip())
				continue

			x = re.match(r"GRANT .* ON TABLE (?P<table_name>\S+) TO (?P<role>\S+);$", command)
			if x:
				if schema(set_schema, x.group('table_name')) in project.tables:
					project.tables[schema(set_schema, x.group('table_name'))].grant.append(command.strip())
				else:
					project.views[schema(set_schema, x.group('table_name'))].grant.append(command.strip())
				continue

			x = re.match(r"REVOKE .* ON SEQUENCE (?P<table_name>\S+) FROM (?P<role>\S+);$", command)
			if x:
				project.sequences[schema(set_schema, x.group('table_name'))].revoke.append(command.strip())
				continue

			x = re.match(r"GRANT .* ON SEQUENCE (?P<table_name>\S+) TO (?P<role>\S+);$", command)
			if x:
				project.sequences[schema(set_schema, x.group('table_name'))].grant.append(command.strip())
				continue

			x = re.match(r"REVOKE .* ON FUNCTION (?P<name>[^()]+)(?P<args>\(.*\)) FROM (?P<role>\S+);$", command)
			if x:
				args = remove_default(x.group('args'))
				project.functions[schema(set_schema, x.group('name')) + str(args)].revoke.append(command.strip())
				continue

			x = re.match(r"GRANT .* ON FUNCTION (?P<name>[^()]+)(?P<args>\(.*\)) TO (?P<role>\S+);$", command)
			if x:
				args = remove_default(x.group('args'))
				project.functions[schema(set_schema, x.group('name')) + str(args)].grant.append(command.strip())
				continue

			x = re.match(r"ALTER .* PRIVILEGES FOR ROLE \S+ IN SCHEMA (?P<schema_name>\S+) .*;$", command)
			if x:
				project.schemas[x.group('schema_name')].grant.append(command.strip())
				continue

#			x = re.match(r"GRANT \S+ TO \S+ GRANTED BY \S+;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"REVOKE .* ON DATABASE (?P<table_name>\S+) FROM (?P<role>\S+);$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"GRANT .* ON DATABASE (?P<table_name>\S+) TO (?P<role>\S+);$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"GRANT .* ON FOREIGN SERVER \S+ TO \S+;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"GRANT .* ON FOREIGN DATA WRAPPER \S+ TO \S+;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"REVOKE .* ON TYPE \S+ FROM \S+;$", command)
#			if x:
#				# TODO
#				continue

			# ROLE

#			x = re.match(r"CREATE ROLE (?P<name>\S+);$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER ROLE (?P<name>\S+) .*;$", command)
#			if x:
#				# TODO
#				continue

			# DATABASE

#			x = re.match(r"CREATE DATABASE \S+ WITH TEMPLATE = \S+ OWNER = \S+.*;$", command)
#			if x:
#				# TODO
#				continue

			# COMMAND

#			x = re.match(r"\\connect \S+$", command)
#			if x:
#				# TODO
#				continue

			# COMMENT

#			x = re.match(r"COMMENT ON .*", command)
#			if x:
#				# TODO
#				continue

			x = re.match(r"COMMENT ON EXTENSION (?P<name>\S+) IS '(?P<comment>.*)';", command)
			if x:
				project.extentions[x.group('name')].comment = command
				continue

			x = re.match(r"COMMENT ON TABLE (?P<table_name>\S+) IS '(?P<comment>.*)'", command)
			if x:
				project.tables[schema(set_schema, x.group('table_name'))].comment = command
				continue

			x = re.match(r"COMMENT ON COLUMN (?P<table_name>\S+)\.(?P<column_name>\S+) IS '(?P<comment>.*)'", command)
			if x:
				project.tables[schema(set_schema, x.group('table_name'))].comment = command
				continue

			# LANGUAGE

#			x = re.match(r"CREATE OR REPLACE PROCEDURAL LANGUAGE (?P<name>\S+);$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER PROCEDURAL LANGUAGE \S+ OWNER TO \S+;$", command)
#			if x:
#				# TODO
#				continue

			# AGGREGATE

#			x = re.match(r"ALTER AGGREGATE \S+\(.*\) OWNER TO \S+;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"CREATE AGGREGATE \S+\(.*\)", command)
#			if x:
#				# TODO
#				continue

			# FOREIGN DATA WRAPPER

#			x = re.match(r"CREATE FOREIGN DATA WRAPPER \S+( HANDLER \S+)? VALIDATOR \S+;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER FOREIGN DATA WRAPPER \S+ OWNER TO \S+;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"CREATE SERVER \S+ FOREIGN DATA WRAPPER \S+ OPTIONS", command)
#			if x:
#				# TODO
#				continue

			# SERVER

#			x = re.match(r"CREATE SERVER \S+ FOREIGN DATA WRAPPER \S+;$", command)
#			if x:
#				# TODO
#				continue


#			x = re.match(r"ALTER SERVER \S+ OWNER TO \S+;$", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"CREATE USER MAPPING FOR \S+ SERVER \S+ OPTIONS", command)
#			if x:
#				# TODO
#				continue

			# OPERATOR

			x = re.match(r"CREATE OPERATOR (?P<name>\S+)( \(.*\))? \(", command)
			if x:
				a = re.search(r"LEFTARG\s*=\s*(?P<name>[^\s,]+)", command, re.DOTALL)
				if a:
					leftarg = a.group('name')
				else:
					leftarg = ""
				a = re.search(r"RIGHTARG\s*=\s*(?P<name>[^\s,]+)", command, re.DOTALL)
				if a:
					rightarg = a.group('name')
				else:
					rightarg = ""

				name = "%s,%s,%s" % (schema(set_schema, x.group('name')), leftarg, rightarg)

				project.operators[name] = Operator(command, schema(set_schema, x.group('name')), leftarg, rightarg)
				continue

			x = re.match(r"ALTER OPERATOR (?P<name>\S+) \((?P<leftarg>\S+), (?P<rightarg>\S+)\) OWNER TO (?P<new_owner>\S+);$", command)
			if x:
				name = "%s,%s,%s" % (schema(set_schema, x.group('name')), x.group('leftarg'), x.group('rightarg'))
				project.operators[name].owner = x.group('new_owner')
				continue

			# CAST

#			x = re.match(r"CREATE CAST \(.*\) WITH FUNCTION .* AS IMPLICIT;$", command)
#			if x:
#				# TODO
#				continue

			# RULE

			x = re.match(r"CREATE RULE \S+ AS\s+ON \S+ TO (?P<table_name>\S+)\s+DO.*", command, re.DOTALL)
			if x:
				if schema(set_schema, x.group('table_name')) in project.tables:
					project.tables[schema(set_schema, x.group('table_name'))].rule.append(command.strip())
				else:
					project.views[schema(set_schema, x.group('table_name'))].rule.append(command.strip())
				continue

			# EVENT TRIGGER

#			x = re.match(r"CREATE EVENT TRIGGER \S+ ON \S+", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER EVENT TRIGGER \S+ OWNER TO \S+;", command)
#			if x:
#				# TODO
#				continue

			# TEXT SEARCH

#			x = re.match(r"CREATE TEXT SEARCH DICTIONARY \S+ \(", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER TEXT SEARCH DICTIONARY \S+ OWNER TO \S+;", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"CREATE TEXT SEARCH CONFIGURATION \S+ \(", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER TEXT SEARCH CONFIGURATION \S+", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"CREATE TEXT SEARCH TEMPLATE \S+ \(", command)
#			if x:
#				# TODO
#				continue


			# OPERATOR

#			x = re.match(r"CREATE OPERATOR CLASS \S+", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER OPERATOR CLASS \S+ USING \S+ OWNER TO \S+;", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"CREATE OPERATOR FAMILY \S+ USING \S+;", command)
#			if x:
#				# TODO
#				continue

#			x = re.match(r"ALTER OPERATOR FAMILY \S+ USING btree OWNER TO \S+;", command)
#			if x:
#				# TODO
#				continue

		# ######################################

			project.others.append(Other(command))

		except KeyError:
			logging.error("Parser warning, KeyError on command: %s" % (command, ))
			continue

		except:
			logging.error("Error on command: %s" % (command, ))
			raise

	return project




