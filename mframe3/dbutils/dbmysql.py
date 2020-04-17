import MySQLdb

class DbMySql :
   """SQL Datenbankverbindung spezialisiert fuer mySQL
      """

   connection = None

   def __init__(self,host,port,user,passwd,db):
      self.connection = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)

   def __del__(self):
      self.connection.close()


   def giveInsert(tablename=None,fields=None,primarykey=None):
      """
      Liefert eine mysql spezelles form eines prepared statments

      @param   tablename         Tabellenanmen
      @param   fields            Eine Liste von Feldnamen

      @return  insertstatement   MySQL spezialisiert

      """
      itemlist = []

      for fld in fields:
         if fld != primarykey:
            itemlist.append('{0}'.format('%s'))

      retval =  '''insert into {0} ({1}) values({2})'''.format(tablename,','.join(fields),','.join(itemlist))

      return retval

   giveInsert = staticmethod(giveInsert)



   def giveUpdate(tablename=None,fields=None,primarykey=None):
      """
      Liefert eine mysql spezielles form eines prepared statments

      @param   tablename         Tabellenanmen
      @param   fields            Eine Liste von Feldnamen
      @param   primarykey        Name des Primarykeys in der Datenbank

      @return  insertstatement   Oracle spezialisiert

      """
      itemlist = []

      for fld in fields:

         if fld != primarykey:
            itemlist.append('{0}=%s'.format(fld))

      sql = 'update {0} set {1} where {2}=%s'.format(tablename,','.join(itemlist),primarykey)
      return sql

   giveUpdate = staticmethod(giveUpdate)

