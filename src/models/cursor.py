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
		
	def setupTables(self):
		cursor = self.conn.cursor()
		for tableName in schema.TYPES:
			query = "CREATE TABLE IF NOT EXISTS %s (dbid INTEGER PRIMARY KEY AUTOINCREMENT," % tableName
			columns = []
			for column in getattr(schema, tableName):
				columns.append("%s %s" % (column[0], self.__getSQLType(column[1]) ))
			query += ",".join(columns)
			query += ")"
				
			cursor.execute(query)
			self.conn.commit()
			Cursor.lastCommit = time.time()
		
	def save(self, type, obj):		
		if type not in schema.TYPES:
			raise ValueError("Unable to save '%s' to database, save function non-existant in schema." % type)
		else:
			table = getattr(schema, type)
			values = [value[0] for value in table]
			data = [getattr(obj, objdata[0]) for objdata in table]
			
			query = "INSERT INTO %s (%s) VALUES (%s)" % (type, 
						",".join(values),
						",".join("?" * len(data))
						)	
			self.cursor.execute(query, data)
			self.conn.commit()
			Cursor.lastCommit = time.time()
	
	def getDupData(self):
		
		query = """select * from FILE where strongHash in (select strongHash from (select strongHash, count(*) as numdups from FILE group by strongHash order by numdups) where numdups>1) order by size DESC"""
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
		
						
	def __saveFile(self, objdata):
		pass
		# sql = "INSERT INTO files VALUES (%s)" % ",".join("?" * len(objdata))
		# cursor = self.conn.cursor()
		# cursor.execute(sql, objdata)
		# cursor.close()
		# self.conn.commit()
		
					
		# STANDARD_STAT_FORMAT = ['st_mode', 'st_ino', 'st_dev', 'st_nlink', 
		# 						'st_uid', 'st_gid', 'st_size',
		# 						'st_atime', 'st_mtime', 'st_ctime']

class UniquityDBException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)