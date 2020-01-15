# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import re
import sys

class Address:
	def __init__(self, addr):
		self.addr = addr
		self.ssh = None
		self.ssh_port = None
		self.pg = None
		if '//' in addr:
			ssh_str, self.pg = addr.split("//",1)

			if ssh_str:
				x = re.match(r"^((?P<user>\w+)(:(?P<password>\w+))?@)?(?P<host>\w+)(:(?P<port>\d+))?", ssh_str)

				if x:
					if x.group("password"):
						logging.error("Error: ssh connection does not support 'password' option")
						sys.exit(1)
					if x.group("user"):
						self.ssh = x.group("user") + "@" + x.group("host")
					else:
						self.ssh = x.group("host")
					self.ssh_port = x.group("port")
				else:
					logging.error("Error: ssh connection cannot be parsed: %s" % (ssh_str))
					sys.exit(1)
		else:
			self.pg = addr

	def get_pg(self, dbname=None):
		if dbname:
			return "postgresql://" + self.pg.split("/",1)[0] + "/" + dbname
		else:
			return "postgresql://" + self.pg

	def to_str(self, dbname=None):
		if dbname:
			pg = self.pg.split("/",1)[0] + "/" + dbname
		else:
			pg = self.pg
		if self.ssh:
			return self.ssh+"//"+pg
		return pg

	def parse(self, dbname=None):
		uri = self.get_pg(dbname)
		x = re.match(r"postgresql://((?P<user>[^:@/?&]+)?(:(?P<password>[^:@/?&]+))?@)?(?P<host>[^:@/?&]+)?(:(?P<port>[^:@/?&]+)?)?(/(?P<dbname>[^:@/?&]+))?(\?(?P<param>.*))?", uri)
		return x.groupdict()

	def get_user(self, dbname=None):
		return self.parse(dbname)["user"]

	def get_password(self, dbname=None):
		return self.parse(dbname)["password"]

	def get_host(self, dbname=None):
		return self.parse(dbname)["host"]

	def get_port(self, dbname=None):
		return self.parse(dbname)["port"]

	def get_dbname(self, dbname=None):
		return self.parse(dbname)["dbname"]

	def get_param(self, dbname=None):
		return self.parse(dbname)["param"]

	def cache_file(self, cache_type):
		if cache_type:
			return "/tmp/pgdist-cache-%s-%s" % (self.addr.replace("/", "-"), cache_type)
		return "/tmp/pgdist-cache-%s" % (self.addr.replace("/", "-"),)
