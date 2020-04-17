import sqlite3

class DbSqlite3 :
   """SQL Datenbankverbindung spezialisiert fuer SQLite

      HINT:
         Die Datenbank wird automatisch auf Autocommit gesetzt

      """
   
   connection = None
   connectstring = None

   def __init__(self,filename) :
      """
      Konsturktor: fuer sqlite ist nur der Datenbankpfad notwendig.
      @param   filename       Dateiname und Pfad auf die Datenbankdatei.
      """
      def dictFactory(cursor, row):
         d = {}
         for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
         return d         
         
      self.connection = sqlite3.connect(filename)
      self.connectstring = filename
      self.connection.text_factory = str
      self.connection.isolation_level = None
      self.connection.row_factory = sqlite3.Row


   def __del__(self):
      self.connection.close()
