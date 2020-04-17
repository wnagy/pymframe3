#
# CONFIG BASE
#
# Basiskonfigurationen wird von Applikationseigenen Config uerberschrieben
#
#
import logging
import os
from datetime                 import datetime

class Settings(object):

   # ### Definition der Pfade auf Bibliothken
   webserver = os.environ.get('SERVER_SOFTWARE','')

   appname              = '«PYMFRAME»'
   cwd                  = os.path.dirname(os.getcwd())
   utcdate              = str(datetime.utcnow())
   locale               = "de_AT.UTF-8"
   # Pfade
   if webserver.startswith('SimpleHTTP'):
      base  = './WEB-INF'
   elif webserver.startswith('Apache'):
      base  = cwd+'/WEB-INF'


   datastore            = base+'/datastore'
   mvcpath              = base+'/mvc'

   logpath              = datastore+'/log/access/'+utcdate[:4].replace('-','/')
   logfile              = '{}/pymframe3.log'.format(logpath)

   sessionpath          = '{}/session'.format(datastore)

   # Allgemeines
   homeurl              = "cgi-bin/start.py"
   loglevel             = logging.INFO
   sessionlifetime      = 180 # In Minuten
   authenvar            = 'user' # Variable in Session, welch gefuellt sein muss, wenn angemeldet
   contenttype          = 'Content-Type: text/html\n\n'
   maxredirects         = 4   # maximale tiefe fuer redirects
   senderroron          = 'name@mail.xxx'
   authenpath           = '/authen' # Pfad der Anmelderetourne

   gobacktext           = '&nbsp;<i class="fa fa-arrow-circle-left" title="Schritt zurück">&nbsp;</i>'  # Text fuer Zurueckbutton
   gobackpath           = '/*GOBACK*'

   # -- TEMPLATE-SECTION --

   templatepath         = base+'/templates'
   defaulttemplate      = templatepath+'/default.tpl'
   logintemplate        = templatepath+'/login.tpl'
   
   
   # -- DATENBANK --
   dbtype               = 'sqlite'
   dbpath               = '{}/database'.format(datastore)
   sqlitefilename       = '{}/database.db3'.format(dbpath)
   # Feldersetzung in database.core werden die
   # Beginn- und Endkennungen gesetzt
   # Default sind
   # Beginn mit '$' und keine Endkennung
   # Bsp: $Domainfield --> DDLFeld
   #
   SqlConverter_fieldBegin    = '$'
   SqlConverter_fieldEnd      = ''


   # Authen
   authenMethod         = 'pbkdf2'
   authenSalt           = '3a7100f48b9e4156b369d265175a1fe1'
   
   # Text
   gespeichert          = 'gespeichert'
   geloescht            = 'gelöscht'
   eingefuegt           = 'eingefügt'
