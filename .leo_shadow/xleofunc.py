#@+leo-ver=4-thin
#@+node:sa.20090403012613.1:@shadow leofunc.py
#@@language python
#@@tabwidth -4

"""
leofunc.py

A simulation of leo directives as decorators

usage::

    >>> from leofunc import Node, directive
    >>> @directive('hello', 'hello-expr')
    ... def eval_hello(world):
    ...     def _eval_hello(element):
    ...         return 'hello %s' % world
    ...     return _eval_hello
    ...
    >>> n = Node("@hello('leo')")
    >>> n
     <Node  [@hello('leo')]>
    >>> n.head.type
    'hello-expr'
    >>> n.head.directive
    "hello('leo')"
    >>> n.head.code
    ''
    >>> n.head.data
    ''
    >>> n.head.text
    "@hello('leo')"
    >>> n.head.view
    'hello leo'
    >>>


"""

#@+others
#@+node:sa.20090405023327.1:leofunc declarations
import sys, string, re, os
from datetime import datetime

PATTERNS = {
    # @(?P<directive>\S+)\s+(?P<code>.*)\n@\n(?P<data>.*)
    'block': re.compile(
        r'@(?P<directive>\S+)\s+'   
        r'(?P<code>.*)\n@\n'      
        r'(?P<data>.*)'
        ,flags=re.DOTALL),

    # @(?P<directive>\S+)\s?(?P<code>.*)
    'line': re.compile(
        r'@(?P<directive>\S+)\s?'
        r'(?P<code>.*)'
        ,flags=re.DOTALL)
}

DIRECTIVES = {}

# custom namespace for inserting builtins etc..
NAMESPACE = {
    'a': 2,
    'date': str(datetime.now().date()),
    'upper' : lambda s: s.upper(),
}

#@-node:sa.20090405023327.1:leofunc declarations
#@+node:sa.20090405023327.55:outlining
#@+node:sa.20090405023327.2:class UpOutline
class UpOutline(Exception):
    "sends the outline iterator up a level"

#@-node:sa.20090405023327.2:class UpOutline
#@+node:sa.20090405023327.3:class DownOutline
class DownOutline(Exception):
    "sends the outline iterator down a level"

#@-node:sa.20090405023327.3:class DownOutline
#@+node:sa.20090405023327.4:outline
def outline():
    """
    creates numbered outlines

    originally created by castironpi (aaron brady), 
    tweaked by gabriel genelina

        >>> o = outline()
        >>> o.next()
        '1'
        >>> o.throw(DownOutline)
        '1.0'
        >>> o.next()
        '1.1'
    """
    stack = [1]
    while True:
        try:
            yield '.'.join(str(s) for s in stack)
            stack[-1] += 1
        except DownOutline:
            stack.append(0)
        except UpOutline:
            stack.pop(-1) 

#@-node:sa.20090405023327.4:outline
#@-node:sa.20090405023327.55:outlining
#@+node:sa.20090405023327.56:utilities
#@+node:sa.20090405023327.5:combine
# utility functions

def combine(*namespaces):
    """combines dictionaries
       last dict is prior.

        >>> combine({1:2}, {1:3})
        {1: 3}
    """
    combined = {}
    for namespace in namespaces:
        combined.update(namespace)
    return combined

#@-node:sa.20090405023327.5:combine
#@+node:sa.20090411210049.2:strip_sides
def strip_sides(text):
    """cleans whitespace from both sides of a string

        >>> strip_sides(' hello ')
        'hello'
    """
    return text.lstrip().strip()
#@-node:sa.20090411210049.2:strip_sides
#@+node:sa.20090411210049.3:strip_all


def strip_all(text):
    """cleans all whitespace in a string

        >>> strip_all(' hello world ')
        'helloworld'
    """
    return text.replace(' ', '')

#@-node:sa.20090411210049.3:strip_all
#@+node:sa.20090405023327.6:pipe

def pipe(arg, funcs):
    """creates a functional pipe operating on arg

        >>> pipe(1, [lambda x:x+1, lambda y:y*2]) 
        4
    """
    result = arg 
    for func in funcs:
        result = func(result)
    return result


#@-node:sa.20090405023327.6:pipe
#@-node:sa.20090405023327.56:utilities
#@+node:sa.20090405023327.57:decorators
#@+node:sa.20090405023327.53:directive
# utility decorators
def directive(symbol, type='', kind='element'):
    """a decorator registerings objects as leo directives
    """
    def _register(obj):
        obj.type = type
        obj.kind = kind
        DIRECTIVES[symbol] = obj 
        return obj
    return _register
#@-node:sa.20090405023327.53:directive
#@-node:sa.20090405023327.57:decorators
#@+node:sa.20090405023327.7:directives

# -------------------------------------------------------------
# Higher-level functions as directives
#@+node:sa.20090405023327.8:hello
@directive('hello', 'hello-expr')
def hello(world):
    def _hello(element):
        return 'hello ' + world
    return _hello

#@-node:sa.20090405023327.8:hello
#@+node:sa.20090408102856.9:set_attributes
@directive('attr', 'set-attributes')
def set_attributes(**kwds):
    def _set_attributes(element):
        element.node.attributes.update(kwds)
    return _set_attributes
#@-node:sa.20090408102856.9:set_attributes
#@+node:sa.20090413173014.5:eval_shadow

@directive('shadow', 'shadow-object')
def eval_shadow(*args, **kwds):
    '''placeholder for a more functional shadow directive
       doesn't really do anything but register the path 
       in the node's attributes 
    '''
    def _eval_shadow(element):
        element.node.attributes['path'] = element.code
    return _eval_shadow
#@-node:sa.20090413173014.5:eval_shadow
#@+node:sa.20090405023327.9:eval_py_namespace

@directive('pg', 'py-globals')
@directive('imports', 'py-imports')
def eval_py_namespace(**kwds):
    """creates and registers an @imports directive
    """
    def _eval_py_imports(element):
        element.node.tree.namespace.update(kwds)
        exec element.code in element.node.tree.namespace
    return _eval_py_imports


#@-node:sa.20090405023327.9:eval_py_namespace
#@+node:sa.20090405023327.10:eval_py_expression
@directive('py', 'py-expr')
def eval_py_expression(**kwds):
    """ creates and registers an @py directive
    """
    def _eval_py_expression(element):
        namespace = element.get_namespace(**kwds)
        return eval(element.code, globals(), namespace)
    return _eval_py_expression

#@-node:sa.20090405023327.10:eval_py_expression
#@+node:sa.20090405023327.11:eval_py_suite
@directive('pyc', 'py-suite')
def eval_py_suite(**kwds):
    """ creates and registers an @pyc directive
    """
    def _eval_py_suite(element):
        # namespace = element.get_namespace(**kwds)
        exec element.code in element.node.namespace
    return _eval_py_suite

#@-node:sa.20090405023327.11:eval_py_suite
#@+node:sa.20090411210049.4:eval_shell
@directive('shell', 'shell-suite')
def eval_shell(**kwds):
    """ creates and registers an @shell and @sh directives
    """
    def _eval_shell(element):
        # namespace = element.get_namespace(**kwds)
        for line in element.code.split('\n'):
            os.system(line)
    return _eval_shell

#@-node:sa.20090411210049.4:eval_shell
#@+node:sa.20090412220044.4:eval_shell_value
@directive('sh', 'shell-value')
def eval_shell_value(**kwds):
    """ creates and registers an @sh directives
    """
    import subprocess
    def _eval_shell_value(element):
        args = element.code.split()
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    return _eval_shell_value

#@-node:sa.20090412220044.4:eval_shell_value
#@+node:sa.20090405023327.12:eval_pipe
@directive('pipe', 'py-pipe')
def eval_pipe(**kwds):
    """ creates and registers an @pipe directive
    """
    def _eval_pipe(element):
        namespace = element.get_namespace(**kwds)
        lst = [i.strip() for i in element.code.split('|')]
        arg, funcs = lst[0], lst[1:]
        arg = eval(arg, globals(), namespace)
        funcs = (eval(i, globals(), namespace) for i in funcs)
        return pipe(arg, funcs)
    return _eval_pipe


#@-node:sa.20090405023327.12:eval_pipe
#@+node:sa.20090405023327.13:eval_template
@directive('template', 'tmpl-suite')
@directive('tmpl', 'tmpl-expr')
def eval_template(**kwds):
    """evaluates string templates
    """
    def _eval_template(element):
        namespace = element.get_namespace(**kwds)
        return string.Template(element.code).substitute(**namespace)
    return _eval_template


#@-node:sa.20090405023327.13:eval_template
#@+node:sa.20090405023327.14:eval_cheetah
@directive('cheetah', 'cheetah-suite')
@directive('ch', 'cheetah-expr')
def eval_cheetah(**kwds):
    """ evaluates cheetah templates
    """
    def _eval_cheetah(element):
        from Cheetah.Template import Template
        namespace = element.get_namespace(**kwds)
        return str(Template(element.code, namespaces=[namespace]))
    return _eval_cheetah


#@-node:sa.20090405023327.14:eval_cheetah
#@+node:sa.20090405023327.58:eval_xtemplate
@directive('xt', 'xt-templates')
def eval_xtemplate(engine, **kwds):
    """ multi-type template directive
    """
    engines = {'cheetah': eval_cheetah}
    def _eval_xtemplate(element):
        eval_func = engines[engine](**kwds)
        return eval_func(element)
    return _eval_xtemplate


#@-node:sa.20090405023327.58:eval_xtemplate
#@+node:sa.20090408100102.1:eval_graph
@directive('graph', 'dot-graphs')
def eval_graph(name='', **kwds):
    """ creates and registers an @graph directive
    """
    if not name:
        name = 'leo_graphe'

    def _eval_graph(element):
        import pygraphviz
        graph = pygraphviz.AGraph(directed=True)
        nodes = set()
        edges = []
        entries = (i for i in element.code.split('\n') if i)
        for entry in entries:
            first, last = entry.split('->')
            first = strip_sides(first)
            last = strip_sides(last)
            edges.append((first,last))
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)        
        graph.write('%s.dot' % name)
        graph.layout()
        graph.draw('%s.png' % name)
        return graph.string()
    return _eval_graph
#@nonl
#@-node:sa.20090408100102.1:eval_graph
#@+node:sa.20090408102856.7:eval_rss

@directive('rss', 'rss-feed')
def eval_rss(**kwds):
    """ creates and registers an @rss directive
    """
    # takes the code part of an element as the argument
    # e.g. @rss feed://news.google.com/etc

    def _eval_rss(element):
        import urllib
        feed = urllib.urlopen(element.code).read()
        return feed
    return _eval_rss
#@-node:sa.20090408102856.7:eval_rss
#@+node:sa.20090411175828.4:eval_doc

@directive('doc', 'doc-attr')
def eval_doc(**kwds):
    """ creates and registers an @doc directive
    """
    def _eval_doc(element):
        element.doc = element.code
        return element.doc
    return _eval_doc

#@-node:sa.20090411175828.4:eval_doc
#@+node:sa.20090411175828.5:eval_csum
@directive('csum', 'csum-expr')
def eval_csum(**kwds):
    def _eval_csum(element):
        sumd = lambda d: sum(d[k] for k in d)
        if element.code:
            d = element.node.namespace[element.code] = {}
        else:
            d = {}
        lst = []
        # all_children = list(element.node)
        for child in element.node.children:
            head = child.head.view
            lst.append(head)
            body = child.body.view
            lst.append(body)
        assigns = '\n'.join(lst)
        exec assigns in d
        del d['__builtins__']
        return sumd(d)
    return _eval_csum

#@-node:sa.20090411175828.5:eval_csum
#@+node:sa.20090405023327.15:sort_children
# -------------------------------------------------------------
# Tree Transformers

@directive('sort', 'tree-transformer')
def sort_children(**kwds):
    """sorts children nodes
    """
    def _sort_children(element):
        element.node.children = sorted(element.node.children)        
    return _sort_children

# -------------------------------------------------------------
#@-node:sa.20090405023327.15:sort_children
#@-node:sa.20090405023327.7:directives
#@+node:sa.20090405023327.16:class Element
# Main  classes

class Element(object):
    """ superclass of a head or body element in a LeoNode

        :param node: a leo node
        :type  node: Node
        :param text: raw text associated with the element
        :type  text: str
    """
    #@    @+others
    #@+node:sa.20090405023327.17:__init__

    def __init__(self, node, text):
        """ an element takes a node as its parent and a string
            for its content
        """
        self.node = node
        self.text = text
        self.directive = ''
        self.code = ''
        self.data = '' 
        self.cache = {'default':''}
        self.parse()

    #@-node:sa.20090405023327.17:__init__
    #@+node:sa.20090405023327.19:type
    @property
    def type(self):
        """ retrieves the type of the directive
        """
        if '(' in self.directive:
            directive = self.directive[:self.directive.index('(')]
        else:
            directive = self.directive
        func = DIRECTIVES.get(directive)
        if func:
            return func.type
        else:
            return 'user-data'        

    #@-node:sa.20090405023327.19:type
    #@+node:sa.20090411210049.13:view
    #@+node:sa.20090405023327.20:get_view
    def get_view(self):
        """ returns default object view
        """
        return self.views('default')

    #@-node:sa.20090405023327.20:get_view
    #@+node:sa.20090405023327.21:set_view
    def set_view(self, value):
        """ set default object view
        """
        self.cache['default'] = value

    #@-node:sa.20090405023327.21:set_view
    #@+node:sa.20090405023327.22:del_view
    def del_view(self):
        """del default obj view
        """
        self.cache['default'] = ''


    view = property(get_view, set_view, del_view, 
                    doc="default view of object")

    #@-node:sa.20090405023327.22:del_view
    #@+node:sa.20090411175828.1:eval_view
    def eval_view(self):
        """eval current obj view
        """
        return eval(self.view, globals(), self.get_namespace())

    #@-node:sa.20090411175828.1:eval_view
    #@-node:sa.20090411210049.13:view
    #@+node:sa.20090405023327.23:views

    def views(self, name):
        """multiple views of object with caching
        """
        view = self.cache.get(name)
        if view:
            return view
        else:
            self.render(name)
            return self.cache[name]

    #@-node:sa.20090405023327.23:views
    #@+node:sa.20090405023327.24:render
    def render(self, name='default', **kwds):
        """render to named view or default
        """
        self.cache[name] = self.eval(**kwds)


    #@-node:sa.20090405023327.24:render
    #@+node:sa.20090405023327.25:parse
    def parse(self):
        """updates attributes from input text
        """
        if self.text.startswith('@'):
            result = {'directive':'', 'code':'', 'data':''}
            if '\n' in self.text.strip():
                # a block
                pattern = PATTERNS['block']
            else:
                # a line
                pattern = PATTERNS['line']
            match = pattern.match(self.text)
            if match:
                result.update(match.groupdict())
                self.__dict__.update(result)
            else:
                self.data = self.text
        else:
            self.data = self.text

    #@-node:sa.20090405023327.25:parse
    #@+node:sa.20090405023327.26:get_namespace

    def get_namespace(self, **kwds):
        """ retrieves namespace and combines tree.namespace

            Note: this creates an independent namespace which dies
            i.e. it is expressly not an inplace namespace.
        """
        self.node.namespace.update(kwds)
        return combine(self.node.tree.namespace, self.node.namespace)        

    #@-node:sa.20090405023327.26:get_namespace
    #@+node:sa.20090405023327.27:eval
    def eval(self, *args, **kwds):
        """ the evaluation dispatcher defaults to self.text
        """
        directive = self.directive
        kwds.update(DIRECTIVES)
        if directive:
            if '(' in directive:
                namespace = self.get_namespace(**kwds)
                eval_func = eval(directive, globals(), namespace)
            else:
                eval_func = DIRECTIVES[directive](*args, **kwds)
            return eval_func(self)
        else:
            return self.text


    #@-node:sa.20090405023327.27:eval
    #@-others
#@-node:sa.20090405023327.16:class Element
#@+node:sa.20090405023327.28:class Head
class Head(Element):
    """ concrete implementation of head element
    """

#@-node:sa.20090405023327.28:class Head
#@+node:sa.20090405023327.29:class Body
class Body(Element):
    """ concrete implementation of body element
    """

#@-node:sa.20090405023327.29:class Body
#@+node:sa.20090405023327.54:redirectors
#@+node:sa.20090405023327.30:class ReDirector
class ReDirector(object):
    """ abstract redirection class
    """
    #@    @+others
    #@+node:sa.20090405023327.31:__init__
    def __init__(self, node):
        self.node = node

    #@-node:sa.20090405023327.31:__init__
    #@+node:sa.20090405023327.32:__call__
    def __call__(self):
        return self.node

    #@-node:sa.20090405023327.32:__call__
    #@-others
#@-node:sa.20090405023327.30:class ReDirector
#@+node:sa.20090405023327.33:class ToBody
class ToBody(ReDirector):
    """ redirects parameters to body object
    """
    #@    @+others
    #@+node:sa.20090405023327.34:data
    def data(self, data):
        self.node.body.data = data
    #@-node:sa.20090405023327.34:data
    #@+node:sa.20090405023327.35:code
    def code(self, code):
        self.node.body.code = code
    #@-node:sa.20090405023327.35:code
    #@+node:sa.20090405023327.36:view
    def view(self, obj):
        self.node.body.view = obj

    #@-node:sa.20090405023327.36:view
    #@-others
#@-node:sa.20090405023327.33:class ToBody
#@+node:sa.20090405023327.37:class ToHead
class ToHead(ReDirector):
    """ redirects parameters to head object
    """
    #@    @+others
    #@+node:sa.20090405023327.38:data
    def data(self, data):
        self.node.head.data = data
    #@-node:sa.20090405023327.38:data
    #@+node:sa.20090405023327.39:code
    def code(self, code):
        self.node.head.code = code
    #@-node:sa.20090405023327.39:code
    #@+node:sa.20090405023327.40:view
    def view(self, obj):
        self.node.head.view = obj

    #@-node:sa.20090405023327.40:view
    #@-others
#@-node:sa.20090405023327.37:class ToHead
#@+node:sa.20090405023327.41:class ToParent
class ToParent(ReDirector):
    """ redirects the parameters to parent object
    """
    #@    @+others
    #@+node:sa.20090405023327.42:__init__
    def __init__(self, node):
        super(ToParent, self).__init__(node)
        self.head = ToHead(node.parent)
        self.body = ToBody(node.parent)

    #@-node:sa.20090405023327.42:__init__
    #@-others
#@-node:sa.20090405023327.41:class ToParent
#@+node:sa.20090405023327.43:class To
class To(ReDirector):
    """ the principal redirection mechanism

        >>> node = Node('a','b')
        >>> to = To(node)
        >>> # sets the node's head to 'hello'
        >>> to.head.data('hello')
        >>> assert node.head.data == 'hello'
    """
    #@    @+others
    #@+node:sa.20090405023327.44:__init__
    def __init__(self, node):
        super(To, self).__init__(node)
        self.stdout = lambda s: sys.stdout.write(s+'\n')
        self.head = ToHead(node)
        self.body = ToBody(node)
        self.parent = ToParent(node)
        self.children = lambda arg: setattr(self.node, 'children', arg)

    #@-node:sa.20090405023327.44:__init__
    #@-others
#@-node:sa.20090405023327.43:class To
#@-node:sa.20090405023327.54:redirectors
#@+node:sa.20090405023327.45:class Tree
class Tree(object):
    """placeholder for a more functional tree
    """
    namespace = {}

#@-node:sa.20090405023327.45:class Tree
#@+node:sa.20090405023327.46:class Node
class Node(object):
    """principle Node class

    :param head: a string for the head
    :type  head: str

    :param body: a string for the body
    :type  body: str

    :param children: children nodes
    :type children: list

    :param parent: a parent node
    :type parent: Node 

    :param type: the given node-type
    :type type: str

    :param attributes: a dict of attributes
    :type attributes: dict

    :param namespace: node-level namespace
    :type namespace: dict

    :param level: the position of a node in an outline
    :type level: str

    """
    #@    @+others
    #@+node:sa.20090405023327.47:__init__
    def __init__(self, head='', body='', children=[], parent=None, 
                type=None, attributes={}, namespace={}, level=''):
        """initialize the class
        """
        self.children = children
        self.parent = parent
        self.namespace = dict(node=self, to=To(self))
        self.namespace.update(namespace)
        self.namespace.update(NAMESPACE)
        self.tree = Tree()
        self.head = Head(self, head)
        self.body = Body(self, body)
        self.attributes = attributes
        self.write = lambda x: sys.stdout.write(x)
        self.type = type
        self.directive = ''
        self.level = level


    #@-node:sa.20090405023327.47:__init__
    #@+node:sa.20090405023327.48:walk
    def walk(self, node, o=None):
        """ recursive node walker
            sets parents and levels as a bonus
            cheers castironpi and gabriel (-:
        """
        if o is None:
            o = outline()
        node.level = o.next()
        yield node
        if node.children:
            o.throw(DownOutline)
            for child in node.children:
                child.parent = node
                for subnode in self.walk(child, o):
                    yield subnode
            o.throw(UpOutline) 

    #@-node:sa.20090405023327.48:walk
    #@+node:sa.20090405023327.49:__iter__
    def __iter__(self):
        return self.walk(self)

    #@-node:sa.20090405023327.49:__iter__
    #@+node:sa.20090405023327.50:__repr__
    def __repr__(self):
        name = self.__class__.__name__
        return "%s<%s %s [%s]>" % ( ' '*len(self.level.split('.')),
            name, self.level, self.head.text)

    #@-node:sa.20090405023327.50:__repr__
    #@+node:sa.20090405023327.51:__cmp__
    def __cmp__(self, other):
        return cmp(self.level.split('.'), other.level.split('.'))

    #@-node:sa.20090405023327.51:__cmp__
    #@+node:sa.20090405023327.52:render
    def render(self, **kwds):
        """ renders both head and body
        """
        self.head.render(**kwds)
        self.body.render(**kwds)



    #@-node:sa.20090405023327.52:render
    #@-others
#@-node:sa.20090405023327.46:class Node
#@-others

if __name__ == '__main__':
    import doctest
    doctest.testmod()
#@-node:sa.20090403012613.1:@shadow leofunc.py
#@-leo
