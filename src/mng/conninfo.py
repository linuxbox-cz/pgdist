# -*- coding: utf-8 -*-


class ConnInfo:
	def __init__(self, args):
		self.dbname = args.database
		self.host = args.host
		self.port = args.port
		self.user = args.user
		self.password = args.password

	def dsn(self, dbname=None):
		d = ""
		if dbname:
			d += "dbname=%s " % (dbname,)
		elif self.dbname:
			d += "dbname=%s " % (self.dbname,)

		if self.host:
			d += "host=%s " % (self.host,)

		if self.port:
			d += "port=%s " % (self.port,)

		if self.user:
			d += "user=%s " % (self.user,)

		if self.password:
			d += "password=%s " % (self.password)

		return d
