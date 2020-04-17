# -*- coding: utf-8 -*-
import re
import time
import datetime

class Dateconverter():
   """
   Die Klasse Dateconverter konvertier Datumseintraege von und nach ASCII

   """


   format = None              # Formatstring
   timestamp = None           # Hilfsfeld fuer aktuelles Datum und Zeit

   def validDate(self,value,format):
      """
      Prueft ob ein uebergebenes Datum dem Format entspricht
      @param   value    Datumswert
      @param   formt    Formatstring

      @return  [True|False]
      """
      self.format = format
      try:
         self.timestamp = time.strptime(value, format)
      except:
         return False

      return True


   def _getANSI(self,secs=False):
      """
      Liefert eine Ausgabe eines Timestamps im ISO Format

      @param   secs   [True|False] Bei True werden die Sekunden mit ausgegeben
      """
      result = datetime.datetime(self.timestamp[0],
                                 self.timestamp[1],
                                 self.timestamp[2],
                                 self.timestamp[3],
                                 self.timestamp[4],
                                 self.timestamp[5]).isoformat()

      
      if not secs:
         result = result[0:16]

      return result

   def fromString(self,value):
      """
      Aus einem String wird ein ANSI Datum generiert
      Tritt ein Fehler auf, wird ein TypeError geworfen.

      Die Ausgabe erfolgt im ANSI/ISO Format.
      Werden beim Imputstring Sekunden angegeben, wird dies
      bei der Ausgabe beachtet sonst werden nur bis zur Minute ausgegeben.

      @param   value       Datumswert

      @return  Datums als ISO/ANSI Foramt
      """

      isOk = False
      secs = False

      
      if isinstance(value,str):
         value = value.strip()
         value = value.replace(',','.')
      
      if re.match('\d{1,2}\.\d{1,2}\.\d{1,4}$',value):
         if self.validDate(value, '%d.%m.%Y'):
            isOk = True

      elif re.match('\d{4}\-\d{2}\-\d{2}$',value):
         if self.validDate (value, '%Y-%m-%d'):
            isOk = True

      elif re.match('\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}$',value):
         if self.validDate (value, '%Y-%m-%dT%H:%M'):
            isOk = True

      elif re.match('\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}$',value):         
         if self.validDate (value, '%Y-%m-%dT%H:%M:%S'):
            secs = True
            isOk = True
         
      elif re.match('\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}$',value):
         if self.validDate (value, '%Y-%m-%d %H:%M'):
            isOk = True
      
      elif re.match('\d{1,2}\.\d{1,2}\.\d{1,4} \d{2}:\d{2}$',value):
         if self.validDate(value, '%d.%m.%Y %H:%M'):
            isOk = True

      elif re.match('\d{1,2}\.\d{1,2}\.\d{1,4} \d{2}.\d{2}$',value):
         if self.validDate(value, '%d.%m.%Y %H.%M'):
            isOk = True

      elif re.match('\d{1,2}\.\d{1,2}\.\d{1,4} \d{2}:\d{2}:\d{2}$',value):
         secs = True
         if self.validDate(value, '%d.%m.%Y %H:%M:%S'):
            isOk = True

      elif re.match('\d{1,2}\.\d{1,2}\.\d{1,4} \d{2}:\d{2}:\d{2}\.\d{3}$',value):
         secs = True
         if self.validDate(value, '%d.%m.%Y %H:%M:%S'):
            isOk = True

      elif re.match('\d{4}-\d{1,2}-\d{2} \d{2}:\d{2}:\d{2}$',value):
         secs = True
         if self.validDate(value, '%Y-%m-%d %H:%M:%S'):
            isOk = True

      if not isOk:
         raise TypeError("'%(value)s' ist kein gueltiges Datum. Format %(format)s" % {'value':value,'format':self.format})

      return self._getANSI(secs=secs)

   def clear(self):
      """Loescht timestamp """
      self.timestamp = None


   def initTimestamp(self,value=None):
      """Initialisiert Timestamp

         @param  value       Datum als Zeichenkette
                             wirft Exception wenn
                             value und timestamp None

         HINT:
            Wird als Uebergabewert 'now' oder 'jetzt' eingegeben
            wird das aktelle Datum angenommen.
         """
      
      if value is None:
         self.timestamp = None
         return

      if isinstance(value,str):
         value = value.strip()
         value = value.replace(',','.')

      
      # Wenn aktuelles Datum gewuenscht
      if value in ['now','jetzt']:
         now = time.localtime()
         value = time.strftime('%d.%m.%Y %H:%M:%S',now)
         
      
      if value is not None:
         retval = self.fromString(str(value))
         
         
      else:
         if self.timestamp is None:
            raise ValueError('Es wurde kein Datum initialisiert')

   def giveAsANSIDate(self,value=None,secs=False,nvl=None):
      """Liefert das aktuelle Datum als ANSI Datum
         optional koennen die Sekunden mit ausgegeben werden
         """
      self.initTimestamp(value)
      if self.timestamp is None: return nvl

      result = self._getANSI(secs=False)      
      return result[0:10]


   def giveAsANSIDateTime(self,value=None,secs=False,nvl=None):
      """Liefert das aktuelle Datum als ANSI Datum und Zeit
         optional koennen die Sekunden mit ausgegeben werden
         """
      self.initTimestamp(value)
      if self.timestamp is None: return nvl

      result = self._getANSI(secs=secs)
      return result

   def giveAsGermanDate(self,value=None,format=None,nvl=None):
      """Liefert das aktuelle Datum als ANSI Datum und Zeit
         optional koennen die Sekunden mit ausgegeben werden
         @param value      Wert
         @param format     Datumformat Vorgabewert %d.%m.%Y
         @param nvl        Defaultwert: ist value None wird dieser Wert eingesetzt
                           der Wert now gibt das aktuelle Datum
         """

      self.initTimestamp(value)
      if self.timestamp is None: return nvl

      if format is None:
         format = '%d.%m.%Y'
      if self.timestamp is None:
         result = value
      else:
         result = time.strftime(format,self.timestamp)

      return result


   def giveAsGermanDateTime(self,value=None,secs=False,nvl=None):
      """Liefert das aktuelle Datum als ANSI Datum und Zeit
         optional koennen die Sekunden mit ausgegeben werden
         """
      self.initTimestamp(value)
      if self.timestamp is None: return nvl
      if secs:
         result = time.strftime('%d.%m.%Y %H:%M:%S',self.timestamp)
      else:
         result = time.strftime('%d.%m.%Y %H:%M',self.timestamp)
      return result

   def giveAsTime(self,value=None,secs=False,nvl=None):
      """Liefert das aktuelle Datum als ANSI Datum und Zeit
         optional koennen die Sekunden mit ausgegeben werden
         """
      self.initTimestamp(value)
      if self.timestamp is None: return nvl
      if secs:
         result = time.strftime('%H:%M:%S',self.timestamp)
      else:
         result = time.strftime('%H:%M',self.timestamp)
      return result

if __name__ == '__main__':
   print ("-- T E S T --")
   dc = Dateconverter()
   assert (dc.fromString('1.1.2012')=='2012-01-01T00:00')
   dc.initTimestamp()
   assert dc.giveAsGermanDate('now',nvl='') != ''

   dc.initTimestamp()
   assert dc.fromString('2011-01-01 12:31') == '2011-01-01T12:31'

   dt = dc.fromString('1.1.2011 12:31')
   assert dc.giveAsANSIDateTime(dt) == '2011-01-01T12:31'
   print (dc.giveAsANSIDate('now'))
   assert dc.giveAsGermanDateTime(dc.fromString('2011-01-01 12:31')) == '01.01.2011 12:31'

   print ('all tests well done')

