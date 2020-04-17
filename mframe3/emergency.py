"""
Notfall stop eines Programms.

Wird in absoluten Notfaellen bei schwerwiegenden und nicht
mehr reparierbaren Fehlverhalten ausgegeben.

Gibt Fehlermeldung (message) aus und beendet den Programmlauf.


"""

import sys, traceback
from config.settings          import Settings


class Emergency(object):
   
   @staticmethod 
   def stop(message,modul=None):
      """
      Fuehr eine Nothalt aus
      @param   message        Meldungstext.
      
      """
      sendMailOn  = Settings.senderroron
      
      exc_info = sys.exc_info()
      stack = ''.join(traceback.format_stack()[:-2])
      print ('content-type: text/plain\n\n')
      
      print ('Oups, dass sollte nicht passieren!')
      print ('----------------------------------\n')
         
      print ('Bitte sende den Inhalt dieses Bildschirms per Mail "{}" an den Entwickler dieser Anwendung'.format(sendMailOn))
      print ('\nMeldung:\n{}\n'.format(message))

      if modul is not None:
         print('Modul:\n{}'.format(modul))
         
      print()
      print (exc_info[1])
      print ("-" * 64)
      print (traceback.format_exc())
      exit()
