import cx_Oracle
import os

class DbOracle :
   """
   Anbindung an eine Oracle Datenbankname

   Die Anbindung wird ueber einen TNS-Names String bewerkststelligt.

   HINT:
      Autocommit wird eingeschalten!

   Static Methods:  
      giveInsert
      giveUpate

   """

   connection = None

   # TNS-Names String
   TNS='%(username)s/%(password)s@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=%(host)s)(PORT=%(port)s)))(CONNECT_DATA=( SID=%(v9i)s)))'
   connectstring = None

   def __init__(self,username,password,sid,host,port,nls_lang="German_Germany.WE8ISO8859P1") :
      os.environ["NLS_LANG"] = nls_lang
      self.connectstring = self.TNS % {
           'username':username,
           'password':password,
           'v9i':sid,
           'host':host,
           'port':port
           }
      
      self.connection = cx_Oracle.connect(self.connectstring)
      self.connection.autocommit = True

   
   def giveInsert(tablename=None,fields=None):
      """
      Liefert eine Oracle spezelles form eines prepared statments

      @param   tablename         Tabellenanmen
      @param   fields            Eine Liste von Feldnamen
      
      @return  insertstatement   Oracle spezialisiert

      """
      itemlist = []

      for itemno in range(len(fields)):
         itemlist.append(':{0}'.format(str(itemno+1)))
      
      return "insert into {0} ({1}) values({2})".format(tablename,','.join(fields),','.join(itemlist))
   giveInsert = staticmethod(giveInsert)
   

   def giveUpdate(tablename=None,fields=None,primarykey=None):
      """
      Liefert eine Oracle spezielles form eines prepared statments

      @param   tablename         Tabellenanmen
      @param   fields            Eine Liste von Feldnamen
      @param   primarykey        Name des Primarykeys in der Datenbank
      
      @return  insertstatement   Oracle spezialisiert

      """
      itemlist = []
      
      for fld in fields:         
         if fld != primarykey:
            itemlist.append('{0}=:{0}'.format(fld))
           
      sql = 'update {0} set {1} where {2}=:{2}'.format(tablename,','.join(itemlist),primarykey)      
      return sql

   giveUpdate = staticmethod(giveUpdate)
   
   def __del__(self):
      self.connection.close()
