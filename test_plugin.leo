<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="20" left="1" height="790" width="655"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="sa.20090904024838.1225" a="E"><vh>@chapters</vh>
<v t="sa.20091017135749.1358"><vh>@enabled-plugins</vh></v>
<v t="sa.20091017131913.1244"><vh>docs</vh>
<v t="sa.20091017131913.1266"><vh> Templates: these show recommended ways of defining plugins.</vh>
<v t="sa.20091017131913.1267"><vh>Notes</vh>
<v t="sa.20091017131913.1268"><vh>About comments in the style guide</vh></v>
<v t="sa.20091017131913.1269"><vh>About the root node</vh></v>
<v t="sa.20091017131913.1270"><vh>About defining functions in separate nodes</vh></v>
<v t="sa.20091017131913.1271"><vh>About the &lt;&lt; imports &gt;&gt; section</vh></v>
<v t="sa.20091017131913.1272"><vh>About exceptions</vh></v>
</v>
<v t="sa.20091017131913.1273"><vh>Template for plugin that overrides commander methods</vh>
<v t="sa.20091017131913.1274"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="sa.20091017131913.1275"><vh>&lt;&lt; version history &gt;&gt;</vh></v>
<v t="sa.20091017131913.1276"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="sa.20091017131913.1277"><vh>init</vh></v>
<v t="sa.20091017131913.1278"><vh>onStart2</vh></v>
</v>
<v t="sa.20091017131913.1279"><vh>Template for Tk plugin with per-commander controller class</vh>
<v t="sa.20091017131913.1280"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="sa.20091017131913.1281"><vh>&lt;&lt; version history &gt;&gt;</vh></v>
<v t="sa.20091017131913.1282"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="sa.20091017131913.1283"><vh>init</vh></v>
<v t="sa.20091017131913.1284"><vh>onCreate</vh></v>
<v t="sa.20091017131913.1285"><vh>class pluginController</vh>
<v t="sa.20091017131913.1286"><vh>__init__</vh></v>
</v>
</v>
</v>
</v>
<v t="sa.20091017131913.1242" a="E"><vh>code</vh>
<v t="sa.20091017131913.1243"><vh>@button hello</vh></v>
<v t="sa.20091026232257.1296"><vh>doit</vh></v>
<v t="sa.20091017131913.1295"
expanded="sa.20091017143710.1570,"><vh>@thin leofunc_plugin.py</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="sa.20090904024838.1225" str_leo_pos="0,2,1"></t>
<t tx="sa.20091017131913.1242"></t>
<t tx="sa.20091017131913.1243">def fprint(name, obj):
    g.es_print(name+'\t: %s' % obj)

fprint('c', c.fileName())
fprint('p.h', p.h)
fprint('p', p)
fprint('g', g)
fprint('c', c)
#fprint('v', v)


</t>
<t tx="sa.20091017131913.1244"></t>
<t tx="sa.20091017131913.1266">@

Note: the newButtons.py now has templates for the following plugin nodes.
    
- init: A generic init function.
- init(tk): An init function for a plugin that uses Tk (or Pmw).
- &lt;&lt; imports &gt;&gt;:  The &lt;&lt;imports&gt;&gt; section.
- &lt;&lt; version history &gt;&gt;: The &lt;&lt;version history&gt;&gt; section.</t>
<t tx="sa.20091017131913.1267">@nocolor</t>
<t tx="sa.20091017131913.1268">Most of the comments in the style guide are comments _about_ the style guide.
You would replace these comments with your own, or eliminate them entirely in
your plugin.</t>
<t tx="sa.20091017131913.1269">- Several plugins show the docstring, so please take care to do a good job of
describing what the plugin does and how to use it.

- Please put the following immediately following the plugin's docstring.

    @language python
    @tabwidth -4

- There is no need to use sections if they are empty.

- The code should test whether modules have been imported only if those modules
may not be available on all platforms.

- Use following three lines only if your plugin uses a gui.

    if g.app.gui is None: 
        g.app.createTkGui(__file__)
    if g.app.gui.guiName() == "tkinter":
        ...

- Please use g.plugin_signon as shown, not leoPlugins.signon.</t>
<t tx="sa.20091017131913.1270">PLEASE define each function or method in a separate node! To make this work,
just put @others in the root of your plugin as shown. Note that @others may be
nested, as shown in class myClass.</t>
<t tx="sa.20091017131913.1271">Please use the general format as shown in &lt;&lt; imports &gt;&gt;.  In partular:

- Please do _not_ assume that modules like Tkinter, Pmw, etc. are always available.
  Use g.importExtension.

- Good Python style is to put each import on a separate line.

- Please abbreviate Tkinter as Tk.  Please do NOT abbreviate Pmw or leoPlugins.

- Please do NOT use either of the following kinds of imports.
    from m import *
    from m import x,y,z

- Do not import leo.core.leoNodes as leoNodes unless your plugin creates nodes directly.</t>
<t tx="sa.20091017131913.1272">It is usually best _not_ to catch exceptions in plugins:
doHook catches all exceptions and disables further calls to plugins.

If a plugin catches exceptions during startup it should do one of the following:
    
- raise the exception again.
- provide an init function at the top level that reports the failure.</t>
<t tx="sa.20091017131913.1273">&lt;&lt; docstring &gt;&gt;

__version__ = '0.0'
&lt;&lt; version history &gt;&gt;

&lt;&lt; imports &gt;&gt;

@others</t>
<t tx="sa.20091017131913.1274">'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
</t>
<t tx="sa.20091017131913.1275">@killcolor
@

Put notes about each version here.</t>
<t tx="sa.20091017131913.1276">import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

# Whatever other imports your plugins uses.</t>
<t tx="sa.20091017131913.1277">def init ():
    
    ok = True # This might depend on imports, etc.
    
    if ok:
        leoPlugins.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)
        
    return ok</t>
<t tx="sa.20091017131913.1278">def onStart2 (tag, keywords):
    
    """
    Showing how to define a global hook that affects all commanders.
    """

    import leo.core.leoTkinterFrame as leoTkinterFrame
    log = leoTkinterFrame.leoTkinterLog
    
    # Replace frame.put with newPut (not shown).
    g.funcToMethod(newPut,log,"put")</t>
<t tx="sa.20091017131913.1279">&lt;&lt; docstring &gt;&gt;

__version__ = '0.0'
&lt;&lt; version history &gt;&gt;

&lt;&lt; imports &gt;&gt;

@others</t>
<t tx="sa.20091017131913.1280">'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
</t>
<t tx="sa.20091017131913.1281">@killcolor
@

Put notes about each version here.</t>
<t tx="sa.20091017131913.1282">import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

Pmw = g.importExtension('Pmw',    pluginName=__name__,verbose=True,required=True)
Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

# Whatever other imports your plugins uses.</t>
<t tx="sa.20091017131913.1283">def init ():
    
    if not (Pmw and Tk): return False
    
    if g.app.gui is None:
        g.app.createTkGui(__file__)
        
    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        if 1: # Use this if you want to create the commander class before the frame is fully created.
            leoPlugins.registerHandler('before-create-leo-frame',onCreate)
        else: # Use this if you want to create the commander class after the frame is fully created.
            leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)
        
    return ok</t>
<t tx="sa.20091017131913.1284">def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    thePluginController = pluginController(c)</t>
<t tx="sa.20091017131913.1285">class pluginController:
    
    @others</t>
<t tx="sa.20091017131913.1286">def __init__ (self,c):
    
    self.c = c
    # Warning: hook handlers must use keywords.get('c'), NOT self.c.</t>
<t tx="sa.20091017135749.1358">leofunc_plugin.py
</t>
<t tx="sa.20091026232257.1296">g.es('hello')
</t>
</tnodes>
</leo_file>
