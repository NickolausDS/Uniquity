import sqlite3
import schema
import time
import logging

import os
from data.config import DB_NAME, DB_DIR, MAIN_LOG_NAME


class Cursor(object):

	# #Use to make Cursor a singlton. We probably won't use this
	# #Because separate connections are needed for separate threads
	# _instance = None
	# def __new__(cls, *args, **kwargs):
	# 	if not cls._instance:
	# 		cls._instance = super(Cursor, cls).__new__(cls, *args, **kwargs)
	# 		cls.conn = sqlite3.connect("example.db")
	# 	return cls._instance
	
	#Last time the db was committed to
	lastCommit = -1
	tables = []
	
	
	def __init__(self):
		self.log = logging.getLogger('.'.join((MAIN_LOG_NAME, 'Main.Cursor')))
		
		try:
			if not os.path.exists(DB_DIR):
				os.mkdir(DB_DIR)
			self.conn = sqlite3.connect(DB_NAME)
		except Exception as e:
			#Raising an exception here will halt the program. It happens
			#when the user tries to run uniquity directly from a dmg where
			#they don't have write access (ie, the db can't be written to)
			#We'll do this until there is a workaround
			raise UniquityDBException(str(e))
		# except OSError as e:
		# 	self.log.error("DB: %s", str(e))	
		# 	self.log.info("Attempting to start database in memory...")
		# 	self.conn = sqlite3.connect(":memory:")
		# except sqlite3.OperationalError as soe:
		# 	self.log.error("DB: %s", str(soe))	
		# 	self.log.info("Attempting to start database in memory...")
		# 	self.conn = sqlite3.connect(":memory:")
		
		self.cursor = self.conn.cursor()		
		
	def __del__(self):
		try:
			self.conn.close()
		#Sometimes we get an attribute error if the conn wasn't inititalized
		except AttributeError:
			pass
		
	def close(self):
		self.__del__()
		
	def __getSQLType(self, theType):
		if theType == str:
			return "TEXT"
		elif theType == int:
			return "INTEGER"
	
	@staticmethod
	def registerTable(obj):
		Cursor.tables.append(obj)
			
	def setupTables(self):
		cursor = self.conn.cursor()
		for obj in Cursor.tables:
			tablename = getattr(obj, "DB_TABLE_NAME")
			query = "CREATE TABLE IF NOT EXISTS %s (dbid INTEGER PRIMARY KEY AUTOINCREMENT," % tablename
			columns = []
			for column in getattr(obj, "DB_SAVE_ATTRS"):
				columns.append("%s %s" % (column[0], self.__getSQLType(column[1]) ))
			query += ",".join(columns)
			query += ")"
				
			cursor.execute(query)
			self.conn.commit()
			Cursor.lastCommit = time.time()
			
	def save(self, obj):
		# try:
		saveAttrs = getattr(obj, "DB_SAVE_ATTRS", None)
		if not saveAttrs:
			raise ValueError("Unable to save '%s' to database, DB_SAVE_ATTRS not set." % obj)
		else:
			values = [value[0] for value in saveAttrs]
			data = [getattr(obj, objdata) for objdata in values]

			query = "INSERT INTO %s (%s) VALUES (%s)" % (obj.DB_TABLE_NAME, 
						",".join(values),
						",".join("?" * len(data))
						)	
			# self.log.debug("QUERY %s, DATA %s", query, data)
			try:
				self.cursor.execute(query, data)
			except sqlite3.OperationalError as oe:
				if "no such table" in str(oe):
					Cursor.registerTable(obj)
					self.setupTables()
					self.save(obj)
				else:
					raise oe
			self.conn.commit()
			Cursor.lastCommit = time.time()
				
	
	def query(self, obj, cols=[]):
		"""
		Returns a list of columns (cols) from obj (obj)
		"""
		queryCols = ",".join(cols)
		query = """select %s from %s""" % (queryCols, obj.DB_TABLE_NAME)
		rows = self.cursor.execute(query)
		return rows.fetchall()
		
	def delete(self, obj, col, id):
		"""
		Delete an object from table (obj) where column (col) matches (id)
		"""
		query = """delete from %s where %s=?""" % (obj.DB_TABLE_NAME, col)
		rows = self.cursor.execute(query, [id])
		return rows.fetchall()
	
	def getDupData(self):
		query = """select * from FileObject where strongHash in (select strongHash from (select strongHash, count(*) as numdups from FileObject group by strongHash order by numdups) where numdups>1 and scanParent in (select filename from ScanParent))  order by size DESC"""
		rows = self.cursor.execute(query)
		return rows.fetchall()
		
		
	
			
	# def load(self, obj, objtype, query):
	# 	"""Load data into a list of type 'obj' with query 'query'"""
	# 	data = []
	# 	table = getattr(schema, type)
	# 	objattrs = [od[0] for od in table]
	# 	
	# 	rows = self.cursor.execute(query)
	# 	row = rows.fetchone()
	# 	while row:
	# 		newobj = obj()
	# 		for idx, attrs in enumerate(objattrs):
	# 			setattr(newobj, row[idx]) 
	# 		data.append(newobj)
	# 		row = rows.fetchone()
	# 		
	# 	return data
		

class UniquityDBException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)