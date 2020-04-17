# -*- coding: iso-8859-15 -*-

"""
Stellt einen Typensicherheitsmechanismus zur Verfuegung.

Diese Klasse wird ovn dbaccess.core verwendent

"""
from mframe3.dateconverter       import Dateconverter


class Checktype():
   """
   Es werden folgende Typen ueberprueft:

      + String
      + Integer
      + Float, Double
      + Date (Basiierend auf dem Dateconvertert Objekt)
      + email
   """

   def isString(self,value):
      """
      Pruefen ob der uebergene Wert ein String ist.

      @param   value

      @return [True|False] 
      """
      return isinstance(value,str)

   def isInteger(self,value):
      """
      Pruefen ob der uebergene Wert ein Integer ist.

      @param   value

      @return [True|False] 
      """
      return isinstance(value,int)

   def isLong(self,value):
      """
      Pruefen ob der uebergene Wert ein Long ist.

      @param   value

      @return [True|False] 
      """
      return isinstance(value,long)

   def isFloat(self,value):
      """
      Pruefen ob der uebergene Wert ein Float ist.

      @param   value

      @return [True|False] 
      """
      return isinstance(value,float)

   def isDate(self,value):
      """
      Pruefen auf gueltiges Datum vorhanden ist dies geschieht durch die Klasse Dateconverter

      @param   value

      @return [True|False] 
      """
      dc = Dateconverter()
      value = value.replace(',','.')
      value = value.replace('*',' ')
      
      try:
         dc.fromString(value)
      except:
         return False
      return True


   #
   def isEmail(self,a):
      """
      MINI emailadressencheck
      basierend auf http://www.daniweb.com/code/snippet280071.html

      @param   value

      @return [True|False] 
      """

      if not self.isString(a):
         return False

      sep=[x for x in a if not x.isalpha()]
      sepjoined=''.join(sep)
      if sepjoined.strip('.') != '@':
         return False
      end=a
      for i in sep:
         part,i,end=end.partition(i)
         if len(part)<2:
           return False
      return True
