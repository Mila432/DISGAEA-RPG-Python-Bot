# -*- coding: utf-8 -*-
import sqlite3
import os.path

class Database(object):
	def __init__(self):
		self.sqlite_file='db.db'
		if not os.path.isfile(self.sqlite_file):
			self.createDb()

	def createDb(self):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute('''CREATE TABLE "drops" ("id" INTEGER,"itemid" TEXT,"itemtype" INTEGER,"count" INTEGER,"stage" INTEGER,"rpcid" TEXT,PRIMARY KEY("id" AUTOINCREMENT));''')
		conn.commit()
		conn.close()

	def add(self,itemid,itemtype,count,stage,rpcid):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("INSERT OR IGNORE INTO drops (itemid,itemtype,count,stage,rpcid) VALUES (%s,%s,%s,%s,'%s')"%(itemid,itemtype,count,stage,rpcid))
		conn.commit()
		conn.close()

if __name__ == '__main__':
	db=Database()