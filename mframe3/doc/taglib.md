#Taglib
Die Taglib stellt einen Sammlung von Routinen zu Verfügung, welche zum formatierten Ausgeben dient.

Die Methoden sind als statische Methoden implementiert werden als `Taglib.<methodename>()` aufgerufen.

Beispiel: `print()Taglib.hidden('action','run'))` erzeugt ein HTML Fragment:
`<input type="hidden" name="action" value="run"/>`

## options
Sehr vielen Mehtoden ist der optionale Parameter options beigefügt. Dieser repräsentiert die Optionen des HTML Tags.

Beispiel:
`print()Taglib.tag('span','Ein beliebiger Text',options={'style':'color:hotpink'}))` 
erzeugt 
`<span style="color:hotpink">Ein beliebiger Text</span>`

#table
Liefert den Beginn einer HTML Tabelle

      @param   options     Tag Opionen
         

Beginnt eine HTML Tabelle.

Beispiel:
`   print(Taglib.table(options={'style':'width:100%'})`

erzeugt:
`<table style="width:100%">`

#endtable
Erzeugt einen Tag der das Ende einer HTML Tabelle anzeigt

#form
Beginnt eine Form in HTML.
**Forms werden immer mit der Methode "post" erzeugt**

      @param   options        HTML Optionen



#endform
Erzeugt einen Tag der das Ende einer HTML Tabelle anzeigt

#hidden
Erzeugt ein verstecktes eingabefeld in einer HTML Form.

      @param   name        Feldname
      @param   value       Inhalt
      @param   display     wird True uebergeben, so wird
                           der Inhalt von value an das HTML Feld
                           angefuegt
      	
Beispiel: `print(Taglib.hidden('id','123',display=True))`
erzeugt:
`<input type="hidden" name="id" value="123"/>123`

#displayandhidden
Eine spezialisierte Version von hidden mit der Option display=True


      @param   name        Feldname
      @param   value       Inhalt
      @param   display     wird True uebergeben, so wird
                           der Inhalt von value an das HTML Feld
                           angefuegt

Es wird ein verstecktes Eingabefeld erzeugt. Der Ihalt des Parameter `value` wird in Span-tags eigerahmt und kann mit Optionen versehen werden.

Beispiel:

	print()Taglib.displayandhidden('id','123',options={'style':'color:red'}))

erzeugt:
`<input type="hidden" name="id" value="123"/><span style="color:red">123</span>`

#getRow

Liefert eine Datenzeile basieren auf einer Domain Es koennen Hooks mitgegeben werden.

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

#gridRow

Liefert eine Eingabezeile als HTML Tabellennzeile (`<tr><td>...</tr>`)

      @param   datasource ist eine Liste mit HMTL Fragmenten.
      @param   onBeginn    Eine Funktion die einen Text liefert.
                           Dieser wird am beginn der Datenzeile angezeigt.
      @param   onEnd       Eine Funktion die einen Text liefert.
                           Dieser wird am Ende der Datenzeile angezeigt
      @param   options     Ein Dictionary mit optionen fuer den td Tag.

#tag

Schliesst eine Inhalt in einem Tag ein.

      @param   tag      Tagart, Vorgabewert div
      @param   value    Inhalt, welcher zwischen Tagbeginn und Ende
                        eingefuegt wird.
      @param   options  HTML Optionen
      
#inputText

Liefert ein HTML Fragment zur Dateneingabe. Die Tags koennen mit HTML Optionen versehen werden. Der Inputtag wird mit einem Labeltag verbunden.

>**HINT**
>
>wird Prompt nicht angegeben oder mit None versehen, wird das Erzeugen des `label` Elements unterdrückt.

      @param   name           Name des Inputfeldes
      @param   type           Standard "text"
      @param   prompt         Text, welcher vor dem Feld ausgegeben
                              werden soll (Labeltag)
      @param   options        Ein Diktionary welches die Optionen
                              fuer den Inputtag enthaelt.
      @param   lbloptions     Ein Diktionary welches die Optionen

Beispiel:

	print()Taglib.inputText("fldname",'text','Name eingeben',options={'id':'fldid','value':'MeinInhalt'}))

erzeugt:
`<label for="fldid" >Name eingeben</label><input id="fldid" value="MeinInhalt" type="text" name="fldname"/>`

#button

Erzeugt eine Schaltflaeche. Optional kann diese in eine Form
eingebettet werden.

      @param   text        Anzeigetext
      @param   formaction  Aktion, welche bei ausloesen der Schaltflaeche
                           druchgefuehrt wird.
      @param   form        Wenn True wird in Form Tags eingeschlossen
      @param   options     Optionen des Buttontas

Beispiel:

	print(Taglib.button(
	   'Edit',
	   '?path=/extras/employees&action=editmask&id={0}'.format(23),
	   form=True)
	   )

erzeugt:

	<form><button formaction="?path=/extras/employees&action=editmask&id=23" formmethod="post" type="submit">Edit</button></form>

#truncate
Beschneidet die Länge eines Strings und fügt, wenn der String die angegebene Länge übersteigt Fortsetzungspunkte (hellip) an. Die Zeichenkette wird im Original in einer Titeloption angegeben.

Beispiel:

	print(Taglib.truncate('Ein langer Text, der abgekürzt werden soll.'))

erzeugt:

	<span title="Ein langer Text, der abgekürzt werden soll.">Ein langer Text,&hellip;</span>

#select

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

Beispiel:

	   datasource  = [[1,'eins'],[2,'zwei'],[3,'drei']]
	   print(Taglib.select('Zahlen',datasource,
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
		  )
		 )

erzeugt:

	<label for="select1" id="lbl-1" class="lbl-class">Report To</label>
	 <select id="select1" class="sel-class" onclick="return confirm(\"Wirklich?\")" name="Zahlen"> 
	   <option value="1">eins</option> 
	   <option value="2" selected >zwei</option> 
	   <option value="3">drei</option>
	 </select>

#inputCheckbox
Liefert eine Checkbox Eingabefeld:

      @param   name           Nameoption des Feldes
      @param   prompt         Eingabeaufforderungs Text
      @param   options        HTML Optionen
      @param   labeloptions   HTML Optionen fuer den Labeltext

Beispiel:

	print(Taglib.inputCheckbox("fld1","Mit Senf und Gurkerl",options={'style':'color:red'}))

lefert.

	<label for="fld1" >Mit Senf und Gurkerl</label><input style="color:red" type="checkbox" name="fld1"/>

#formatNumber

      @param   num         Dezimalzahl

Beispiel:

	print(Taglib.formatNumber(1234567.89))

erzeugt:  1.234.567,89

#tabbing

Um eine Eingabemaske in mehere thematische Bereicht aufzuteilen wird tabbing verwendet.
Im wesentluchen einen Reihe von Tabellenreitern, welche angewählt werden können.

Stellt ein Tabbing widget zu Verfuegung. Die Tabbeingreihe wird als unordert list `(<ul>)` implemintiert. Die Tabs werden als Listenelemente dargestellt. Optional können pro Listenelement ein Anchor Tag (`<a href="...)` angegeben werden.

**HINT: **

es werden dem Widget, CSS Angaben beigefügt.

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

Beispiel:

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

liefert:

	<style>
	#tabbing ul {
			 border-bottom: 1px solid black;
			 list-style-type: none; 
			 margin: 0; 
			 padding: 0;
			 }
	#tabbing ul li{
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
			 }
	#tabbing .active {
			 position:relative;
			 top:3px; 
			 background:white;
			 }
	#tabbing a {
			 text-decoration: none;
			 }
	</style>
	<section id="tabbing">
	 <ul >
	   <li ><a href="?path=/&curtab=tab-1" >eins</a></li>
	   <li ><a href="?path=/&curtab=tab-2" class="nixi">zwei</a></li>
	   <li class="active"><a href="?path=/&curtab=tab-eins" >drei</a></li>
	 <ul>
	</section>
  
  
  