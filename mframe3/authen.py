from mframe3.pbkdf2     import crypt

class Authen(object):

   settings = None
   
   def __init__(self,settings,logger):
      self.settings  = settings
      self.logger    = logger
      
   def cleanPassword(self,password):
      """
      Entfernt aus password den Praefix "md5:{" und abschliesende "}"
                                   oder "pbkdf2:{" und abschliessende "}"
      
      @param      password       Passwort

      @return     bearbeitetes Passwort
      """
      if password is None: password = ''

      if password.startswith('md5:{'):
         if not password.startswith('md5:{') and password.endswith('}'):
            raise Exception("Ungueltiger Passwortstring: {0})".format(password))         
         password = password[5:]
         password = password[:-1]

      elif password.startswith('pbkdf2:{'):
         if not password.startswith('pbkdf2:{') and password.endswith('}'):
            raise Exception("Ungueltiger Passwortstring: {0})".format(password))
         password = password[8:]
         password = password[:-1]
      
      elif password.startswith('plain:{'):
         if not password.startswith('plain:{') and password.endswith('}'):
            raise Exception("Ungueltiger Passwortstring: {0})".format(password))
         password = password[7:]
         password = password[:-1]

      return password

   @staticmethod
   def giveReadablePassword():
      """
      Liefert ein Passwort bestehend aus zwei Worten (Buchstabiertabelle)
      gefolgt von einem Sonverzeichen und einer 4-Stelligen Zahl.

      """
      import random
      words = [
         'Alpha',
         'Bravo',
         'Charlie',
         'Delta',
         'Echo',
         'Foxtrot',
         'Golf',
         'Hotel',
         'India',
         'Juliet',
         'Kilo',
         'Lima',
         'Mike',
         'November',
         'Oscar',
         'Papa',
         'Quebec',
         'Romeo',
         'Sierra',
         'Tango',
         'Uniform',
         'Victor',
         'Whiskey',
         'Xray',
         'Yankee',
         'Zulu']

      chars = [
         '!',
         '#',
         '$',
         '%',
         '&',
         '*',
         '-',
         '.',
         ':',
         '?',
         '@'   
         ]


      random.seed()
      pw = ''
      pw += random.choice(words)
      pw += random.choice(words)
      pw += random.choice(chars)
      pw += "{:04d}".format(random.randint(0,10000))
      return pw


   def match(self,pwdmarked,password):
      """
      Vergleicht Passworte

      Es wird davon ausgangen, dass das 1. Passwort
      markiert ist z.B: pbkdf2:{. Diese Markierung
      wird entfernt.
      
      """
      pwd1 = self.cleanPassword(pwdmarked)
      pwd2 = self.cleanPassword(password)
      if not (pwdmarked or '').startswith('plain:{'):
         pwd2 = crypt(password,self.settings.authenSalt,10000)
      return pwd1==pwd2

   
   def encodepbkdf2(self,password):
      return crypt(password,self.settings.authenSalt,10000)
