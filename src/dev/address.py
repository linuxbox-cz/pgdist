# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class Address:
	def __init__(self, addr):
		self.addr = addr
		self.ssh = None
		self.pg = None
		if '//' in addr:
			self.ssh, self.pg = addr.split("//",1)
		else:
			self.pg = addr

	def get_pg(self, dbname=None):
		if dbname:
			return "postgresql://" + self.pg.split("/",1)[0] + "/" + dbname
		else:
			return "postgresql://" + self.pg
