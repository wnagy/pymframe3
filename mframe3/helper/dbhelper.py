
"""
Hilfsklasse zur Behandlung von Datenspeicherungen
"""
class Crud(object):

   id          = None
   controller  = None
   
   def __init__(self,controller,usedFields):
      self.id           = controller.cgiparam('id','')
      self.usedFields   = usedFields
      self.controller   = controller

   def delete(self,domain):
      pk = domain.meta['primarykey']
      currentUser = domain.db.user
      domain.get(where='{}=?'.format(pk),values=[self.id])
      domain.delete()
      if domain.isOk:
         msg = 'Datensatz wurde durch "{}" gelöscht'.format(currentUser)
         self.controller.logger.info(msg)
      else:
         Emergency.stop(msg)
      self.id = ''
      
   def save(self,domain):
      currentUser = domain.db.user
      pk = domain.meta['primarykey']
      domain.fromCgi(self.controller.cgiparam)
      if not domain.isOk:
         self.controller.setFlash('Speicherfehler {} (update)!'.format(repr(domain.errors)))
         return
         
      if domain.getValue(pk,'') == '':
         domain.insert()
         if domain.isOk:
            msg = 'Datensatz wurde durch "{}" angelegt'.format(currentUser)
            self.controller.logger.info(msg)
         else:
            self.controller.setFlash('Speicherfehler {} (insert)!'.format(str(domain.errors)))
      else:
         if self.usedFields is None:
            self.usedFields = domain.usesFields
         domain.update(usedFields=self.usedFields)

         if domain.isOk:
            msg = 'Datensatz wurde durch "{}" gespeichert'.format(currentUser)
            self.controller.logger.info(msg)
         else:
            self.controller.setFlash('Speicherfehler {} (update)!'.format(repr(domain.errors)))
            return False
      self.id = '0'
      self.id = ''


