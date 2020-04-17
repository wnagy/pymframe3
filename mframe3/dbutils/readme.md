# H I N T E R G R U N D

Dient zur Verbindung der Domain mit einer Datenbanktabelle

Eine Domain enthaelt
 + Die Felder welche von der Datenbanktabelle
   verwaltet werden sollen. Es ist nicht notwendig
   alle Felder zu deklarieren.
 + Eine Datenstruktur (metah) welche die Datenbanktabelle
   beschreibt und eine Verbindug zu den Domainfeldern deklariert.
 + Optional noch Methoden, welche zur Behandlung von Daten oder
   die Bereitstellung von ORM Methoden ermoeglichen.
 + HANDLER
     Handler liefern [True|False] Zurueck.
     Bei False wird die Datenbankaktion abgebrochen

Fehlermeldungen koennen mit self.addError("Meldung")
angegben werden.

## Typensichere Zuweisung

   Die Domain sichert sich gegen fehlerhafte Datentypenzuweisungen
   ab. Basierend auf den Angaben in der Mehtadaten Datenstruktur wird
   geprueft, ob die zugewiesene Datentypen den Datentypen in der Datenbanktabelle entsprechen.

# W E S E N T L I C H E   M E T H O D E N

## insert

fuegt die Daten der Domai in die Datenbank ein.
   
Beispiel:

     loc.clear()                 # Loeschen der Datenfelder der Domain
     lov.lovClass = 'Test'       # Befuellen
     lov.lovKey = '123'          # - " -
     lov.insert()                # In die Datenbank schreiben

## update

Aendert die Daten einer Datenbantabelle mit den in der Domain gespeicherten Daten.

Beipiel:

      lov.get(12)                # Hole die Daten aus der Tabelle in die Domain

      lov.lovClass = 'TEST'      # Aender
      lov.update()               # in die Datebank schreiben

## delete

Loescht einen Datenbankeintrag basieren auf den in der Domain abgelegten Primary Key
   
Beipiel:
   
      lov.get(13)                # Hole Datensatz
      lov.delete()               # Loesche den Datensatz aus Tabelle7

## get

Liest die Daten aus der Datenbank und kopiert diese in die Felder der Domain.

Beispiel:

      lov.get(where="lovKey = 'test' and lovClass = 'TEST'")
      if lov.isOK:
         print lov.lovID
      else:
         print 'Nicht gefunden'

# eachDomain

Serialisert die Domain. Basierend auf den Parametern werden alle oder 
eine Auswahl von Datensaetzen der Datenbankstabelle
wird bereitgestellt.

Die einfachste Form als Beispiel:

      for l  in lov.eachDoamin():
         print l.lovKey

## where
   
Where Klause
Es kann entwede der original Tabellen Feldnamen oder
der Domain Feldnamen mit vorangestellten Dollarzeichen ($) verwendet werden.

## orderby

Order by Klausel
Es koennen entwede der original Tabellen Feldnamen oder
der Domain Feldnamen mit vorangestellten Dollarzeichen ($) verwendet werden.

## limit
   
Kann ein Integer oder ein Tupple sein
Wenn Integer wird maximal die Anzahl der genannten
Datensaetze ausgegeben
Bei einem Tupple wird vom angegebenen bis maximal
bis zur angegeben Anzahl der Datensaetze ausgegeben.

## filter
sucht in allen Datenbankfeldern nach dem
uebergenen Wert.

Ist Filter ein Dictionary koennen speziellere
Einstellungen vorgenommen werden.
Filter kann mit where kombiniert werden um das Suchergebnis weiter einzuschraenken.

Beispiele:
      
     filter='Mayer'
  
es wird in allen Feldern nach dem Vorkommen 'Mayer' gesucht

    filter={'value':'Mayer',exclude=['PERSON_ID','GEHALT']}

Es wird in allen Feldern bis aus die Angegeben nach dem Filter gesucht
   
    filter={'value':'100',include=['$personID','$gehalt']}

es wird zuerst eine Ueberseetzung in Tabellenfeldnamen vogenommen und
nur in den angegebenen Feldern gesucht.
