import base64
from Crypto.Cipher import AES
import urllib.parse


class Crypto(object):
   salt = '9e33820b15d24391'
   
   @staticmethod
   def encrypt(text,pwd,urlencoded=False):
      pwd = pwd.ljust(16,'\n')
      while len(pwd) % 8 != 0: pwd=pwd+'\x00'
         
      obj = AES.new(pwd, AES.MODE_CFB, Crypto.salt)
      ciphertext = obj.encrypt(text)
      b64 =  base64.b64encode(ciphertext)
      b64 = b64.decode('utf-8')
      if urlencoded:
         return urllib.parse.quote_plus(b64)
      else:
         return b64

      
   @staticmethod
   def decrypt(text,pwd,urldecoded=False):
      pwd = pwd.ljust(16,'\n')
      while len(pwd) % 8 != 0: pwd=pwd+'\x00'

      
      if urldecoded:
         crypted = urllib.parse.unquote(text)
      else:
         crypted = text
         
      text = base64.b64decode(crypted)
      obj = AES.new(pwd, AES.MODE_CFB, Crypto.salt)
      dc = obj.decrypt(text)
      return dc.decode("utf-8") 


if __name__ == '__main__':

   pwd = '123456793'
   message = 'das ist irgendein lager text'
   
   crypted = Crypto.encrypt(message,pwd,True)
   print (crypted)

   text = Crypto.decrypt(crypted,pwd,True)
   print(text)

   #print(ct)
   #ue = urllib.parse.quote_plus(ct)
   #ct = (urllib.parse.unquote(ue))
   #print ('"{}"'.format(Crypto.decrypt(ct,pwd)))
