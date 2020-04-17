# -*- coding: utf-8 -*-
import os
import json
from mframe3.emergency        import Emergency
from options.taglib           import Taglib

class Routing(object):
   
   entries = []

   gobacktext      = None
   
   def __init__(self,logger,settings):
      self.logger       = logger
      self.settings     = settings
      self.gobacktext   = self.settings.gobacktext
      self.gobackhtml   = self.settings.gobackhtml

   def getParentePath(self,path):
      """
      Liefert den Pfad auf vorhergenden Eintrag.

      @param   path        Pfad
      """
      retval = '/'
      if path != '/':
         retval = os.path.dirname(path)
      return retval
      
   def getEntry(self,path):
      """
      Liefert ein Dict mit dem Uebergebenen
      Pfad.
      Kann der Eintrag nicht gefunden werden, so wird
      None retourniert.
      
      @return Entry 
      """
      for entry in self.entries:
         if entry.get('path','') == path:
            return entry
      return None

   def displayEntry(self,path,ident=None):
      """
      Liefert einen String mit einer JSON repraesentation
      eines Eintrags

      @param   path     Pfad auf Eintrag
      @return  Eintrag in Json
      
      """
      allEntries = list()
      if path is None:
         for entry in self.entries:
            allEntries.append(json.dumps(entry,indent=ident))
         retval = '\n'.join(allEntries)
      else:
         entry = self.getEntry(path)
         retval = json.dumps(entry,indent=ident)
      return retval
   
   def getParentEntry(self,path):
      """
      Liefert den Eintrag des Elterneintrags in der Routingtabelle
      oder None, wenn dieser nicht erreichbar ist.
      
      @param   path           current Path
      
      """
      if path == '/': return None

      curPath = os.path.dirname(path)
      entry = self.getEntry(curPath)
      return entry

   def addEntry(self,path,**kwargs):
      """
      Fuegt einen Eintrag in die Routingtabelle an
      """
      if kwargs is None:
         self.logger.debug("No arguments, we leave...")
         return
         
      auxEntry = {
         'path':path
         }
      
      for key, value in kwargs.items():
         auxEntry[key] = value      
      self.logger.debug('{}'.format(repr(auxEntry)))

      self.entries.append(auxEntry)

   def findEntry(self,path):
      """
      Liefert den Index (oder None) auf einen Eintrag in 
      der Routingtabelle.
      
      @param   path     Kenung des Eintrags
      
      @return  Index oder None
      """
      retval = None
      inxEntry = 0
      for entry in self.entries:

         if entry.get('path') == path:
            retval = inxEntry
            break
         inxEntry+=1

      if retval is None:
         sPath = '\n'.join([x.get('path') for x in self.entries])
         Emergency.stop('[{}] Kann keinen Eintrag auf "{}" finden. {}'.format(__name__,path,sPath)) 

      return retval

   def changeEntry(self,path,**kwargs):
      """
      Aendern einen Eintrags in der Routingtabelle
      
      @param   path              Kennung
      
      """   
      if kwargs is None:
         self.logger.debug("No arguments, we leave...")
         return
         
      inxEntry =  self.findEntry(path)

      for key, value in kwargs.items():
         self.entries[inxEntry][key] = value
         self.logger.debug('[{}] {}="{}"'.format(path,key,value))
   
      return

   def goback(self,path,message=None,url=None):
      """
      Ersetzt den Zurueckbutton

      @param   path           Pfadangabe
      @param   message        Anzeigetext
                              wenn nicht uebergeben, wird
                              Standardtext verwendet
      @param   url            URL zum anspringen
                              wenn nicht deklariert, wird
                              der Pfad verwendet
      
      """
      self.gobacktext = None
      theUrl = '?path='+path
      if url is not None:
         theUrl=url
         
      self.addEntry(
         path+'/back',
          text=message or self.settings.gobacktext,
          url=theUrl)
      
   def writelog(self,*args):
      """
      Schreibt einen Fehlermeldung auf stderr
      """
      import sys
      print(' '.join([str(a) for a in args]),file=sys.stderr)

   def getMenu(self,path,checkRights):
      """
      Gibt das Menu formartiert aus.
      
      
      """
      
      self.lstEntries = list()
      curPath = path
      for entry in self.entries:
         
         if entry.get('path') != '/':
            try:
               ePath = os.path.dirname(entry.get('path'))
            except Exception as ex:
               pass
               #Emergency.stop("Fehler beim Ausgeben des Menu entry-path:{} Meldung:{}".format(entry.get('path'),ex),__file__)
         else:
            ePath = entry.get('path')
            
         self.logger.debug('Path: {} Check if menuentry "{}" == "{}" = {}'.format(entry.get('path'),ePath,curPath,curPath == ePath))

         if curPath == ePath:
            if checkRights(entry):
               self.lstEntries.append(entry)
               self.logger.debug('Add entry  "{}" to Menulist'.format(entry.get('path')))
         
      lstItems = list()

      for entry in self.lstEntries:
         display = True if (entry.get('display') or True) and entry.get('text') is not None else False
         sOptions = ''
         self.logger.debug('Path: "{}" display: {}'.format(entry.get('path'),display))

         if display:
            html = entry.get('html',{})
            options = list()
            for option in ['id','class','style','title']:
               value = html.get(option,'')
               if value is not None:
                  options.append('{}="{}"'.format(option,value))
            sOptions = ' '.join(options)

            if entry.get('url') is None:
               item = Taglib.button(
                      entry.get('text'),
                      '?path={}'.format(entry.get('path')),
                      form=True,
                      options=html)
            else:
               item = Taglib.button(
                      entry.get('text'),
                      entry.get('url'),
                      form=True,
                      options=html)
               
            lstItems.append(item)   
      
      if self.gobacktext is not None:
         retpath = self.getParentePath(path)
         if path != '/':
            item = Taglib.button(
                   self.gobacktext,
                   '?path={}'.format(retpath),
                   True,
                   self.gobackhtml)
            lstItems.append(item)   
      
      retval = ''.join(lstItems)
      self.logger.debug('Created Menu: "{}"'.format(retval))
      return retval
