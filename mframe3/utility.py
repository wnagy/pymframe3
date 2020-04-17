from mframe3.dateconverter          import Dateconverter

class Utility(object):
   """
   Beinhaltet allgemeine Hilfsroutinen
   """

   @staticmethod
   def formatNumber(num):
      if isinstance(num, (int, float)):
         if isinstance(num, float):
            head, tail = str(num).split('.')
         elif isinstance(num, int):
            head, tail = str(num), ''
         digit_parts = re.findall(r'\d{1,3}\-?', ''.join(head[::-1]))
         num = '.'.join(part[::-1] for part in digit_parts[::-1])
         if tail:
            if len(tail) < 2: tail += '0'
            num = ','.join((num, tail))
         return num
      else:
         return num

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
