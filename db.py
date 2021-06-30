# -*- coding: utf-8 -*-
import sqlite3
import os.path

class Database(object):
	def __init__(self):
		self.sqlite_file='accounts.db'

	def addAccount(self,uuid,password,pid,gems):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("INSERT OR IGNORE INTO players (uuid,password,id,gems) VALUES ('%s','%s',%s,%s)"%(uuid,password,pid,gems))
		conn.commit()
		conn.close()

	def updateAccount(self,pid,gems,uuid):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("UPDATE players SET id='%s',gems=%s WHERE uuid='%s'"%(pid,gems,uuid))
		conn.commit()
		conn.close()

	def getAllAccounts(self):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("SELECT uuid,id FROM players")
		all_rows = c.fetchall()
		conn.close()
		return all_rows

if __name__ == '__main__':
	db=Database()
	db.createDb()