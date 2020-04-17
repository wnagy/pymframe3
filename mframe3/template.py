#       Templite+
#       A light-weight, fully functional, general purpose templating engine
#
#       Copyright (c) 2009 joonis new media
#       Author: Thimo Kraemer <thimo.kraemer@joonis.de>
#
#       Angepasst: W. :nagy
#
#
#       Based on Templite - Tomer Filiba
#       http://code.activestate.com/recipes/496702/
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#
# Update:
#  15.12.2010, NY:
#
#  cgiparam:
#  ---------
#  Diese ermoeglicht es Daten aus dem CGI zu erhalten.
#  usage:
#     cgiparam(name='variable',nvl='')
#     name:    Name der CGI variable
#     nvl:     Inhalt wenn der Parameter nicht gesetzt oder einen leerstring enthaelt
#
# getField:
# ---------
# Dem Template kann ein Dictionary namens fields uebergeben werden.
# Diese Funktion ermittelt den Inhalt des Elements (name) aus dem Dictionary
# Wird dieser nicht gefunden wird der Wert aus dem Parameter nvl zurueckgeliefert.
# usage:
#  getField(name='<name>',nvl:'<default>')
#
# taglib:
# -------
# Die Klasse Taglib wird automatisch eingebunden.
#
#
#

import sys, re
import cgi
import traceback
from options.taglib         import Taglib

class PSP(object):
    auto_emit = re.compile('(^[\'\"])|(^[a-zA-Z0-9_\[\]\'\"]+$)')
    form = None
    namespace =  {}
    filename = None
    cgiparam = None
    isReadonly=False
    controller=None

    def getField(self,name=None, nvl=''):
       """Liefert eine Inhalt aus dem Dictionary fields
          Ist dies nicht moeglich, wird der Wert des Parameters nvl zurueckgegeben.

          @param  name     Name des Feldes
          @param  nvl      Vorgabewert

          """
       if not 'fields' in self.namespace:
          raise Exception('Das Dictionary fields wurde PSP nicht uebergeben')

       if 'fields' in self.namespace:
          fields = self.namespace['fields']
          if name in fields:
             return fields[name]
          else:
             return nvl
       else:
         return nvl

    def __init__(self, template=None, filename=None,cgiparam=None,start='<%', end='%>',isReadonly=False,controller=None):
        self.controller = controller
        if cgiparam is None:
            raise ValueError('cgiparam nicht uebergeben')
        self.cgiparam = cgiparam
        self.isReadonly = isReadonly

        if len(start) != 2 or len(end) != 2:
            raise ValueError('each delimiter must be two characters long')
        delimiter = re.compile('%s(.*?)%s' % (re.escape(start), re.escape(end)), re.DOTALL)
        offset = 0
        if filename is not None:
           self.filename = filename
        tokens = []
        for i, part in enumerate(delimiter.split(template)):
            part = part.replace('\\'.join(list(start)), start)
            part = part.replace('\\'.join(list(end)), end)
            if i % 2 == 0:
                if not part: continue
                part = part.replace('\\', '\\\\').replace('"', '\\"')
                part = '\t' * offset + 'out("""%s""")' % part
            else:
                part = part.rstrip()
                if not part: continue
                if part.lstrip().startswith(':'):
                    if not offset:
                        raise SyntaxError('no block statement to terminate: ${%s}$' % part)
                    offset -= 1
                    part = part.lstrip()[1:]
                    if not part.endswith(':'): continue
                elif self.auto_emit.match(part.lstrip()):
                    part = 'out(%s)' % part.lstrip()
                lines = part.splitlines()
                margin = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
                part = '\n'.join('\t' * offset + l[margin:] for l in lines)
                if part.endswith(':'):
                    offset += 1
            tokens.append(part)

        if offset:
            raise SyntaxError('%i block statement(s) not terminated' % offset)
        self.__code = compile('\n'.join(tokens), '<templite %r>' % template[:20], 'exec')

    def render(self, __namespace=None, **kw):
        """
        renders the template according to the given namespace.
        __namespace - a dictionary serving as a namespace for evaluation
        **kw - keyword arguments which are added to the namespace
        """
        self.namespace = {}

        if __namespace: self.namespace.update(__namespace)

        if kw: self.namespace.update(kw)
        theTaglib = Taglib()
        theTaglib.isReadonly = self.isReadonly

        self.namespace['out']          = self.write
        self.namespace['cgiparam']     = self.cgiparam
        self.namespace['getField']     = self.getField
        self.namespace['taglib']       = theTaglib
        self.namespace['controller']   = self.controller


        savestdout = sys.stdout
        hasError = False
        evalerror = None

        errormsg = ''
        try:
           __stdout = sys.stdout
           sys.stdout = self
           self.__output = []
           eval(self.__code, self.namespace)
           sys.stdout = __stdout

           return '\n'.join(self.__output)
        except Exception as ex:
           sys.stdout = savestdout
           errormsg = ex
           hasError = True

        if hasError:
           #raise Exception("Fehler in Templatefile '{0}'<br >{1}<br />".format(self.filename,ex))
           raise Exception("Fehler in Templatefile '{0}'<br >{1}<br />".format(self.filename,errormsg))

    def write(self, *args):
        for a in args:
            self.__output.append(str(a))

if __name__ == '__main__':

    template = r"""
This we already know:
<html>
    <body>
        ${
        def say_hello(arg):
            emit("hello ", arg, "<br>")
        }$

        <table>
            ${
                for i in range(10):
                    emit("<tr><td> ")
                    say_hello(i)
                    emit(" </tr></td>\n")
            }$
        </table>

        ${emit("hi")}$

        tralala ${if x > 7:
            say_hello("big x")}$ lala

        $\{this is escaped starting delimiter

        ${emit("this }\$ is an escaped ending delimiter")}$

        ${# this is a python comment }$

    </body>
</html>

But this is completely new:
${if x > 7:}$
    x is ${emit('greater')}$ than ${print x-1}$ Well, the print statement produces a newline.
${:else:}$
 This terminates the previous code block and starts an else code block
 Also this would work: $\{:end}\$$\{else:}\$, but not this: $\{:end}\$ $\{else:}\$
${:this terminates the else-block
only the starting colon is essential}$

So far you had to write:
${
    if x > 3:
        emit('''
            After a condition you could not continue your template.
            You had to write pure python code.
            The only way was to use %%-based substitutions %s
            ''' % x)
}$

${if x > 6:}$
    Now you do not need to break your template ${print x}$
${:elif x > 3:}$
    This is great
${:endif}$

${for i in range(x-1):}$  Of course you can use any type of block statement ${i}$ ${"fmt: %s" % (i*2)}$
${:else:}$
Single variables and expressions starting with quotes are substituted automatically.
Instead $\{emit(x)}\$ you can write $\{x}\$ or $\{'%s' % x}\$ or $\{"", x}\$
Therefore standalone statements like break, continue or pass
must be enlosed by a semicolon: $\{continue;}\$
The end
${:end-for}$
"""

    t = Templite(template)
    print (t.render(x=8))


    # Output is:
    """
This we already know:
<html>
    <body>


        <table>
            <tr><td> hello 0<br> </tr></td>
<tr><td> hello 1<br> </tr></td>
<tr><td> hello 2<br> </tr></td>
<tr><td> hello 3<br> </tr></td>
<tr><td> hello 4<br> </tr></td>
<tr><td> hello 5<br> </tr></td>
<tr><td> hello 6<br> </tr></td>
<tr><td> hello 7<br> </tr></td>
<tr><td> hello 8<br> </tr></td>
<tr><td> hello 9<br> </tr></td>

        </table>

        hi

        tralala hello big x<br> lala

        ${this is escaped starting delimiter

        this }$ is an escaped ending delimiter



    </body>
</html>

But this is completely new:

    x is greater than 7
 Well, the print statement produces a newline.


So far you had to write:

        After a condition you could not continue your template.
        You had to write pure python code.
        The only way was to use %-based substitutions 8



    Now you do not need to break your template 8



  Of course you can use any type of block statement 0 fmt: 0
  Of course you can use any type of block statement 1 fmt: 2
  Of course you can use any type of block statement 2 fmt: 4
  Of course you can use any type of block statement 3 fmt: 6
  Of course you can use any type of block statement 4 fmt: 8
  Of course you can use any type of block statement 5 fmt: 10
  Of course you can use any type of block statement 6 fmt: 12

Single variables and expressions starting with quotes are substituted automatically.
Instead ${emit(x)}$ you can write ${x}$ or ${'%s' % x}$ or ${"", x}$
Therefore standalone statements like break, continue or pass
must be enlosed by a semicolon: ${continue;}$
The end
"""
