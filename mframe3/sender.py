import os
import sys
import tempfile

class Sender(object):
   """
   Senden einer Datei
   """


   def __init__(self):
      # Spezielle Behandlung, wenn Binaere Daten unter Windows
      #
      if sys.platform == "win32":
         import msvcrt
         msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


   def sendfile (self,tmpFileName, fName,delete=False):
      fLength = os.path.getsize(tmpFileName)

      print ("Content-Type: application/octet-stream")
      print ('Content-Disposition: attachment;filename="{0}" '.format(fName))
      print ("Content-Length: {0}".format(fLength))
      print ('\n')
      sys.stdout.flush()
      with open(tmpFileName,'rb',buffering=0) as f:
         sys.stdout.buffer.write(f.read())
      sys.stdout.flush()
      exit()
      if delete:  
         try:
            os.unlink(tmpFileName)
         except Exception as e:
            raise Exception(e)
            
      return True
