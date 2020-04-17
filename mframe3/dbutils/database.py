"""
Datenbank Verbindung

databases.py
  Copyright 2020 Wilhelm Nagy <wnagy@NY32>

  More details see Readme.md

Autor    : W. Nagy
Seit     : 1.4.2020
Kontakt  : wilhelm.nagy@gmail.com


History
¯¯¯¯¯¯¯
_VERSION_._AKTION____________________________________________________
3.0      | Uebernahme aus dbaccess mframe 2.x
         |

"""

class Database(object):
   
   db          = None
   dbtype      = None
   session     = None

   DBTYPE_ORACLE  = 'oracle'
   DBTYPE_SQLITE  = 'sqlite'
   DBTYPE_MYSQL   = 'mysql'

   TYPE_INTEGER   = 'Integer'
   TYPE_LONG      = 'Long'
   TYPE_DOUBLE    = 'Double'
   TYPE_STRING    = 'String'
   TYPE_FLOAT     = 'Float'
   TYPE_JSON      = 'Json'
   TYPE_EMAIL     = 'Email'
   TYPE_ANSIDATE  = 'AnsiDate'
   
   def __init__(self,dbtype,*args):
      """
      Initialiseren
      """
      self.dbtype = dbtype or self.DBTYPE_SQLITE

      if dbtype == self.DBTYPE_SQLITE :
         from mframe3.dbutils.dbsqlite3 import DbSqlite3
         self.filename = args[0]
         self.db = DbSqlite3(args[0])

      elif dbtype == self.DBTYPE_ORACLE :
         # username, passworId, sid
         from mframe3.dbutils.dboracle import DbOracle
         nls_lang = self.settings.oracle['nls_lang'] if 'nls_lang' in config.oracle else None
         if nls_lang is None:                        
            self.db = DbOracle(args[0],args[1],args[2],args[3],args[4])
         else:
            self.db = DbOracle(args[0],args[1],args[2],args[3],args[4],nls_lang)

         self.connectstring = self.db.connectstring

      elif dbtype == self.DBTYPE_MYSQL :
         from mframe3.dbutils.dbmysql import DbMySql
         self.db = DbMySql(args[0],args[1],args[2],args[3],args[4])
      else :
         raise "Ungueltiger Datenbanktype '%s'" % (dbtype)
      

   def cursorFactory(self):
      """
      Liefert eine Cursor auf die atuelle Datenbank
      """
      return self.db.connection.cursor()
     
