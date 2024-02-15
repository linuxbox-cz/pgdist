# -*- coding: utf-8 -*-

import re

class Version:
	version_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)

	def __init__ (self, vstring):
		self.parse(vstring)

	def parse(self, vstring):
		self.vstring = vstring
		v_array = [x for x in self.version_re.split(vstring) if x and x != '.']
		for i, obj in enumerate(v_array):
			try:
				v_array[i] = int(obj)
			except ValueError:
				pass
		self.version = v_array

	def __str__ (self):
		return self.vstring

	def cmp (self, other):
		if isinstance(other, str):
			other = Version(other)

		for i, c1 in enumerate(self.version):
			if i >= len(other.version):
				if type(c1) == str:
					return -1
				else:
					return 1
			c2 = other.version[i]
			# id both is int, str
			if type(c1) == type(c2):
				if c1 == c2:
					continue
				if c1 < c2:
					return -1
				if c1 > c2:
					return 1
			if type(c1) == int:
				return 1
			return -1
		if len(self.version) < len(other.version):
			if type(other.version[len(self.version)]) == str:
				return 1
			else:
				return -1
		else:
			return 0

	def __eq__(self, other):
		return self.cmp(other) == 0

	def __lt__(self, other):
		return self.cmp(other) < 0

	def __le__(self, other):
		return self.cmp(other) <= 0

	def __gt__(self, other):
		return self.cmp(other) > 0

	def __ge__(self, other):
		return self.cmp(other) >= 0


x = Version('1.2.3') == Version('1.2.3')
print("== True", x)

x = Version('1.2.3') > Version('1.2.3')
print("> False", x)

x = Version('1.2.3') < Version('1.2.3')
print("< False", x)



x = Version('1.2.3') == Version('1.2')
print("== False", x)

x = Version('1.2.3') > Version('1.2')
print("> True", x)

x = Version('1.2.3') < Version('1.2')
print("< False", x)



x = Version('1.2') == Version('1.2.3')
print("== False", x)

x = Version('1.2') > Version('1.2.3')
print("> False", x)

x = Version('1.2') < Version('1.2.3')
print("< True", x)


x = Version('1.2beta') == Version('1.2beta')
print("== True", x)

x = Version('1.2beta') > Version('1.2beta')
print("> False", x)

x = Version('1.2beta') < Version('1.2beta')
print("< False", x)


x = Version('1.2beta') == Version('1.2')
print("== False", x)

x = Version('1.2beta') > Version('1.2')
print("> False", x)

x = Version('1.2beta') < Version('1.2')
print("< True", x)


x = Version('1.2beta.1') == Version('1.2.1')
print("== False", x)

x = Version('1.2beta.1') > Version('1.2.1')
print("> False", x)

x = Version('1.2beta.1') < Version('1.2.1')
print("< True", x)






