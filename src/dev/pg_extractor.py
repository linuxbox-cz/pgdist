
import sys
import shutil
import logging
import tempfile
import subprocess

import color

class PG_extractor:
	def __init__(self, basedir):
		self.basedir = basedir
		self.db1 = None
		self.db2 = None
		if self.basedir:
			self.basedir_tmp = None
		else:
			self.basedir_tmp = tempfile.mkdtemp(prefix="pgdist_")

	def get_dumpdir(self):
		if self.basedir:
			return self.basedir
		else:
			return self.basedir_tmp

	def add_db(self, db):
		if not self.db1:
			self.db1 = db
		elif not self.db2:
			self.db2 = db

	def print_dump_info(self):
		if self.basedir:
			print("pg_extractor dumped project to: %s" % (pg_extractor.basedir))

	def print_diff(self, swap=False):
		self.print_dump_info()
		args = ["diff", "-r"]
		if color.color_out:
			args.append("--color=always")
		else:
			args.append("--color=never")
		if not swap:
			args.append(self.db1)
			args.append(self.db2)
		else:
			args.append(self.db2)
			args.append(self.db1)
		logging.debug(str(args))
		process = subprocess.Popen(args, cwd=self.get_dumpdir(), stdout=sys.stdout)
		retcode = process.wait()

	def clean(self):
		if self.basedir_tmp and "pgdist" in self.basedir_tmp:
			shutil.rmtree(self.basedir_tmp)
