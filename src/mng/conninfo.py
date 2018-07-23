class ConnInfo:
	def __init__(self, args):
		self.dbname = args.dbname
		self.host = args.host
		self.port = args.port
		self.user = args.user

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

		return d
