# -*- coding: utf-8 -*-
"""
core.py
  Copyright 2020 Wilhelm Nagy <wnagy@NY32>
  More details see Readme.md

Autor    : W. Nagy
Seit     : 1.4.2020
Kontakt  : wilhelm.nagy@gmail.com

ABSTRAKT
========

Diese Klasse stellt die Mehtoden und Attribute zur Steuerung des
Frameworks zu Verfuegung.

HINT
   In diesem Quellentext auf keinen Fall Aenderungen vornehmen!
   
   Sollten Aenderungen notwendig sein so koennen diese in
     /options/mframe.py 
   vorgenommen werden.
   
"""

import logging
import os,sys
import locale
import distutils.dir_util
from http                           import cookies as Cookies

from cgi                            import FieldStorage
from cgi                            import MiniFieldStorage
from datetime                       import datetime

# Load configurations
from config.settings                import Settings
from config.routing                 import Routing

# Load internal libs
from mframe3.controller             import Controller
from mframe3.session                import Session
from mframe3.emergency              import Emergency
from mframe3.template               import PSP
from mframe3.templateengine         import Templateengine
from mframe3.dbutils.database       import Database


FOREVER = 1

class Core(object):
   pymframeversion   = "3.0"
   settings          = Settings()
   logger            = None
   startTime         = datetime.now()
   content           = ''
   session           = None
   usecgi            = True
   form              = None
   tplparam          = {}
   _rendernl         = None
   loggedin          = False
   flash             = None
   routing           = None
   db                = None

   def __init__(self):
      """
      Initialsierung
      """

      try:
         self.version = '1.0'

         os.environ["PYTHONIOENCODING"] = "utf-8"
         myLocale=locale.setlocale(category=locale.LC_ALL, locale=self.settings.locale)

         self.createDirectories()
         self.setLogger()
         self.loadCgiParameter()
         self.setWinBinMode()
         self.logger.info('START: "{}"'.format(self.path)) 

         self.session         = Session(self.logger)
         self.routing         = Routing(self.logger,self.settings)
         
         self.currenttemplate = self.settings.defaulttemplate
         self.tplparam = {
            'BODY'            : '',
            'APPNAME'         : self.settings.appname,
            'PATH'            : self.path
            }
         self.connectDb()
      except Exception as ex:
         Emergency.stop(ex)

      
   def __del__(self):
      """
      Zerstoeren des Hauptobjektes
      """
      try:
         self.logger.info('END: "{}" wtc {}'.format(self.path,datetime.now() - self.startTime))      
      except: pass
          
   def setWinBinMode(self):
      """
      Wenn Windows, verhalten von binaeren Dateien verbessern.
      """
      try: # Windows needs stdio set for binary mode.
          import msvcrt
          msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
          msvcrt.setmode (1, os.O_BINARY) # stdout = 1          
          self.logger.debug("Windows found, set binary mode")
      except ImportError:
          pass      
      
   def createDirectories(self):
      """
      Erzeugen notwendige Verzeichnisse in Datastore wenn nicht vorhanden.
      """
      # -- LOG
      thepath = os.path.dirname(self.settings.logfile)
      distutils.dir_util.mkpath(thepath)

      # -- SESSION      
      thepath = self.settings.sessionpath
      distutils.dir_util.mkpath(thepath)

      # -- DATABASE
      thepath = self.settings.dbpath
      distutils.dir_util.mkpath(thepath)

   def writelog(self,*args):
      """
      Schreibt einen Fehlermeldung auf stderr
      """
      import sys
      print(' '.join([str(a) for a in args]),file=sys.stderr)

   def connectDb(self):
      """
      Verbinden mit Datenbank
      Wenn dbfilename angegeben
      """
      self.db           = Database('sqlite',self.settings.sqlitefilename)
      self.db.user      = self.session.getAttribute(self.settings.authenvar)
      self.db.settings  = self.settings
      self.db.logger    = self.logger
      self.db.cgiparam  = self.cgiparam
      self.db.writelog  = self.writelog
      

   def setLoggerOn(self,level=10):
      self.logger.setLevel(level)
      
   def setLoggerOff(self,level=20):
      self.logger.setLevel(level)

   def setLogger(self):
      """
      Definition logging
      """
      self.logger = logging.getLogger("")
      self.logger.setLevel(self.settings.loglevel)
      fh = logging.FileHandler(self.settings.logfile)
      formatter = logging.Formatter("%(asctime)s - %(levelname)-6s - %(process)08d:[%(module)s.%(funcName)s] %(message)s")
      fh.setFormatter(formatter)
      self.logger.addHandler(fh)
               
   def handleLogin(self):
      """
      Behandelt Anmeldeverfahren
      
      Es wird geprueft, ob schon ein Benutzer eingeloggt ist.
      Des erfogt durch das versuchte Lesen einer Sessionvariabel 
      (gewoehnlich "user") ist diese Vorhanden bzw. nicht Leer, gilt 
      der Benutzer als angemeldet.
      
      """
      aVar = self.session.getAttribute(self.settings.authenvar)
      self.loggedin = False
      if not aVar:
         self.currenttemplate = self.settings.logintemplate 
         self.logger.debug("Not logged in, Login-Mask activated.")
         return

      self.loggedin = True
      self.logger.debug('Loged in as: "{}"'.format(aVar))

   def setFlash(self,txt):
      """
      Setzen der Flashvariable
      Der Text in flash wird dem Template uebergeben ${FLASH} und kann
      wird dort angezeigt.
      
      @param   txt         Flash Text
      """
      self.flash = txt
      
      
   def getEntry(self,path=None,strict=True,secure=True):
      """
      Liefert einen Eintrag im Routingverzeihnis basierend auf Pfad
      
      @param   path        Pfad auf eintrag, 
                           wird keiener angegeben,so wird 
                           der aktuelle Pfad verwendet
      @param   strict      Vorgabewert gesetzt
                           wird False uebergeben, so wird kein
                           Fehler erzeugt, wenn nicht gefunden.
      @param   secure      Ueberprueft, ob beim Eitrag die 
                           Rechte ueberprueft werden soll.
                            
      """
      path = path or self.path
      inxEntry = self.routing.findEntry(path)
      entry = self.routing.entries[inxEntry]

      if strict and entry is None:
         
         sEntries = "Path-tree\n"+"\n".join([x.get('path','') for x in self.routing.entries])
         msg = 'Es konnte kein Routingeintrag "{}" gefunden werden.\n{}'.format(path,sEntries)
         self.logger.debug(msg)
         Emergency.stop(msg)

      # Wenn nicht eingeloggt keine Pruefung durchfuehren
      if self.loggedin:
         if secure and self.checkRights(entry):
            return entry
         else:
            Emergency.stop("Kein Recht, die Funktion {}/{} aufzurufen".format(entry.get('path'),entry.get('controller')))
      else:
         return entry
         

   def prepareController(self):
      """
      Vorbereiten des Controller.
      Abstrakte Methode, diese kann in options/mframe.py ueberschrieben 
      weden
      
      Setzen von Methoden und Vorgabewert
      
      HINT:
         Die Standards werden im creator des Controllers gesetzt.
         
      """
      pass      
      
   def checkRights(self,entry):
      """
      Prueft ob der Benutzer eines der uebergebene Rechte besitzt

      Die Pruefung unterbleibt wenn:
         * der Eintrag keinen Rechteeintrag hat
         * kein Loggin stattgefunden hat

      HINT:
         Es sind "negative" Rechte moeglich.
         ist in rights ein Recht mit einem vorlaufenden Minuszeit 
         behaftet z.B.: "-admin"  so wird falsch zurueckgeliefert,
         wenn das recht fuer den aktuellen Benutzer gefunden wird.

         Beispiel
            rights: develop,-admin
            userRights: "admin,user"
            Falsch da -admin in userRights vorhanden ist.
      """
      if not self.session.isLoggedin():
         self.logger.debug('Not logged in, we leave checkRights')
         return False
      
      # Ist Eintrag Public (z.B. Authen)
      if entry.get('public'):
         return True
         
         
      rights = entry.get('rights')
      
      if rights is None: 
         self.logger.debug('Rights are net set (None), we leave checkRights')
         return True

      self.logger.debug('Entryrights: {}'.format(repr(rights)))

      found = False
      userRights = self.session.getAttribute('rights')
      self.logger.debug('Userrights: {}'.format(repr(userRights)))

      # wurden Rechte gesetzt
      if rights is not None or rights==[]:
         if isinstance(rights,str): rights = rights.split(',')
            
         for right in rights:
            if right.startswith('-'):
               right = right[1:]
               if right in userRights: 
                  self.logger.debug('Negative righths found: {} is forbidden'.format(right))
                  return False
            else:
               if right in (userRights or []):
                  found = True         
      else:
         # Wenn keine Rechte im Eintrag
         # auf jeden Fall anzeigen
         found = True
      
      self.logger.debug('Result is "{}"'.format(found))
      return found

   def releaseController(self,entry):
      """
      Erzeugen des Controller,
      
      @param   entry          Routing Eintrags Object
      
      HINT:
         der Path wird nach Spezialfunktionen gescannt
         + *goback
            Muss im Entry eine Option redirekt haben.
            Es wird redirect auf den angegebnen Pfad durchgefuehrt
      """
      
      controllerName = entry.get('controller')
         
      if controllerName is None:
         self.logger.debug('Path: "{}" controller not decleared, we leave'.format(entry.get('path')))
         self.controller = Controller(self)
         return
        
      self.logger.debug("entrypath: {} controller: {}".format(entry.get('path'),controllerName))

      sControllerPath  = entry.get('path','').replace('/','.')
      sControllerPath = sControllerPath.lower()
      
      if sControllerPath.startswith('.'): sControllerPath = sControllerPath[1:]

      if sControllerPath == '':
         sControllerFile = 'mvc.controller.{}'.format(controllerName)
      else:
         sControllerFile = 'mvc.controller.{}.{}'.format(sControllerPath,controllerName)
         
      sControllerFile = self.settings.base+'/'+sControllerFile.replace('.','/')+'.py'
      sControllerFile = os.path.realpath(sControllerFile)
      
      if not os.path.isfile(sControllerFile):
         msg = 'Keinen Controller Datei {} gefunden'.format(sControllerFile)
         self.logger.debug(msg)
         self.content = msg
         Emergency.stop(msg)
         return

      if sControllerPath == '':
         sCommand = "from mvc.controller.{0} import {0}".format(controllerName)
      else:
         sCommand = "from mvc.controller.{0}.{1} import {1}".format(sControllerPath,controllerName)
      
      self.logger.debug('Import Controller over "{}"'.format(sCommand))
      try:
         exec(sCommand)
      except Exception as ex:
         msg = 'Fehler bei Import des Controller "{}": "{}"'.format(sCommand,ex)
         self.content = msg
         self.logger.debug(msg)
         Emergency.stop(msg)
      
      self.controller = None
      sCommand = "{}(self)".format(controllerName)
      self.logger.debug('Build controller by sentence: "{}"'.format(sCommand))

      try:
         self.controller = eval(sCommand)
      except Exception as ex:
         msg = 'Controller "{}" kann nicht initialiert werden; Meldung: "{}"'.format(sCommand,ex)
         self.content = msg
         self.logger.debug(msg)
         Emergency.stop(msg)

      
      self.prepareController()
      
      try:
         self.controller.get()
      except Exception as ex:
         msg = 'Fehler bei get() des Controller "{}": "{}"  Abbruch'.format(controllerName,ex)
         self.logger.debug(msg)
         self.logger.debug(self.content)
         self.controller.status == self.controller.FAILED
         Emergency.stop(msg)
               
   def work(self):
      """
      In der CGI Variable path wir der gewuenschte Pfad
      auf den Controller uebergeben. Diese wird ausgwertet und
      in der Routingtabelle nachgeschlagen.
      
      In der Routingtabelle wird der Controllername vermerkt und
      ausgefuehrt.
      """

      redirectDeep=self.settings.maxredirects
               
      # Redirect Loop 
      while FOREVER:
         entry = self.getEntry()

         for redirectcnt in range(0,redirectDeep-1):
            if entry.get('redirect') is None: break
            self.path = entry.get('redirect')
            entry = self.getEntry()
         else:
            Emergency.stop('Die Redirectfunktion durch Entry "{}" verursacht einen Zirkelbezug.'.format(self.path))

         self.logger.debug('Entry "{}" gefunden'.format(entry.get('path','-- not found --')))
                  
         # Wenn bei Controller kein Login notwendig
         if entry.get('public'):
            self.logger.debug('path "{}" ist public - keine Autentifizierung notwendig'.format(self.path))
         else:
            # Wenn noch nicht eingeloggt, dann loginmaske aufrufen
            self.handleLogin()
            if not self.loggedin:
               self.currenttemplate = self.settings.logintemplate 
               break
         self.logger.debug('We are goin to execute Controller "{}"'.format(entry.get('controller')))
         
         # absicherung gegen endlosloop
         redirectDeep -= 1
         self.logger.debug('Redirectid: "{}"'.format(redirectDeep))
         if redirectDeep < 1:
            self.logger.debug("Zu viele Redirects")
            Emergency.stop("Es sind zu viele Redirects hintereinader aufgerufen worden!")

         self.releaseController(entry)
         
         if self.controller.redirect is None:
            self.logger.debug('Controller is executed, no redirect found')
            break

         self.path = self.controller.redirect
         self.logger.debug('Redirect detected "{}"'.format(self.path))
         entry = self.getEntry()
      else:
         self.content += controller.content
               

   def render(self,value):
      """
      fuegt text dem Contentnbuffer hinzu
      
      @param   text        String mit inhalt
      
      """
      self.content += value
      if self._rendernl:
         self.content += self._rendernl
      
      
   @staticmethod
   def getCgiParameter(param,nvl=''):
      """
      Liefert den Inhalt eines CGI Parmeters basierend auf den QUERY_STRINGS

      @param   param    Name des CGI Parameters
      @param   nvl      Null-Value wird zurueckgeliefert, wenn der 
                        Parameter nicht vorhanden ist.
                        Vorgabewert ''

      HINT:
         Es wird nur das 1. Vorkommen des Parameters ausgewertet!

      """
      query_string = os.environ['QUERY_STRING']
      parsed = parse_qs(query_string)
      retval = parsed.get(param)
      if retval is None: 
         return None
      else:
         return retval[0]
   
   def loadCgiParameter(self):
      """
      Laed den Inhalt des CGI in Abhaengigkeit des Flags usecgi.

      usecgi
         True:    Es wird die Lib cgi verwendet
         False:   Es wird QUERY_STRING verwendet

      HINT:
         In bestimmten Situationen z.B. wenn im HTTP Body nur daten uebertragen werden.
         verhaelt sich das CGI Modul so, dass es einen Ausnahmebedingung wirft.
         Der Flag usecgi ermoeglicht das Abschalten des Moduls. Die CGI Parameter werden
         aus dem URL extrahiert und so verspeichert, dass sie mit der Methode cgiparam 
         wiedergewonnen werden koennen.

      """
      if self.usecgi:
         self.form=FieldStorage(keep_blank_values=1)
         self.path = self.cgiparam(name='path',nvl='/')
      else:
         # Form inhalte holen
         qs = self.query_string

         parsed = parse_qs(qs)
         self.form = dict()

         for key in parsed.keys():
            for val in parsed.get(key):
               self.form[key] = val
         try:
             self.path=parsed.get('path')[0]
         except: 
            self.form = {'path':'/root'}
                  
         self.path = self.cgiparam('path','/root')
      
   def getParsedQueryString(self):
      """
      Liefert den geparsten Query String
      """
      return cgi.parse_qs(self.query_string)
   
   def cgiparam(self,name=None,nvl='',noneifnotused=False):
      """
      Liefert aus dem CGI einen benannten Parameter

      @param   name     Name des Cgiparmeters
      @param   nvl      NullValue wird geliefert,
                        wenn der Parameter nicht uebergeben wurde

      HINT:
         Es wird geprueft, ob self.form ein Dict oder FieldStorage ist.
         Je nach Type wird der Inhalt geliefert.

      """      
      if self.form is None:
         self.logger.debug('Form not defined, nvl returnd')
         return nvl
      
      # Wurde Spezielle CGI Verarbeitung gewuenscht
      if isinstance(self.form,dict):
         return self.form.get(name,nvl)

      # wenn Parameter nicht definiert
      # null-value zurueckgeben
      if name not in self.form:
         if noneifnotused:
            return None
         else:
            return nvl

      value = self.form.getvalue(name)
            
      if value is None:
         value = nvl
      else:
         if isinstance(value,list):                 
            try:
               value = value[0]
            except: value = nvl

      auxValue = value if name != 'password' else '*' * len(value)
      self.logger.debug('Get from CGI: "{}"="{}"'.format(name,auxValue))

      return value

   def defaultTemplateParameter(self):
      """
      Setzen der Parameter fuer Templates
      """
      self.tplparam['BODY']                  = self.content
      self.tplparam['FLASH']                 = (self.flash or '').replace('"', r'\"')
      self.tplparam['PYMFRAMEVERSION']       = self.pymframeversion
      self.tplparam['USER']                  = self.session.getAttribute(self.settings.authenvar)
      self.tplparam['RIGHTS']                = repr(self.session.getAttribute('rights'))
      self.tplparam['MENU']                  = self.routing.getMenu(self.path,self.checkRights)
      self.tplparam['PATH']                  = self.path

   def setTemplateParameter(self,name,value):
      """
      Fuegt der Standard Parmeterliste einen Eintrag hinzug
      oder aendert diesen.
      
      @param   name        Name des Parameters
      @param   value       Inhalt
      """
      self.tplparam[name]  = value

   def disableGoback(self):
      """
      Deaktiviert den Zurueckbutton
      
      """
      self.routing.gobacktext = None
      
   #
   # ######## Core ROUTINES ############################################
   #
   def setup(self):
      """
      Initialisieren
      Abstrakte Methode, diese kann in options/mframe.py
      ueberschrieben werden
      """
      pass
   
   def onInit(self):
      """
      Abstrakte Mehtode wird in options/mframe.py aufgerufen
      """
      pass
   
   def afterWork(self):
      """
      Abstrakte Mehtode wird in options/mframe.py aufgerufen
      """
      pass
      
   def onDone(self):
      """
      Abstrakte Mehtode wird in options/mframe.py aufgerufen
      """
      pass
      
   def build(self):
      """
      Startet die Verarbeitung.
      
      @param   onInit      Hook bevor die Bearbeitung beginnt
      @param   onClose     Nachbearbeitung
      """
      self.logger.debug("run")

      self.onInit()
      self.work()
      
      self.afterWork()

      template = Templateengine(self.currenttemplate)
      template.readTemplateFile()
      contenttype = self.settings.contenttype      
      self.defaultTemplateParameter()
      
      try:
         self.content = template.get(self.tplparam)
      except Exception as ex:
         Emergency.stop(ex)

      self.onDone()
      
      self.logger.debug("done")

   def write(self):
      """
      Gibt den gesamten Response auf stdout aus
      """
      
      self.session.cookies['with_max_age'] = 'expires in {} minutes'.format(self.settings.sessionlifetime)
      sys.stdout.flush()
      sys.stdout.write(self.session.cookies.output(self.session.cookies))
      sys.stdout.write('\n')
      sys.stdout.write(self.settings.contenttype)
      sys.stdout.write('\n')
      sys.stdout.buffer.write(self.content.encode('utf-8'))
      sys.stdout.write('\n')
      sys.stdout.flush()
