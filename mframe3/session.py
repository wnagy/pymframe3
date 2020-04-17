f"""
Sessionhandling

Die Session wird durch einen Sessionid (UUID) gekennzeichnet.
Die ID ist equivalent mit einem Dateinamen. Die Sessionid wird
mittels Coockies persistent gemacht.

Die Datai enthaelt ein JSON Objekt in den die Attribute gespeichert werden.

"""
import uuid
import json
import os,sys

from config.settings    import Settings
from datetime           import datetime, timedelta, time
from mframe3.emergency  import Emergency

from http               import cookies as Cookies

class Session(object):
   config         = Settings()
   sid            = None
   cookies        = None
   logger         = None
   sFilename      = None
   attributes     = None

   # Liefert ein Cookie oder None wenn nicht vorhanden
   getCookie = lambda self,c : \
      self.cookies.get(c).value if self.cookies.get(c) is not None \
      else None


   def __init__(self,logger):
      # Ist Cookie SID vorhanden?
      #
      # @param logger      Loggerobjekt
      #
      self.logger       = logger
      webserver = os.environ.get('SERVER_SOFTWARE','')
                  
      self.cookies = Cookies.SimpleCookie(os.environ.get('HTTP_COOKIE',''))
      self.sid = self.getCookie('sid')
      
      if self.sid is None:
         self.sid          = str(uuid.uuid4())
         self.logger.debug('No Cookie sid, create it sid={}'.format(self.sid))
      else:
         self.logger.debug('Found cookie sid={}'.format(self.sid))
      self.removeZoobies()
      
      self.sFilename    = "{}/{}.ses".format(self.config.sessionpath,self.sid)

      self.logger.debug('SFile: "{}"'.format(self.sFilename))
      
      # erzeugen Sessionfile wenn nicht vorhanden
      if not os.path.isfile(self.sFilename):
         with open(self.sFilename,'w') as fSession:
            self.attributes = dict()
            self.attributes['sid'] = self.sid

            json.dump(self.attributes,fSession)
            self.logger.debug("Create empty sessionfile {}".format(self.sFilename))


      # Hole Attribute      
      with open(self.sFilename,'r') as fSession:
         self.attributes = json.load(fSession)


      if self.sid != self.getAttribute('sid'):
         Emergency.stop('Session ID is not equal cookie-id')

      self.cookies['sid'] = self.sid
      self.logger.debug("Attributes: {}".format(json.dumps(self.attributes)))

   def isLoggedin(self):
      """
      Testet ob schon ein login stattgefunden hat.
      
      Dies ist gegeben, wenn das Attribute (normalerweise "user")
      gesetzt worden ist.
      
      """
      retval = self.getAttribute(self.config.authenvar)
      return retval 
      
      
   def removeZoobies(self):
      """
      Loeschen aller Sessionfiels, deren Lebenszeit abgelaufen ist
      Die Lebenszeit wird aus Config entnommen
      """
      path = self.config.sessionpath
      lifetime = self.config.sessionlifetime
      erasedate = datetime.now()-timedelta(minutes=lifetime)
      self.logger.debug("Lifetime:{} Erasedate:{}".format(lifetime,erasedate))
      
      # Alle Dateien pruefen
      for sFile in os.listdir(path):
         sFile = os.path.join(path,sFile)
         if not os.path.isfile(sFile): continue
         fn, ext = os.path.splitext(sFile)
         if not ext.startswith('.ses'):  continue

         # Dateizeit
         fdt =  datetime.fromtimestamp(os.stat(sFile).st_mtime)

         # Pruefen ob zu loeschen
         if fdt < erasedate:
            os.remove(sFile)
            self.logger.debug("Remove Sessionfile: {} {} {}".format(sFile,fdt,erasedate))

   def removeSession(self):
      """
      Entfernt akutelle Session
      """
      if self.sid is None: return
      sFilename    = "{}/{}.ses".format(self.config.sessionpath,self.sid)
      if os.path.isfile(self.sFilename):
         os.remove(sFilename)
         self.sFilename = None
         self.attributes['user']=''
         self.attributes['sid']=''
         self.logger.debug('Remove sessionfile "{}"'.format(sFilename))

      
   def setAttribute(self,aname,avalue):
      """
      Setzen von Cookie Attribute
      """
      #with open(self.sFilename,'r') as fSession:
      #   self.attributes = json.load(fSession)

      self.attributes[aname] = avalue

      with open(self.sFilename,'w') as fSession:
         json.dump(self.attributes,fSession)

      self.logger.debug('Set Sessionattribute {}="{}"'.format(aname,avalue))

   def getAttribute(self,aname):
      """
      Liefert den Inhalt eines Attributes 
      von Session
      
      @param   aname       Name des Attributes
      
      @return  Attribute oder None
      """
      
      # Wenn keine Attribute dann Session nachladen
      if not isinstance(self.attributes,dict):
         with open(self.sFilename,'r') as fSession:
            self.attributes = json.load(fSession)

      self.logger.debug('Get Sessionattribute {}="{}"'.format(aname,self.attributes.get(aname,'')))

      return self.attributes.get(aname,None)
                  
   @staticmethod
   def purge(self):
      """
      Loescht alle Sessionfiels
      """
      for sFile in os.scandir(self.config.sessionpath):
         if os.path.isfile(sFile):
            os.remove(sFile)
      self.logger.debug("removed sessionfiles in {self.config.sessionpath}")
            
   
