# -*- coding: utf-8 -*- 
from config.settings       import Settings
from string                import Template
import sys

class Templateengine:
   template=''
   tplFileName = ''
   config = None

   def __init__(self,currenttemplate):

      self.tplFileName = currenttemplate
      self.readTemplateFile()
      
   def readTemplateFile(self):
      #print("content-type: text/plain\n\n!"+locale.getpreferredencoding());exit()
      with open(self.tplFileName,'r',encoding="utf-8") as fIn:
         buffer = fIn.read()

      self.template = Template(buffer)
   

   def get(self,map):
      return self.template.substitute(map)
      pass
