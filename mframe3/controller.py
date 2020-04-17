"""
Basisklasse fuer die Behandlung eines Controllers
"""
from mframe3.emergency           import Emergency
from mframe3.template            import PSP
import os,sys

class Controller(object):
   FAILED         = 0
   OK             = 1
   CLOSED         = 2
   
   content        = ''
   settings       = None
   session        = None
   cgiparam       = None
   render         = None
   logger         = None
   redirect       = None
   isReadonly     = False
   status         = OK
   
   def __init__(self,core):
      self.core               = core
      self.path               = core.path
      self.settings           = core.settings
      self.session            = core.session
      self.cgiparam           = core.cgiparam
      self.render             = core.render
      self.logger             = core.logger
      self.setLoggerOn        = core.setLoggerOn
      self.setLoggerOff       = core.setLoggerOff
      self.setAttribute       = core.session.setAttribute
      self.getAttribute       = core.session.getAttribute
      self.removeSession      = core.session.removeSession
      self.routing            = core.routing
      self.setFlash           = core.setFlash
      self.writelog           = core.writelog
      self.disableGoback      = core.disableGoback
      self.goback             = core.routing.goback
      self.db                 = core.db
      self.content            = ''
      
      self.logger.debug('Inititat Controller "{}"'.format(self.__class__.__name__))

   def render(self,text):
      self.content += text
   
   def emergencystop(self,msg):
      Emergency.stop(msg,__file__)

   def view(self,filename,param=None,importcgi=False):
      """
      Aufrufen Viewer
      
      @param   filename          Filenamen des Viewer
      @param   param             Binding Variable fuer den 
                                 Viewer, welch dort verwenden werden koennen.
      @param   importcgi         Felder eine Form werden automatisch
                                 aus dem CGI befuellt

      @return     True|False     Je nach erfolgt
      """
      if filename.startswith('mvc://'):
         viewerfile = self.settings.mvcpath+'/controller/'+filename[6:]         

      elif filename.startswith('file://'):
         viewerfile = filename[7:]

      else:
         viewerfile = self.settings.mvcpath+'/controller/'+self.core.path+'/'+filename

      viewerfile = os.path.normpath(viewerfile.replace('\\','/'))            
      
      try:
         fViewer = open(viewerfile,'r')
         with open(viewerfile,'r',encoding="utf-8") as fViewer:
            text = fViewer.read()
            
      except Exception as e:
         Emergency.stop('Kann {} nicht finden: {}'.format(filename,e),__file__)

      self.logger.debug('Found File: "{}"'.format(viewerfile))


      try:
         psp = PSP(template=text,
                   filename=filename,
                   cgiparam=self.cgiparam,
                   isReadonly=self.isReadonly,
                   controller=self)
      except Exception as e:
         Emergency.stop('Fehler im Template: {} {}'.format(filename,e))

      # Importiert alle CGI Parameter in Param
      if importcgi:
         self.form=cgi.FieldStorage()
         for fld in self.form:
            param[fld]=self.form[fld].value
      value = ''
      
      value = psp.render(param)

      self.core.content += value
      return True
