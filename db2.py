# -*- coding: utf-8 -*-
import sqlite3
import os.path

class Database(object):
	def __init__(self):
		self.sqlite_file='db.db'

	def add(self,itemid,itemtype,count,stage,rpcid):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("INSERT OR IGNORE INTO drops (itemid,itemtype,count,stage,rpcid) VALUES (%s,%s,%s,%s,'%s')"%(itemid,itemtype,count,stage,rpcid))
		conn.commit()
		conn.close()

if __name__ == '__main__':
	db=Database()