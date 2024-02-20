# -*- coding: utf-8 -*-

import re

class InvalidVersionFormatError(Exception):
	pass

class Version:
	version_re = re.compile(r'(\.)', re.VERBOSE)

	def __init__ (self, vstring):
		self.parse(vstring)


	def parse(self, vstring):
		self.vstring = vstring
		ver_match = re.match(r'^((?:0.|[1-9]\d*\.){1}(?:0.|[1-9]\d*\.){0,}(?:0|[1-9]\d*))(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[0-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$',vstring)
		if ver_match is None:
			raise InvalidVersionFormatError(f'Not valid semantic versioning format: {vstring}')
		
		core, pre_rel, build = ver_match.groups()

		core_version = [x for x in self.version_re.split(core) if x and x != '.']
		
		if pre_rel is not None:
			pre_version = [x for x in self.version_re.split(pre_rel) if x and x != '.']
		else: 
			pre_version = []

		for v in [core_version,pre_version]:
			for i, obj in enumerate(v):
				try:
					v[i] = int(obj)
				except ValueError:
					pass

		self.core_version = core_version
		self.pre_version = pre_version

	def __str__ (self):
		return self.vstring

	def cmp (self, other):
		if isinstance(other, str):
			other = Version(other)
		#compare core part of version
		for i, c1 in enumerate(self.core_version):
			if i >= len(other.core_version):
					return 1
			c2 = other.core_version[i]
			# id both is int, str
			if type(c1) == type(c2):
				if c1 == c2:
					continue
				if c1 < c2:
					return -1
				if c1 > c2:
					return 1
		if len(other.core_version) > len(self.core_version):
			return -1

		#compare pre-release part of version
		if len(self.pre_version) > 0 and len(other.pre_version) > 0:
			for i, p1 in enumerate(self.pre_version):
				if i >= len(other.pre_version):
					return 1
				p2 = other.pre_version[i]
				if type(p1) == type(p2):
					if p1 == p2:
						continue
					if p1 < p2:
						return -1
					if p1 > p2:
						return 1
				elif type(p1) == int:
					return -1
				else:
					return 1

			if len(other.pre_version) > len(self.pre_version):
				return -1
			else:
				return 0

		if len(self.pre_version) > len(other.pre_version) :
			return -1
		if len(other.pre_version) > 0:
			return 1
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


def tests():
	# test of normal version
	x = Version('1.2.3') == Version('1.2.3')
	print("1. == True", x)
	assert x == True

	x = Version('1.2.3') > Version('1.2.3')
	print("2. > False", x)
	assert x == False

	x = Version('1.2.3') < Version('1.2.3')
	print("3. < False", x)
	assert x == False

	x = Version('1.2.3') == Version('1.2')
	print("4. == False", x)
	assert x == False

	x = Version('1.2.3') > Version('1.2')
	print("5. > True", x)
	assert x == True

	x = Version('1.2.3') < Version('1.2')
	print("6. < False", x)
	assert x == False

	x = Version('1.2') == Version('1.2.3')
	print("7. == False", x)
	assert x == False

	x = Version('1.2') > Version('1.2.3')
	print("8. > False", x)
	assert x == False

	x = Version('1.2') < Version('1.2.3')
	print("9. < True", x)
	assert x == True

	x = Version('1.1') < Version('1.2.3')
	print("9.1 < True", x)
	assert x == True

	x = Version('1.1.1.1') < Version('1.2.3')
	print("9.2 < True", x)
	assert x == True

	x = Version('1.3.5.8') > Version('1.2')
	print("9.3 < True", x)
	assert x == True

	#tests of prelease verisons
	x = Version('1.2-beta') == Version('1.2-beta')
	print("10. == True", x)
	assert x == True

	x = Version('1.2-beta') > Version('1.2-beta')
	print("11. > False", x)
	assert x == False

	x = Version('1.2-beta') < Version('1.2-beta')
	print("12. < False", x)
	assert x == False


	x = Version('1.2-beta') == Version('1.2')
	print("13. == False", x)
	assert x == False

	x = Version('1.2-beta') > Version('1.2')
	print("14. > False", x)
	assert x == False

	x = Version('1.2-beta') < Version('1.2')
	print("15. < True", x)
	assert x == True

	x = Version('1.2-beta.1') == Version('1.2.1')
	print("16. == False", x)
	assert x == False

	x = Version('1.2-beta.1') > Version('1.2.1')
	print("17. > False", x)
	assert x == False

	x = Version('1.2-beta.1') < Version('1.2.1')
	print("18. < True", x)
	assert x == True


	x = Version('1.2-beta.1') == Version('1.2-delta.1')
	print("19. == False", x)
	assert x == False

	x = Version('1.2-beta.1') > Version('1.2-delta.1')
	print("20. > False", x)
	assert x == False

	x = Version('1.2-beta.1') < Version('1.2-delta.1')
	print("21. < True", x)
	assert x == True

	x = Version('1.2-beta.1') == Version('1.2-alfa.1')
	print("22. == False", x)
	assert x == False

	x = Version('1.2-beta.1') > Version('1.2-alfa.1')
	print("23. > True", x)

	x = Version('1.2-beta.1') < Version('1.2-alfa.1')
	print("24. < False", x)
	assert x == False

	x = Version('1.2-beta1') == Version('1.2-beta2')
	print("25. == False", x)
	assert x == False

	x = Version('1.2-beta1') > Version('1.2-beta2')
	print("26. > False", x)
	assert x == False

	x = Version('1.2-beta1') < Version('1.2-beta2')
	print("27. < True", x)
	assert x == True

	x = Version('1.2-beta1.0.1') == Version('1.2-beta2')
	print("28. == False", x)
	assert x == False

	x = Version('1.2-beta1.0.1') > Version('1.2-beta2')
	print("29. > False", x)
	assert x == False

	x = Version('1.2-beta1.0.1') < Version('1.2-beta2')
	print("30. < True", x)
	assert x == True

	x = Version('1.2-1.0.1') == Version('1.2-2')
	print("31. == False", x)
	assert x == False

	x = Version('1.2-1.0.1') > Version('1.2-2')
	print("32. > False", x)
	assert x == False

	x = Version('1.2-1.0.1') < Version('1.2-2')
	print("33. < True", x)
	assert x == True

	x = Version('1.2.1-1') == Version('1.2.1-alfa')
	print("34. == False", x)
	assert x == False

	x = Version('1.2.1-1') > Version('1.2.1-alfa')
	print("35. > False", x)
	assert x == False

	x = Version('1.2.1-1') < Version('1.2.1-alfa')
	print("36. < False", x)
	assert x == True

	x = Version('1.0.0-alpha') < Version('1.0.0-alpha.1')
	print("37. < True", x)
	assert x == True

	x = Version('1.0.0-alpha.1') < Version('1.0.0-alpha.beta')
	print("38. < True", x)
	assert x == True

	x = Version('1.2.3----RC-SNAPSHOT.12.9.1--.12') < Version('1.2.3')
	print("39. < True", x)
	assert x == True

	x = Version('1.2.3----RC-SNAPSHOT.12.9.1--.12') > Version('1.2.3----RC-SNAPSHOT')
	print("40. < True", x)
	assert x == True

	x = Version('10.2.3-DEV-SNAPSHOT') == Version('10.2.3-DEV-SNAPSHOT')
	print("40. == True", x)
	assert x == True

	x = Version('10.2.3-DEV-SNAPSHOT-aa') < Version('10.2.3-DEV-SNAPSHOT-last')
	print("41. < True", x)
	assert x == True

if __name__ == '__main__':
	tests()
	try:
		tests()
		print('\033[1;32m Tests OK!\n \033[0m')
	except Exception as e:
		print('\033[1;31;40m Tests FAILED !!!! \033[0m')