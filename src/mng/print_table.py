# -*- coding: utf-8 -*-

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
			elif type(v) != str:
				row2.append([v])
				columns_size[i] = max(columns_size[i], len(str(v)))
			elif v == "":
				row2.append([""])
			else:
				r = v.splitlines()
				row2.append(r)
				self.rows = max(self.rows, len(r))
				for rv in r:
					columns_size[i] = max(columns_size[i], len(rv))
		self.row = row2

	def format(self, columns_size, init_len, buf, empty_value=""):
		for k in range(self.rows):
			buf.write(("%%-%ds" % (init_len,)) % (self.init,))
			buf.write(" ")
			for i, cell in enumerate(self.row):
				if i > 0: buf.write("   ")
				if k < len(cell):
					v = cell[k]
					if v is None:
						buf.write(("%%-%ds" % (columns_size[i],)) % (empty_value,))
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

	def format(self, empty_value=""):
		buf = io.StringIO()
		
		buf.write(" " * self.init_len)
		buf.write("=")
		for i in range(len(self.columns_size)):
			if i > 0: buf.write("===")
			buf.write("=" * self.columns_size[i])
		buf.write("=\n")
		self.headers.format(self.columns_size, self.init_len, buf)
		buf.write(" " * self.init_len)

		for row in self.data:
			row.format(self.columns_size, self.init_len, buf, empty_value)
		buf.write(" " * self.init_len)
		buf.write("=")
		for i in range(len(self.columns_size)):
			if i > 0: buf.write("===")
			buf.write("=" * self.columns_size[i])
		buf.write("=")
		return buf.getvalue()

def table_print(data, headers, formats=None, empty_value=""):
	tp = TablePrint(headers)
	for row in data:
		tp.add(row)
	print(tp.format(empty_value))
