"""

domain.py
  Copyright 2020 Wilhelm Nagy <wnagy@NY32>
  More details see Readme.md

Autor    : W. Nagy
Seit     : 1.4.2020
Kontakt  : wilhelm.nagy@gmail.com

Die Domain enthält Daten, die von der Praesentation dargestellt werden. E
s ist von Praesentation und Steuerung unabhaengig. 
Die Aenderungen der Daten werden der Praesentation durch das Entwurfsmuster 
"Beobachter" bekanntgegeben. 

HINT:
¯¯¯¯¯
   Die Klassen SqlConverter und EachDomain sind nicht dafuer gedacht
   direkt verwendet zu werden.

   Vorbereitet fuer
     + oracle
     + sqLite
     + mySql


History
¯¯¯¯¯¯¯
_VERSION_._AKTION____________________________________________________
3.0      | Uebernahme aus dbaccess mframe 2.x
         |

"""
import codecs
import re
from mframe3.dbutils.database    import Database
from mframe3.emergency           import Emergency
from mframe3.dateconverter       import Dateconverter
from mframe3.dbutils.checktype   import Checktype


class Domain(Database,Checktype):
   """
   Basisklasse fuer alle Domains
   
   """
   dbFieldIndex = lambda self,fieldnames,domain,fld : fieldnames.index(self.meta['fields'][fld]['dbfield'])
   
   db                   = None         # Datenbankhandle
   fields               = None         # Felder
   limit                = None         # Maximale Anzahl zu lesender Records
   offset               = None         # Anzahl der  zu überspringenden Records
   rownum               = None         # Aktuelle Recordnummer
   usedfields           = None
   typecheckStrict      = True         # False schaltet Typenueberpruefung ab
   
   db                   = None         # Datenbank handle
   cursor               = None         # Cursor auf die Datenbanktabelle
   tablename            = None         # Tabellename
   currec               = {}           # Aktueller Record
   isOk                 = False        # [True|False] Datenbankoperatonsstatus
   typecheckNoneAllowed = True         # True bei Typencheck ist None ein erlaubter Wert
   lastsql              = None         # Letzte verwendedete SQL Anweisung
   lastsqlvalues        = list()       # Liste der Werte fuer SQL
   typecheckStrict      = True         # False schaltet Typenueberpruefung ab
   errors               = []           # Liste von Fehlrmeldungen
   mode                 = None         # Haelt den Modus (delete,update,insert)
   hasErrors            = False        # Beim verarbeiten von mehreren Felder wird als
                                       # globale Fehlermelder verwendet.

   DELETE   = 'delete'
   UPDATE   = 'update'
   INSERT   = 'insert'
   
   includeflds = []
   
   
   
   meta = {
      }


   def __init__(self,db=None,autocommit=True) :
      """
      Initialisierung der Domainklasse.

      @param         db          Datenkhandle
      @param         autocomit   Automatisches Commit

      """
      self.db = db
      self.settings     = self.db.settings
      self.user         = self.db.user
      self.logger       = self.db.logger
      self.cgiparam     = self.db.cgiparam
      self.writelog     = self.db.writelog
      
      self.logger.debug('Initiate Domain datbasestype "{}" and User: "{}"'.format(self.db.dbtype,self.user))

      if self.db is not None: 
         self.isOk = True
      else:
         return
      self.clear()
      self.cursor = db.db.connection.cursor()
      
      # Autocommit nur bei mySQL
      if self.db.dbtype == self.db.DBTYPE_MYSQL:
         self.cursor.connection.autocommit(autocommit)

   def __str__(self):
      retval = list()
      retval.append("Status: {}".format(self.isOk))
      retval.append("Table: {}".format(self.meta.get('tablename','k.a.')))
      retval.append('Values:')
      for fld in self.getDomainFieldnames():
         item =' {} = "{}"'.format(fld,self.getValue(fld))
         retval.append(item)
      retval.append("Errors: {}".format(repr(self.errors)))
      return "\n".join(retval)

   def raiseTypeError(self,fldtype,name,value):
      """
      gibt Fehlermeldung bei Typenfehler aus.

      HINT:
         Diese Methode wirft eine TypeError mit
         einer Fehlermeldung

      @param   fldtype        Typ des Feldes
      @param   name           Domain-Feldname
      @param   value          Uebergebener Wert

      """
      myType =  str(type(value))
      raise TypeError('"%(value)s" ist nicht vom Typ %(type)s in Feld %(name)s, Typ: %(mytype)s in Klasse: "(%(classname)s)"!' % {'value':str(value),'type':fldtype,'name':name,'classname':self.__class__,'mytype':myType})


   def set(self,name=None,value=None):
      """
      Setzt den Inhalt eines Feldes der Domain

      @param   name        Domainfeldnamen
      @param   value       zu setzender Wert

      """
      if name is None:
         raise ValueError("Domain:: Feldname fehlt")
      self.__setattr__(name,value)

   def clear(self):
      """
      setzt alle Attribute welche als Datenbankfelder deklariert
      wurden auf None.

      Diese Method kann dazu verwenden werden das Domain-Objekt
      wiederzuverwenden.
      """
      for fld in self.meta['fields'].keys():
         self.__dict__[fld] = None

   def getPK(self):
      """
      Gibt den Domain-Felnamen des Primary Keys zurueck
      """
      return self.meta['primarykey']

   def getDbPK(self):
      """
      Gibt den Namen des Primary Key der Datenbanktabelle zurueck.
      """
      pk = self.meta['primarykey']

      return self.meta['fields'][pk]['dbfield']

   def getFieldnames(self) :
      """
      Liefert eine Liste mit Datenbank-Feldname fuer den Cursor.

      @param   cursor      Cursor auf eine Datenbanktabelle

      """
      lstField = []
      for item in self.cursor.description :
         lstField.append(item[0])

      return lstField

   def getDbFieldName(self,fld):
      """
      Liefert den Namen des Datenbankfeldes auf basis des Domainfeldnamen

      @param   fld         Domainfeldname

      @return  Datenbankfeldname
      """
      return self.meta['fields'][fld]['dbfield']

   def getDbFieldType(self,fld):
      """
      Liefert den Type des Datenbankfeldes auf basis des Domainfeldnamen

      @param   fld         Domainfeldname

      @return  Typ
      """
      try:
         return self.meta['fields'][fld]['type']
      except:
         return Database.TYPE_STRING

   def getDbFieldNames(self):
      """
      Liefert eine Liste mit allen Tabellenfeldnamen

      @return     Liste der Namen
      """

      retval = []
      for fld in self.getDomainFieldnames():
         retval.append(self.getDbFieldName(fld))
      return retval

   def get(self,id=None,where=None,values=None):
      """
      Liest geanau einen Datensatz aus der Tabelle
      und kopiert die Daten in die Domain.

      HINT:
         wenn nicht gefunden wird isOk auf False gesetzt
         und die Datenfelder sind None.

      @param   id          Primary Key
      @param   where       Where Klausel
      @param   values      Inhaltswerte (Bei Verwendung von Platzhalten)

      """

      if id==None and where==None:
         raise ValueError("{0}::get: Keine Parameter angegeben".format(self.__class__.__name__))

      # bauen der Where-Klausel
      if where is not None:
         where = SqlConverter.convert(self,where)

      # Verwende Primariy Key fuer Datenbak
      primkey      = self.getDbPK()

      tablename   = self.meta['tablename']
      self.cursor = self.db.db.connection.cursor()

      # Wurde der Primary Key uebergeben
      if (id is not None):
         select = ''

         # Oracle Spezialbehandlung
         if self.db.dbtype == self.db.DBTYPE_ORACLE:

            select = "select * from %(tablename)s where %(pk)s=:id" % {'tablename':tablename,'pk':primkey}

            try:
               self.cursor.execute(select,{'id':id})
            except Exception as e:
               raise ValueError(str(e.message)+' errmsg: :'+select+' ID: '+str(id))

         # MySQL Spezialbehandlung
         elif self.db.dbtype == self.db.DBTYPE_MYSQL:
            select = "select * from %(tablename)s where %(pk)s=%%s" % {'tablename':tablename,'pk':primkey}
            self.cursor.execute(select,(id))

         else:
            select = "select * from %(tablename)s where %(pk)s=?" % {'tablename':tablename,'pk':primkey}
            self.cursor.execute(select,[id])

      else:
         if isinstance(where,str):
            if values is None:
               select = 'select * from %(tablename)s where %(where)s'% {'tablename':tablename,'where':where}
               self.cursor.execute(select)
            else:
               select = 'select * from %(tablename)s where %(where)s'% {'tablename':tablename,'where':where}               
               #print >>sys.stderr,"User prepared: {0} values {1}".format(select,','.join(values))
               self.cursor.execute(select,values)
         else:            
            raise Exception('where Option muss den Typ str oder dict haben!')
                     
      fieldnames = self.getFieldnames()

      record = self.cursor.fetchone()

      if record is not None:
         self.isOk = True
         for fld in self.meta['fields'] :
            iFieldnames = self.dbFieldIndex(fieldnames,self,fld)
            value = record[iFieldnames]
            if self.getDbFieldType(fld) == Database.TYPE_JSON and not self.db.jsonAsString:
               if value is not None:
                  value = json.loads(value,encoding=self.db.jsonEncoding)

            if self.db.dbtype == self.db.DBTYPE_MYSQL:
               fldType = self.getDbFieldType(fld)
               if fldType == Database.TYPE_ANSIDATE:
                  if value is not None:
                     value = value.isoformat()
            self.__dict__[fld] = value
            self.isOk = self.afterRead()         
      else:
         self.isOk = False

         for fld in self.meta['fields'] :
            self.__dict__[fld] = None
         self.afterRead()         
      return self.isOk

   def getDbFieldType(self,fld):
      """
      Liefert den Type des Datenbankfeldes auf basis des Domainfeldnamen

      @param   fld         Domainfeldname

      @return  Typ
      """
      try:
         return self.meta['fields'][fld]['type']
      except:
         return Database.TYPE_STRING

   def __setattr__(self,name,value):
      """
      Pruefen auf Typengueltigkeit.

      HINT:
         geht die Pruefung fehl, so wird ein
         Fehler geworfen.

      @param   name        Domainfeldname
      @param   value       Wert

      """

      dc = Dateconverter()

      # Wurde Typenueberpruefung abgeschalten
      if not self.typecheckStrict:
         self.__dict__[name] = value
         return

      # None als Eingabewert erlaubt.
      if self.typecheckNoneAllowed and value is None:
         self.__dict__[name] = value
         return

      # Ist das ein Domainfeld
      if name in self.meta['fields']:
         # Feldobjekt
         fld = self.meta['fields'][name]
         # Wurde type in meta deklariert
         if 'type' in fld:
            # Integer pruefen
            if fld['type'] == Database.TYPE_INTEGER:
               if self.isInteger(value):
                  self.__dict__[name] = value
               else:
                  self.raiseTypeError(fld['type'],name,value)
            elif fld['type'] == Database.TYPE_LONG:
               if self.isLong(value):
                  self.__dict__[name] = value
               else:
                  self.raiseTypeError(fld['type'],name,value)

            # String pruefen
            elif fld['type'] == Database.TYPE_STRING:
               if self.isString(value):
                  self.__dict__[name] = value
               else:
                  self.raiseTypeError(fld['type'],name,value)

            # Emailadresse pruefen
            elif fld['type'] == Database.TYPE_EMAIL:
               if self.isString(value):
                  self.__dict__[name] = value
               else:
                  self.raiseTypeError(fld['type'],name,value)

            # Float
            elif fld['type'] == Database.TYPE_FLOAT:
               if self.isFloat(value):
                  self.__dict__[name] = value
               else:
                  self.raiseTypeError(fld['type'],name,value)

            # Database.TYPE_DOUBLE ist equivalent zu float
            elif fld['type'] == Database.TYPE_DOUBLE:
               if self.isFloat(value):
                  self.__dict__[name] = value
               else:
                  self.raiseTypeError(fld['type'],name,value)

            # JSON
            elif fld['type'] == Database.TYPE_JSON:               
               self.__dict__[name] = json.dumps(value,indent=self.db.jsonIndent,encoding=self.db.jsonEncoding)                              
            
            # Behandlung des Datentypes Date.
            # Dieser wird nur 
            elif fld['type'] == 'Date':
               if self.db.dbtype == self.db.DBTYPE_ORACLE:                  
                  
                  # Ist Value schon ein Zeitobjekt ist
                  # keine Umwandlung mehr notwendig.
                  if isinstance(value,datetime): 
                     self.__dict__[name] = value
                     return
                     
                  try:
                     value = dc.fromString(value)
                  except:
                     self.raiseTypeError(fld['type'],name,value)
               
                  value =  datetime.strptime(value, "%Y-%m-%dT%H:%M")

                  self.__dict__[name] = value
               elif self.db.dbtype in [self.db.DBTYPE_SQLITE,self.db.DBTYPE_MYSQL]:
                  if self.isDate(value):
                     dc = Dateconverter()
                     secs = True
                     if 'secs' in fld: secs = fld['secs']
                     self.__dict__[name] = dc.giveAsANSIDateTime(value,secs=secs)
                  else:
                     self.raiseTypeError(fld['type'],name,value)                  
               else:
                  raise Exception("Ungueltiger Datenbanktyp")
                  return

            # AnsiDate
            # In der Domain kann die Option secs (True/False) angegeben werden
            # diese steuert ob Sekunden angegeben werden sollen.

            elif fld['type'] == Database.TYPE_ANSIDATE:
               if self.isDate(value):
                  dc = Dateconverter()
                  secs = True
                  if 'secs' in fld: secs = fld['secs']
                  self.__dict__[name] = dc.giveAsANSIDateTime(value,secs=secs)
               else:
                  self.raiseTypeError(fld['type'],name,value)

            else:
               raise Exception("Ungueltiger Type '{0} in Feld {1}".format(fld['type'],name))
               return
         else:
            pass

      else:
         self.__dict__[name] = value

   def getDomainFieldnames(self):
      """
      Liefert eine Liste mit den Domainfeldern
      """
      retval = []
      for fld in self.meta['fields'].keys():
         retval.append(fld)

      return retval

   def setValue(self,name=None,value=None):
      """
      Setzt den Inhalt eines Feldes der Domain

      @param   name        Domainfeldnamen
      @param   value       zu setzender Wert

      """
      if name is None:
         raise ValueError("Domain:: Feldname fehlt")
      self.__setattr__(name,value)

   def getValue(self,fld,nvl=None):
      """
      Liefert den Inhalt eines Feldes auf Grund eines Domain-Feldnamen

      @param fld           Feldnamen

      """
      value = self.__dict__[fld] or nvl
      return value

   def eachDomain(self,where=None,orderby=None,limit=None,filter=None,offset=None):
      """
      Liefert ein Resultset auf einen Datenbankabfrage.
      
      @param   where          Selektionskriterien
      @param   orderby        Sortierklausel
      @param   limit          Maxmale Ausgabemenge
      @param   filter         Filtern
      
      """
      self.logger.debug('where "{}", orderby "{}", limit="{}"'.format(where,orderby,limit))

      self.db.rownum=0
      
      self.cursor = self.db.db.connection.cursor()

      # Where by Mysql alle % durch %% ersetzen,
      # da sonst Probleme mit prepared statments
      if where is not None:
         if self.db.dbtype == self.db.DBTYPE_MYSQL:
            where = where.replace('%','%%')
      #
      # Behandlung von Limt
      #
      if limit is not None:

         if isinstance(limit,int):
            self.offset = 0
            self.limit  = limit
         elif isinstance(limit,tuple):
            if len(limit) != 2: raise Exception("eachDomain, muss genau zwei Elemente haben")
            self.offset = int(limit[0])
            self.limit  = int(limit[1])
         else:
            raise Exception("eachDomian bei Option limit nur Integer oder Tuple gueltig")
      
      SqlConverter.setSelectAndValue(self,where,filter,orderby)
      
      self.logger.debug('lastsql: "{}", lastsqlvalues: "{}"'.format(self.lastsql,self.lastsqlvalues))

      self.rownum = 0

      for record in self.cursor.execute(self.lastsql,self.lastsqlvalues):
         self.value = None
         
         """
         durchlaufen des Datenstromes bis keine
         weiteren Datensaetze mehr gefunden werden.
         """                  
         self.rownum += 1

         if self.limit is not None: 
            if self.rownum > self.limit:
               break

         fieldnames = self.getFieldnames()
         self.logger.debug('Fieldnames: "{}"'.format(fieldnames))
          
         for fld in self.meta['fields']:
            try:
               iFieldnames  = self.dbFieldIndex(fieldnames,self,fld)
            except Exception as e:
               raise(ValueError(e))

            value = record[iFieldnames]
            
            if self.getDbFieldType(fld) == Database.TYPE_JSON and not self.db.jsonAsString:
               if value is not None:
                  value = json.loads(value,encoding=self.db.jsonEncoding)
                  
            if self.db.dbtype == self.db.DBTYPE_MYSQL:
               fldType = self.getDbFieldType(fld)
               if fldType == Database.TYPE_ANSIDATE:
                  if value is not None:
                     value = value.isoformat()

            self.__dict__[fld] = value
            self.db.__dict__['rownum'] = self.rownum
         
         if self.isOk:
            self.isOk = self.afterRead()
         else:
            self.afterRead()

         yield self

      # Wenn offset deklariert, Datensaetze ueberlesen
      self.rownum = 0
      if self.offset is not None:
         for cnt in range(self.offset):
            record = self.cursor.fetchone()
            if record is None: self.rownum+=1

   def prepareValue(self,fld,value):
      """
      Umwandlung einer String Variable in die von der Domain
      gewuenschten Datentyp

      usage: prepareValue (fld,value)
      
      @param fld          Feldname
      @param value        Inhalt

      @return              Praeparierter Inhalt

      HINT:
         Wenn Ein Fehler auftritt, wird self.hasErrors gesetzt

      """

      # Soll der Eingelesenen Wert aus dem CGI
      # veraendert werden?
      value = self.onReadFromCgi(fieldname=fld,value=value)

      # Pruefen ob Checkroutine verwendet werden soll
      self.isOk = self.onCgiField(fieldname=fld,value=value)

      if not self.isOk: self.hasErrors = True
      # Ein Leeres Feld wird als None behandelt
      if re.search('^\s*$',value):
         value = None

      if value is not None:
         try:
            fldtype = self.meta['fields'][fld]['type']
            if fldtype == Database.TYPE_INTEGER:
               return int(value)

            elif fldtype in [Database.TYPE_DOUBLE,Database.TYPE_FLOAT]:
               # Wenn schon float keine weitere Veranlassung
               if isinstance(value, float): return value

               # Integer in Float
               if isinstance(value, int): return float(value)

               # Ist Dezimalzahl mit Punkten als Tausendertrenner
               if re.search(r'^[-+]?(\d*\.)*\d{1,3}(\,\d+)*$',value):
                  value = value.replace('.','')  # entferne Tausenderpunkte
                  value = value.replace(',','.') # Tausche Komma mit Punkt
                  value = float(value)
               else:
                  # Wenn nur ein Punkt ist Dezimal
                  # Wenn genau ein Komma ist Dezimel
                  if value.count(',') == 1: value = value.replace(',','.')
                  value = float(value)
            
         except Exception as ex:
            raise Exception("[domain.prepareValue] {}".format(ex))

      return (value)

   def fromCgi(self,cgiparam=None,flds=None,typecheckStrict=True):
      """
      Befuellen der Domain aus dem CGI
      HINT:
         Typecheck wird ausgeschalten!
         wirft eine Exception, wenn ein Fehler beim befuellen auftritt

      @param cgiparam     Methode zum lesen aus dem CGI
      @param flds         eine Liste von Felder, welche verewendet werden soll
                              ist die Liste None, so wird die Feldliste aus den Metadaten uebernommen

      @return  [True|Flase] das OK Kennzeichen
      """
      self.typecheckStrict = typecheckStrict

      if cgiparam is None:
         raise Exception("Die Methode fromCgi muss cigparam uebergeben werden!")

      self.isOk = True

      if flds is None:
         flds = self.usedFields(cgiparam)

      self.logger.debug('fields: {}'.format(repr(flds)))
      
      self.hasErrors = False

      for fld in flds:
         value = cgiparam(name=fld,nvl=None)         
         try:
            value = self.prepareValue(fld,value)
            self.set(fld,value)
         except Exception as ex:
            self.hasErrors = True
            self.errors.append("[{}] '{}'".format(fld,ex))

      self.usedFields = flds

      # Wenn bislang noch keine Fehler aufgetreten sind
      # wird handler afterCgi auferufen.
      if not self.hasErrors:
         self.hasErrors = not self.afterCgi()

      if self.hasErrors:
         self.isOk = False
         self.logger.debug('Fehlgeschlaten: {}'.format(repr(self.errors)))

      return self.isOk

   def usedFields(self,cgiparam=None):
      """
      Liefert eine Liste von Feldnamen,
      welche durch das CGI uebergeben wurden
      und in der Domain Feldliste vorhanden ist.

      @param cgiparam     Methode zum lesen aus dem CGI

      @return Feldlist
      """
      if cgiparam is None:
         raise Exception("Die Methode fromCgi muss cigparam uebergeben werden")
      flds = []

      for fld in self.meta['fields'].keys():
         value = cgiparam(name=fld,nvl='',noneifnotused=True)
         if value is not None:
            flds.append(fld)

      return flds

   def createSqlParameter(self):
      self.lastsqlvalues = []
      self.flds =[]
      
      for fld in self.meta['fields'].keys():
         if not isinstance(fld,str) :
            raise ValueError("Felder in Domain muessen als Strings deklariert werden!")

         dbFieldName = self.getDbFieldName(fld)

         if self.db.dbtype == self.db.DBTYPE_MYSQL:
            if dbFieldName != self.getDbPK():
               self.flds.append(dbFieldName)
               if self.__dict__[fld] is None:
                  self.lastsqlvalues.append(None)
               else:
                  self.lastsqlvalues.append(self.__dict__[fld])
         elif self.db.dbtype == self.db.DBTYPE_SQLITE:
            self.flds.append(dbFieldName)
            if self.__dict__[fld] is None:
               self.lastsqlvalues.append(None)
            else:
               self.lastsqlvalues.append(self.__dict__[fld])

         elif self.db.dbtype == self.db.DBTYPE_ORACLE:
            self.flds.append(dbFieldName)
            if self.__dict__[fld] is None:
               self.lastsqlvalues.append(None)
            else:
               self.lastsqlvalues.append(self.__dict__[fld])

            
         else:
            raise Exception('Ungueltiger dbtype: "{0}"'.format(self.db.dbtype))      

   def insert(self):
      """
      Einfuegen eines Datensatzes
      Die aktuellen Werte aus der Domain werden in
      die Datenbank geschrieben.

      HINT:
         vor dem Insert wird die Methode onInsert aufgerufen.
         Liefert diese False zurueck wird der Einfuegevorgang
         abgebrochen.

      @return  [True|Flase] das OK Kennzeichen
      """
      
      self.isOk = self.onInsert()
      if not self.isOk: return False

      self.isOk = self.onWrite(mode=self.INSERT)
      if not self.isOk: return False


      values = list()

      tablename   = self.meta['tablename']
      
      self.lastsqlvalues = values
      
      if self.db.dbtype == self.db.DBTYPE_ORACLE:
         # Erzeugen Oracle spezialisertes Insert Statement
         from dbaccess.dboracle import DbOracle         
         
         self.createSqlParameter()

         self.lastsql = DbOracle.giveInsert(tablename=tablename,fields=self.flds)
                  
      elif self.db.dbtype == self.db.DBTYPE_MYSQL:
         from dbaccess.dbmysql import DbMySql
         
         self.createSqlParameter()
         
         self.lastsql = DbMySql.giveInsert(tablename=tablename,fields=self.flds,primarykey=self.getDbPK())
         self.lastsqlvalues = tuple(self.lastsqlvalues)

      else:
         # Herstellen einer Liste von Fragezeichen
         # fuer prepared statement
         self.createSqlParameter()
         fragezeichen = '?,' * len(self.flds)
         fragezeichen = fragezeichen[:-1]
         self.lastsql = 'insert into %(tablename)s (%(flds)s) values(%(fragezeichen)s)' % {
            'tablename':tablename,
            'flds':','.join(self.flds),
            'fragezeichen':fragezeichen}


      if self.isOk:
         self.createSqlParameter()
         try:
            self.cursor.execute(self.lastsql,self.lastsqlvalues)
         except Exception as e:
            self.isOk = False
            self.errors.append("DB Fehler bei insert {0}".format(e))

      if self.isOk and self.db.dbtype == self.db.DBTYPE_SQLITE:
         sql = 'select seq from sqlite_sequence where name="{0}"'.format(tablename)
         self.cursor.execute(sql)
         next_record = self.cursor.fetchone()

         # Pruefen ob last Autoincrement erreichbar
         # ist wenn nicht wird None gespeichert.
         if next_record is None:
            self.lastAutoincrement = None
         else:
            self.lastAutoincrement = next_record[0]

      elif self.isOk and self.db.dbtype == self.db.DBTYPE_MYSQL:
         self.cursor.execute('SELECT last_insert_id();')
         next_record = self.cursor.fetchone()
         self.lastAutoincrement = next_record[0]
      else:
         self.lastAutoincrement = None

      return self.isOk


   def update(self,usedFields=None,fill=None):
      """
      Veraendern des Datensatzes basieren auf den Inhalten der Domain
         HINT:
            vor dem Update wird die Methode onUpdate aufgerufen.
            Liefert diese False zurueck wird der Ueberschreibenvorgang
            abgebrochen.

            Der Methode kann eine Feldliste uebergeben werden.
            Ist diese deklariert, so werden nur die deklarierten Felder
            zum Update verwendet.

      @parma   usedFields
               + None      Alle Felder werden benutzt
               + list      Liste von Feldern
               + 'auto'    Attribute usedFields wird benutzt
                           dies ist praktisch, wenn vorher fromCgi
                           aufgerufen wurde.
      @return  [True|Flase] das OK Kennzeichen

      """
     
      self.isOk = self.onUpdate()
      if not self.isOk: return False

      self.isOk = self.onWrite(mode=self.UPDATE)
      if not self.isOk: return False
         
      flds = list()

      if usedFields is None:
         for fld in self.meta['fields'].keys():
            flds.append(fld)
      else:
         if usedFields == 'auto':
            flds = self.usedFields
         else:
            flds = usedFields
         
      # Included Flds
      flds += self.includeflds
               
      values = list()
      primkey     = self.getPK()

      # Sicherheitsabfrage:
      # Bei Update muss Primary Key Feld vorhanden sein.
      #
      if not primkey in flds:
         raise Exception('Bei update konnte der Primary Key "{0}" in Feldliste [{1}] nicht gefunden werden'.format(primkey,','.join(flds)))

      for fld in flds:
         if self.__dict__[fld] is None:
            values.append(None)
         else:
            values.append(self.__dict__[fld])

      tablename   = self.meta['tablename']
      values.append(self.__dict__[primkey])
      self.lastsqlvalues = values

      if self.db.dbtype == self.db.DBTYPE_ORACLE:
         
         # Erzeugen Oracle spezialisertes Update Statement
         from dbaccess.dboracle import DbOracle
         dbFlds = []
         self.lastsqlvalues = {}
         
         for fld in flds:
            dbFlds.append(self.getDbFieldName(fld))
            self.lastsqlvalues[self.getDbFieldName(fld)] = self.__dict__[fld]

         self.lastsql = DbOracle.giveUpdate(
             tablename=tablename,
             fields=dbFlds,
             primarykey=self.getDbPK()
             )

      elif self.db.dbtype == self.db.DBTYPE_MYSQL:
         # Erzeugen Mysql spezialisertes Insert Statement
         from dbaccess.dbmysql import DbMySql
         dbFlds = []
         self.lastsqlvalues = []
         for fld in flds:
            if fld != self.getPK():
               dbFlds.append(self.getDbFieldName(fld))
               self.lastsqlvalues.append(self.getValue(fld))
         self.lastsqlvalues.append(self.getValue(self.getPK()))

         self.lastsql = DbMySql.giveUpdate(
             tablename=tablename,
             fields=dbFlds,
             primarykey=self.getDbPK()
             )

      else:
         fragezeichen = '?,' * len(flds)
         fragezeichen = fragezeichen[:-1]

         fldList = list()

         for fld in flds:
            fldList.append('%(fld)s=?' % {'fld':self.getDbFieldName(fld)})
         self.lastsql = 'update %(tablename)s set %(flds)s where %(primkey)s = ?' % {
            'tablename':tablename,
            'flds':','.join(fldList),
            'primkey':self.getDbPK()
            }

      if self.isOk:
         try:
            self.cursor.execute(self.lastsql,self.lastsqlvalues)
         except Exception as e:
            self.isOk = False
            self.errors.append("DB Fehler bei update {0} sql: {1}".format(e,self.lastsql))

      return self.isOk

   def delete(self):
      """
      loescht aktuellen Datensatz

      HINT:
         vor dem Loeschen wird onDelete aufgerufen
         liefert die Methode False, so wird der Loeschvorgang
         abgebrochen

      @return  [True|Flase] das OK Kennzeichen

      """
      # Pruefen
      self.isOk = self.onDelete()
      if not self.isOk:
         return False

      self.isOk = self.onWrite(mode=self.DELETE)
      if not self.isOk: return False

      primkey     = self.getDbPK()
      tablename   = self.meta['tablename']
      self.cursor = self.db.db.connection.cursor()

      id = self.__dict__[self.getPK()]
      if id==None:
         raise Exception("Aktueller Datensatz hat keine Eintrag in %(primkey)s" % {'primkey':self.getPK()})

      if self.db.dbtype == self.db.DBTYPE_ORACLE:
         self.lastsql = "delete from %(tablename)s where %(primkey)s=:id" % {'tablename':tablename,'primkey':primkey}

      elif self.db.dbtype == self.db.DBTYPE_MYSQL:
         self.lastsql = "delete from %(tablename)s where %(primkey)s=%%s" % {'tablename':tablename,'primkey':primkey}

      else:
         self.lastsql = 'delete from %(tablename)s where %(primkey)s = ?' % {'tablename':tablename,'primkey':primkey}

      self.lastsqlvalues = list()
      if self.isOk:
         if self.db.dbtype == self.db.DBTYPE_ORACLE:
            self.cursor.execute(self.lastsql,{'id':id})
         elif self.db.dbtype == self.db.DBTYPE_MYSQL:
            self.cursor.execute(self.lastsql,(id))
         else:
            self.cursor.execute(self.lastsql,[id])
      else:pass
      return self.isOk

   def deleteAll(self,where=None):
      """
      Loeschen basierend auf einet Where Klausel

      HINT:
          Dieser Vorgang fueht keine Pruefung mit der Methode onDelete durch.

      @param   where    Eine where Klausel
                        Diese MUSS angegeben werden.

      """

      if where is None:
         raise Exception("bei delteAll ist Parameter where unbedingt notwendig")

      where = SqlConverter.convert(self,where)

      tablename   = self.meta['tablename']
      self.cursor = self.db.db.connection.cursor()
      self.lastsqlvalues = list()
      self.lastsql = "delete from %(tablename)s where %(where)s" % {'tablename':tablename,'where':where}
      self.cursor.execute(self.lastsql)
      
#_______________________________________________________________________
# H A N D L E R
#_______________________________________________________________________

   """
   === H A N D L E R ===

   HINT:
      Handler liefern [True|False] Zurueck.
      Bei False wird die Datenbankaktion abgebrochen

      Fehlermeldungen koennen mit self.addError("Meldung")
      angegben werden.
   """

   def onReadFromCgi(self,fieldname,value):
      """
      Veraender eines eingelesenen Wertes

      @param fieldname         Feldname
      @param value             Inhalt aus dem CGI

      @return  Veraendertet Inhalt aus dem CGI
      """
      return value


   def onCgiField(self,fieldname,value):
      """
      Wenn die Domain ueber das CGI befuellt wir
      wird bei jedem Feld dieser Handler aufgerufen.


      @param fieldname         Feldname
      @param value             Inhalt aus dem CGI

      @param [True|False]      wird False uebergeben so bricht das Laden ab
      """
      return True

   def afterCgi(self):
      """
      Wird nach dem Einlesen aller Felder aus dem CGI
      aufgerufen.

      @return  [True|False]
      """
      return True

   def onDelete(self):
      """
      Wird aufgerufen vor Loeschen eines Datensatzens

      @return [True|False]
      """         
      return True

   def onInsert(self):
      """
      Wird aufgerufen vor Einfuegen eines Datensatzens
      False beendet die Aktion

      @return [True|False]

      """
      return True

   def onUpdate(self):
      """
      Wird aufgerufen vor Veraendern eines Datensatzens
      False beendet die Aktion

      @return [True|False]

      """
      return True

   def onWrite(self,mode=None):
      """
      Wird vor jeder schreibenden
      Operation aufgerfuen.

      @param  mode     Enthaelt insert/update/delete

      @return [True|False]

      """
      return True

   def afterRead(self):
      """
      wird nach dem Lesen einer Doman aufgerufen

      @return [True|False] 
      """         
      return True

   #
   # ################# END OF HANDLER

   
#_______________________________________________________________________
# SQLKONVERTER
#¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
class SqlConverter(object):
   """
   Behandlung von Domainfeldnamen
   bei where und orderby Optionen.

   Reagiert auf die Konfigurationsvariable
   SqlConverter_fieldBegin und SqlConverter_fieldEnd
   sind beide auf None gesetzt, wird keine Umwandlung durchgefuehrt.

   Sucht das Vorkommen von [fieldBegin]domainfeldname[fieldEnd] und ersetzt
   dieses durch den Tabellenfeldnamen

   Beispiel:
      fieldBegin = '$'
      fieldEnd   = ''

      aus Domain fields Definition:
         'personID':{dbfield:'PERSON_ID', ...}

      Ergebnis:
         "$personID = 23" wird zu "PERSON_ID = 23"

   """

   def convert(domain,klausel):
      """
      Konvertierroutine,
      kann als Klassenmethode aufgerufen werden.

      @param   domain         Domainobjekt
      @param   klausel        Zu konvertierende Klausel

      @return  veraenderte Whereklausel

      """
      fieldBegin = domain.settings.SqlConverter_fieldBegin
      fieldEnd   = domain.settings.SqlConverter_fieldEnd

      # Ist Beginn und Ende Kennung None,
      # ist die Umwandlung ausgeschalten
      #
      if fieldBegin is None and fieldEnd == None: return klausel
      # Ist Uebersetzung notwendig?
      try:
         klausel.index(fieldBegin)
      except: return klausel

      fieldlist = []

      for fld in domain.meta['fields']:
         fieldlist.append([fld,domain.meta['fields'][fld]['dbfield']])


      for conv in fieldlist:
         repl = fieldBegin+conv[0]+fieldEnd
         klausel = klausel.replace(repl,conv[1])

      return klausel

   convert = staticmethod(convert)

   def handleFilterOption(domain=None,filter=None,dbtype=None):
      """
      Behandelt die Filteroption
      Deatilierte Beschreibung in der Domain Klasse

         HINT:
            Liefet ein Tuple zurueck
            1. Element eine Whereklausel
            2. Element Einen Datenstruktur.
                       Diese ist abhaengig vom Datenbanktyp
                       Oracle ist ein Dictionary
                       alle anderen eine Liste mit dem Filterwert(value)
      @param      domain            Domainobjekt
      @param      filter            Filteroption (String oder Dictionary)
      @param      dbtype            Datenbanktpy

      @return     tuple mit Ergenissen

      """
      included = domain.getDbFieldNames()
      if dbtype is None:
         dbtype = domain.db.dbtype

      value = None
      include = None
      exclude = None
      useLike = False

      if  isinstance(filter,dict) :
         # Option value
         if not 'value' in filter:
            value = ''
         else:
            value = filter['value']

         # Nur spezielle Felder
         if 'include' in filter:
            if isinstance(filter['include'],str):
               filter['include'] = [filter['include']]
            if not '*' in filter['include']:
               included = []
               for fld in filter['include']:
                  included.append(SqlConverter.convert(domain,fld))

         # Auszuschliessende Felder
         if 'exclude' in filter:
            if isinstance(filter['exclude'],str):
               filter['exclude'] = [filter['exclude']]
            for fld in filter['exclude']:
               fld = SqlConverter.convert(domain,fld)
               try:
                  included.remove(fld)
               except:
                  raise Exception('Feld {0} nicht in Domain gefunden'.format(fld))
      else:
         value = filter

      if value.find('%') != -1 or value.find('_') != -1:
         useLike = True

      auxWhere    = []
      auxValues   = []

      for fld in included:
         if dbtype == domain.db.DBTYPE_ORACLE:
            if useLike:
               auxWhere.append('{0} like :filter'.format(fld))
            else:
               auxWhere.append('{0}=:filter'.format(fld))
         elif dbtype == domain.db.DBTYPE_MYSQL:
            if useLike:
               auxWhere.append('{0} like %s'.format(fld))
            else:
               auxWhere.append('{0}=%s'.format(fld))
         else:
            if useLike:
               auxWhere.append('{0} like ?'.format(fld))
            else:
               auxWhere.append('{0}=?'.format(fld))
         auxValues.append(value)

      if dbtype == domain.db.DBTYPE_ORACLE:
         auxValues = {'filter':value}

      retval = ' OR '.join(auxWhere),auxValues

      return (retval)

   handleFilterOption = staticmethod(handleFilterOption)

   def setSelectAndValue(domain,where=None,filter=None,orderby=None,listoption='*'):
      """
      Analysiert where und Filter Option und setzt in der Domain
      die Sqlklausel und ggf. die Werteliste.

      @param   domain         Domain
      @param   where          Where Klausel
      @param   filter         Filter Option
      @param   orderby        Order By Klausel


      """
      whereText = ''
      orderbyText = ''
      values = []
      domain.lastsqlvalues = []
      domain.lastsql = None

      if orderby is not None :
         orderby = SqlConverter.convert(domain,orderby)
         orderbyText = ' order by '+orderby

      if where is not None :
         where = SqlConverter.convert(domain,where)
         whereText = ' where '+where

      if filter is not None:
         (where,domain.lastsqlvalues) = SqlConverter.handleFilterOption(domain=domain,filter=filter)

         whereText = whereText.replace(' where ',' AND ')
         domain.lastsql = 'select {4} from {0} where ({1}) {2} {3}'.format(domain.meta['tablename'],where,whereText,orderbyText,listoption)

      else:
         #domain.lastsql = 'select * from '+domain.meta['tablename']+whereText+orderbyText
         domain.lastsql = 'select {0} from {1} {2} {3}'.format(listoption,domain.meta['tablename'],whereText,orderbyText)
      domain.lastsql = domain.lastsql.strip(' ')

   setSelectAndValue = staticmethod(setSelectAndValue)
