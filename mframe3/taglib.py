#
# Basale Taglib
#
import re
class Taglib(object):
         
   @staticmethod
   def table(options={}):
      """
      Liefert den Beginn einer HTML Tabelle

      @param   options     Tag Opionen
         
      """
      options = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))
      return '<table {}>'.format(options)      

   def endtable():
      return '</table>'

   @staticmethod
   def form(options={}):
      """
      Liefert den Beginn einer HTML Form.
      HINT:
         Standardmaessig wird die Methode post verwendet

      @param   options        HTML Optionen
      """
      if options.get('method') is None: options['method'] = 'post'
      options = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))
      
      
      return '<form {}>'.format(options)      

   def endform():
      return '</form>'

   @staticmethod
   def hidden(name,value,display=False):
      """
      Liefert ein hidden Feld

      @param   name        Feldname
      @param   value       Inhalt
      @param   display     wird True uebergeben, so wird
                           der Inhalt von value an das HTML Feld
                           angefuegt
      
      """
      if display:
         return '<input type="hidden" name="{0}" value="{1}"/>{1}'.format(name,value)
      else:
         return '<input type="hidden" name="{}" value="{}"/>'.format(name,value)

   @staticmethod
   def displayandhidden(name,value,options={}):
      """
      Liefert ein hidden Feld und den Inhalt des Valueparameters
      in span-tags eingerahmt.

      @param   name        Feldname
      @param   value       Inhalt
      @param   display     wird True uebergeben, so wird
                           der Inhalt von value an das HTML Feld
                           angefuegt

      """

      options      = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))
      return '<input type="hidden" name="{0}" value="{1}"/><span {2}>{1}</span>'.format(name,value,options)
      
   @staticmethod
   def getRow(domain,fields=None,nvl='',onBegin=None,onEnd=None,options={}):
      """
      Liefert eine Datenzeile basieren auf einer Domain
      Es koennen Hooks mitgegeben werden.

      @parma   domain      Domain- oder list Objekt
                           wird eine Liste uebergeben, so werden
                           die Elemente ausgegeben.
                           Wird eine Domain uebergeben, so werden
                           die Inhalte der Doamain ausgegeben. Die
                           Feldmenge kann durch fields eingeschraenktw
                           werden
      @param   fields      List der Datenfelder, welche angezeigt werden
                           sollen. Bein None werden alle verwendet.
                           Wirk nur im Fall dass Domain kein list Objekt
                           ist.
      @param   nvl         NULL Value. Wird ausgegeben, wenn None
                           aus der Domain geliefert wird.
                           Vorgabewert ist Leerzeichen.
      @param   onBeginn    Eine Funktion die einen Text liefert.
                           Dieser wird am beginn der Datenzeile angezeigt.
      @param   onEnd       Eine Funktion die einen Text liefert.
                           Dieser wird am Ende der Datenzeile angezeigt
      @param   options     Ein Dictionary mit optionen fuer den td Tag.
                           
      """

      isList = isinstance(domain, (list,))
      
      lstTD       = list()
      sBegin      = '<td>'+onBegin(domain)+'</td>' if onBegin is not None else ''
      sEnd        = '<td>'+onEnd(domain)+'</td>' if onEnd is not None else ''

      options      = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))

      if isList:
         for element in domain:
            lstTD.append('<td {}>{}</td>'.format(options,element))
      else:
         lstFields = fields or domain.getDomainFieldnames()
         for fld in lstFields:
            lstTD.append('<td {}>{}</td>'.format(options,domain.getValue(fld,nvl)))
      return '<tr>{}{}{}</tr>'.format(sBegin,''.join(lstTD),sEnd)
       
   @staticmethod
   def gridRow(datasource,onBegin=None,onEnd=None,options={}):
      """
      Liefert eine Eingabezeile aehnlich der einer Tabellenkalkulation.

      @param   datasource  ist eine Liste mit HMTL Fragmenten.
      @param   onBeginn    Eine Funktion die einen Text liefert.
                           Dieser wird am beginn der Datenzeile angezeigt.
      @param   onEnd       Eine Funktion die einen Text liefert.
                           Dieser wird am Ende der Datenzeile angezeigt
      @param   options     Ein Dictionary mit optionen fuer den td Tag.
      """
      lstTD = list()
      sBegin      = '<td>'+onBegin(domain)+'</td>' if onBegin is not None else ''
      sEnd        = '<td>'+onEnd(domain)+'</td>' if onEnd is not None else ''

      options      = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))

      for element in datasource:
           lstTD.append('<td {}>{}</td>'.format(options,element))
      
      return '<tr>{}{}{}</tr>'.format(sBegin,''.join(lstTD),sEnd)
   
   @staticmethod
   def tag(tag='div',value='',options={}):
      """
      Schliesst eine Inhalt in einem Tag ein.

      @param   tag      Tagart, Vorgabewert div
      @param   value    Inhalt, welcher zwischen Tagbeginn und Ende
                        eingefuegt wird.
      @param   options  HTML Optionen
      
      """
      options      = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))
      
      return '<{0} {1}>{2}</{0}>'.format(tag,options,value)


   @staticmethod
   def inputText(name,type='text',prompt='',options={},labeloptions={}):
      """
      Liefert ein HTML Fragment zur Dateneingabe.
      Die Tags koennen mit HTML Optionen versehen werden.
      
      Der Inputtag wird mit einem Labeltag verbunden.

      @param   name           Name des Inputfeldes
      @param   type           Standard "text"
      @param   prompt         Text, welcher vor dem Feld ausgegeben
                              werden soll (Labeltag)
      @param   options        Ein Diktionary welches die Optionen
                              fuer den Inputtag enthaelt.
      @param   lbloptions     Ein Diktionary welches die Optionen
                              fuer den Labeltag enthaelt.
      """
      sID = name if 'id' not in options else options.get('id')

      labeloptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),labeloptions.items()))

      options['type'] = type
      options['name'] = name
      options = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))
      
      label = '' if prompt == '' else '<label for="{id}" {options}>{prompt}</label>'.format(prompt=prompt, id=sID,options=labeloptions)
      return '{}<input {}/>'.format(label,options)

   @staticmethod
   def button(text,formaction,form=False,options={}):
      """
      Erzeugt eine Schaltflaeche. Optional kann diese in eine Form
      eingebettet werden.

      @param   text        Anzeigetext
      @param   formaction  Aktion, welche bei ausloesen der Schaltflaeche
                           druchgefuehrt wird.
      @param   form        Wenn True wird in Form Tags eingeschlossen
      @param   options     Optionen des Buttontas
      
      """
      retval = list()
      
      if formaction is not None:
         options['formaction']=str(formaction)

      options['formmethod']='post'
      options['type']='submit'

      alloptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))
      retval.append('{}<button {}>{}</button>{}'.format(
          '<form>' if form else '',
          alloptions,text,
          '</form>' if form else ''))
      
      return ''.join(retval)

   @staticmethod
   def truncate(value=None,size=16,nvl=''):
      """
      Beschneiden eines Strings
      
      @param   value       Wert
      @param   size        Laenge in Zeichen
      @param   nvl         Wird None als Value uebergeben
                           wird der Inhalt von nvl ausgegeben.

      """
      retval = ''

      value = str(value)
      title = value
      if value is None:
         value = nvl
         
      if len(value) > size :
         value = value[:size]
         while ord(value[-1]) > 127: value = value[:-1]
         value += '&hellip;'

      retval = '<span title="{1}">{0}</span>'.format(value,title)
      return retval

   @staticmethod
   def select(name,datasource,value=None,prompt='',options={},labeloptions={}):
      """
      Liefert einen HTML Select Tag.

      @param   name           Namen des Tag
      @param   datasource     Eine Liste von Optionseintraegen.
                              Jedes Element besteht aus einer Liste von
                              Inhalt und Anzeige. z.B.: [['ja','JA'],...]
      @param   value          Wert, welcher bei der Auwahl als Vorgabewert
                              angezegt werid (<option "selected" ...)
                              Value kann auch in options agegben werden.
                              options={'value':'ja',...} 
      @param   optionen       HTML Optionen des Selecttags
      @param   labeloptions   HTML Optionen des Labeltags
      
      """
      
      sID = name if 'id' not in options else options.get('id')

      if value is None:
         value = options.get('value')

      if name not in options:
         options['name'] = name
      
      theoptions = ''.join(
         [' <option value="{}"{}>{}</option>'.format(option[0],
         ' selected ' if str(option[0]) == str(value) else '',
         option[1]) for option in datasource])

      labeloptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),labeloptions.items()))
      label = '' if prompt == '' else '<label for="{id}" {options}>{prompt}</label>'.format(prompt=prompt, id=sID,options=labeloptions)

      soptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))

      return "{}<select {}>{}</select>".format(label,soptions,theoptions)

   @staticmethod
   def inputCheckbox(name,prompt='',options={},labeloptions={}):
      """
      Liefert ein Checkbox Eingabefeld


      @param   name           Nameoption des Feldes
      @param   prompt         Eingabeaufforderungs Text
      @param   options        HTML Optionen
      @param   labeloptions   HTML Optionen fuer den Labeltext
      
      """

      sID = name if 'id' not in options else options.get('id')

      labeloptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),labeloptions.items()))

      options['type'] = 'checkbox'
      options['name'] = name
      options = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))
      
      label = '' if prompt == '' else '<label for="{id}" {options}>{prompt}</label>'.format(prompt=prompt, id=sID,options=labeloptions)

      return '{}<input {}/>'.format(label,options)

   @staticmethod
   def formatNumber(num):
      """
      Formatiert eine Dezimalzahl deutsch formatiert.

      @param   num         Dezimalzahl
      
      """
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
   def tabbing(id='tabbing',curtab=None,options={},lioptions={},activoptions={},li=[]):
      """
      Stellt ein Tabbing widget zu Verfuegung.
      
      Die Tabbeingreihe wird als unordert list (<ul>) implemintiert.
      Die Tabs werden als Listenelemente dargestellt. Optional können
      pro Listenelement ein Anchor Tag (<a href="...) angegeben werden.
      

      @param   curtab         Aktueller Tab. Dieser wird hervorgehoben.
      @param   options        HTML Optionen fuer den UL-tag
      @param   lioptionen     HTML Optionen für das Listenelement
      @param   activoptions   HTML Optionn fuer das aktuelle
                              Element
      @param   li             Eine Liste von Dictionaries, welche
                              die Tab-Elemente beschreiben.
                              optoins: HTML Optionen
                              value:   Inhalt der Anzeige
                              href:    Wenn angegeben href Option
                                       des Anchortags.

      Beispiel :
         self.render(Taglib.tabbing(curtab=self.cgiparam('curtab'),li=[
            {
            'options':{},
            'value':'eins',
            'href':'?path=/&curtab=tab-1'
            },
            {
            'options':{'class':'nixi'},
            'value':'zwei',
            'href':'?path=/&curtab=tab-2'
            },
            {
            'options':{'name':'tab},
            'value':'drei',
            'href':'?path=/&curtab=tab-3'
            },
            ]
          )
         )
      
      """
      retval = list()
      retval.append('<style>')
      
      retval.append('''#{} ul {{
         border-bottom: 1px solid black;
         list-style-type: none; 
         margin: 0; 
         padding: 0;
         }}'''.format(id))
      
      retval.append('''#{} ul li{{
         margin:0;
         padding:0;
         margin-left:1px;
         border-left:1px solid black;
         border-top:1px solid black;
         border-right:1px solid black;
         padding:4px 4px; 
         display:inline-block;
         border-radius:5px 5px 0 0;
         background-color:#F5F5F5;
         }}'''.format(id))
         
      retval.append('''#{} .active {{
         position:relative;
         top:3px; 
         background:white;
         }}'''.format(id))

      retval.append('''#{} a {{
         text-decoration: none;
         }}'''.format(id))

      retval.append('</style>')

      soptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),options.items()))                     
      aoptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),activoptions.items()))

                    
      retval.append('<section id="{}">'.format(id))
      retval.append(' <ul {}>'.format(soptions))
      cnt = 0
      
      for l in li:
         cnt += 1
         auxlioptions = lioptions.copy()
         auxoptions = l.get('options',{})

         if l.get('name') is None:
            l['name'] = 'tab-{}'.format(cnt)

         if l.get('name','') == curtab:
            if 'class' in auxlioptions:
               auxlioptions['class'] += ' active'
            else:
               auxlioptions['class'] = 'active'
            
         auxoptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),auxoptions.items()))
         auxvalue = l.get('value','')

         if l.get('href') is not None:
            auxvalue = '<a href="{}" {}>{}</a>'.format(l.get('href'),auxoptions,auxvalue)
            
         loptions = ' '.join(map(lambda o : '{}="{}"'.format(o[0],o[1]),auxlioptions.items()))
         val = '   <li {}>{}</li>'.format(loptions,auxvalue)
         retval.append(val)
      retval.append(' <ul>')
      retval.append('</section>')

      return '\n'.join(retval)


if __name__ == "__main__":

   """
   print (Taglib.tabbing(curtab='tab-eins',li=[
         {
         'options':{},
         'value':'eins',
         'href':'?path=/&curtab=tab-1'
         },
         {
         'options':{'class':'nixi'},
         'value':'zwei',
         'href':'?path=/&curtab=tab-2'
         },
         {
         'name':'tab-eins',
         'options':{},
         'value':'drei',
         'href':'?path=/&curtab=tab-eins'
         },
         ]
       )
      )

   print(Taglib.formatNumber(1234567.89))

   print(Taglib.inputText("fldname",'text','Name eingeben',options={'id':'fldid','value':'MeinInhalt'}))

   print(Taglib.displayandhidden('id','123',options={'style':'color:red'}))

   print(Taglib.inputCheckbox("fld1","Mit Senf und Gurkerl",options={'style':'color:red'}))
   
   print (Taglib.tabbing(curtab='tab-eins',li=[
         {
         'options':{},
         'value':'eins',
         'href':'?path=/&curtab=tab-1'
         },
         {
         'options':{'class':'nixi'},
         'value':'zwei',
         'href':'?path=/&curtab=tab-2'
         },
         {
         'name':'tab-eins',
         'options':{},
         'value':'drei',
         'href':'?path=/&curtab=tab-eins'
         },
         ]
       )
      )
      
   
   
   print(Taglib.button(
            'Edit',
            '?path=/extras/employees&action=editmask&id={0}'.format(23),
             form=True)
        )

   datasource  = [[1,'eins'],[2,'zwei'],[3,'drei']]
   print (Taglib.select('Zahlen',datasource,
      value=2,
      prompt='Report To',
      options={
        'id':"select1",
        'class':"sel-class",
        'onclick':r'return confirm(\"Wirklich?\")'
         },
      labeloptions={
         'id':"lbl-1",
         'class':"lbl-class"
         }
      ))

   print(Taglib.inputText("fldname",'text','Name eingeben',options={'id':'fldid','value':'MeinInhalt'}))
   print(Taglib.button('Menueintrag','#',True))
   datasource  = [[1,'eins'],[2,'zwei'],[3,'drei']]
   print (Taglib.select('Zahlen',datasource,
      value=2,
      prompt='Report To',
      options={
        'id':"select1",
        'class':"sel-class",
        'onclick':r'return confirm(\"Wirklich?\")'
         },
      labeloptions={
         'id':"lbl-1",
         'class':"lbl-class"
         }
      ))


   # Hidden 
   print(Taglib.inputText("MeinFeld","hidden",options={'value':'MeinInhalt'}))
   
   lblOptions = {'style':'padding-top:4px;color:darkblue;'}

   print(Taglib.inputText('FirstName',prompt='Vorname:  ',labeloptions=lblOptions))
   """
