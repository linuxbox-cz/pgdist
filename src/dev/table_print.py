# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import io


class Row:
	def __init__(self, row, init, columns_size):
		self.init = init
		self.rows = 1
		row2 = []
		for i, v in enumerate(row):
			if v is None:
				row2.append([None])
				columns_size[i] = max(columns_size[i], 4)
			elif type(v) not in (str, unicode):
				row2.append([v])
				columns_size[i] = max(columns_size[i], len(str(v)))
			elif v == "":
				row2.append([""])
			else:
				if type(v) != unicode:
					try:
						v = unicode(v, "utf-8")
					except UnicodeDecodeError:
						v = "UnicodeDecodeError"
				r = v.splitlines()
				row2.append(r)
				self.rows = max(self.rows, len(r))
				for rv in r:
					columns_size[i] = max(columns_size[i], len(rv))
		self.row = row2

	def format(self, columns_size, init_len, buf):
		for k in xrange(self.rows):
			buf.write(("%%-%ds" % (init_len,)) % (self.init,))
			buf.write(" ")
			for i, cell in enumerate(self.row):
				if i > 0: buf.write(" | ")
				if k < len(cell):
					v = cell[k]
					if v is None:
						buf.write(("%%-%ds" % (columns_size[i],)) % ("NULL",))
					elif type(v) in (int, float):
						buf.write(("%%%ds" % (columns_size[i],)) % (v,))
					else:
						buf.write(("%%-%ds" % (columns_size[i],)) % (v,))
				else:
					buf.write(" " * columns_size[i])
			buf.write(" \n")

	def __cmp__(self, other):
		return cmp(self.row, other.row)

class TablePrint:
	def __init__(self, headers):
		self.columns_size = [0] * len(headers)
		self.headers = Row(headers, "", self.columns_size)
		self.data = []
		self.init_len = 0

	def add(self, row, init=""):
		self.data.append(Row(row, init, self.columns_size))
		self.init_len = max(self.init_len, len(init))

	def sort(self):
		self.data.sort()

	def format(self):
		buf = io.StringIO()
		self.headers.format(self.columns_size, self.init_len, buf)
		buf.write(" " * self.init_len)
		buf.write("-")
		for i in xrange(len(self.columns_size)):
			if i > 0: buf.write("-+-")
			buf.write("-" * self.columns_size[i])
		buf.write("-\n")
		for row in self.data:
			row.format(self.columns_size, self.init_len, buf)
		return buf.getvalue()

def table_print(data, headers, formats=None):
	tp = TablePrint(headers)
	for row in data:
		tp.add(row)
	print(tp.format())

def table_print_pg(cursor):
	table_print(cursor.fetchall(), headers=map(lambda x: x.name, cursor.description))
