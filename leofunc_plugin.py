#@+leo-ver=4-thin
#@+node:sa.20091017131913.1295:@thin leofunc_plugin.py
#@<< docstring >>
#@+node:sa.20091017143710.1564:<< docstring >>
'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
#@-node:sa.20091017143710.1564:<< docstring >>
#@nl

__version__ = '0.0'
#@<< version history >>
#@+node:sa.20091017143710.1565:<< version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-at
#@nonl
#@-node:sa.20091017143710.1565:<< version history >>
#@nl

#@<< imports >>
#@+node:sa.20091017143710.1566:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins


# Whatever other imports your plugins uses.
#@nonl
#@-node:sa.20091017143710.1566:<< imports >>
#@nl

#@+others
#@+node:sa.20091017143710.1567:init
def init ():
    leoPlugins.registerHandler('after-create-leo-frame', onCreate)
    return True
#@-node:sa.20091017143710.1567:init
#@+node:sa.20091017143710.1568:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    thePluginController = pluginController(c)
#@-node:sa.20091017143710.1568:onCreate
#@+node:sa.20091017143710.1569:fprint
def fprint(name, obj):
    g.es_print(name+'\t: %s' % obj)
#@-node:sa.20091017143710.1569:fprint
#@+node:sa.20091017143710.1570:class pluginController
class pluginController:

    #@    @+others
    #@+node:sa.20091017143710.1571:__init__
    def __init__ (self, c):
        self.c = c
        c.k.registerCommand('do-action', shortcut=None, func=self.do_action)
        script = "c.k.simulateCommand('do-action')"
        g.app.gui.makeScriptButton(c, script=script, 
                                   buttonText='Do Action', bg='red')
    #@nonl
    #@-node:sa.20091017143710.1571:__init__
    #@+node:sa.20091017143710.1572:do_action
    def do_action (self, event=None):
        c = self.c ; p = c.p
        fprint('c', c.fileName())
        fprint('p.h', p.h)
        fprint('p', p)
        fprint('g', g)
        fprint('c', c)
    #@-node:sa.20091017143710.1572:do_action
    #@-others
#@-node:sa.20091017143710.1570:class pluginController
#@-others
#@nonl
#@-node:sa.20091017131913.1295:@thin leofunc_plugin.py
#@-leo
