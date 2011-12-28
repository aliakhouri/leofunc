#!/usr/bin/env python
"""
leonode.py

A simulation of leo directives as decorators

usage::

    >>> from leonode import Node, directive
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
import sys
import string
import re
import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr

engine = create_engine('sqlite:///:memory:', echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

PATTERNS = {
    # @(?P<directive>\S+)\s+(?P<code>.*)\n@\n(?P<data>.*)
    'block': re.compile(
        r'@(?P<directive>\S+)\s+'
        r'(?P<code>.*)\n@\n'
        r'(?P<data>.*)'
        , flags=re.DOTALL),

    # @(?P<directive>\S+)\s?(?P<code>.*)
    'line': re.compile(
        r'@(?P<directive>\S+)\s?'
        r'(?P<code>.*)'
        , flags=re.DOTALL)
}

DIRECTIVES = {}

# custom namespace for inserting builtins etc..
NAMESPACE = {
    'a': 2,
    'date': str(datetime.now().date()),
    'upper': lambda s: s.upper(),
}


class UpOutline(Exception):
    "sends the outline iterator up a level"


class DownOutline(Exception):
    "sends the outline iterator down a level"


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


def strip_sides(text):
    """cleans whitespace from both sides of a string

        >>> strip_sides(' hello ')
        'hello'
    """
    return text.lstrip().strip()


def strip_all(text):
    """cleans all whitespace in a string

        >>> strip_all(' hello world ')
        'helloworld'
    """
    return text.replace(' ', '')


def pipe(arg, funcs):
    """creates a functional pipe operating on arg

        >>> pipe(1, [lambda x:x+1, lambda y:y*2])
        4
    """
    result = arg
    for func in funcs:
        result = func(result)
    return result


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

# -------------------------------------------------------------
# Higher-level functions as directives


@directive('hello', 'hello-expr')
def hello(world):
    def _hello(element):
        return 'hello ' + world
    return _hello


@directive('attr', 'set-attributes')
def set_attributes(**kwds):
    def _set_attributes(element):
        element.node.attributes.update(kwds)
    return _set_attributes


@directive('shadow', 'shadow-object')
def eval_shadow(*args, **kwds):
    '''placeholder for a more functional shadow directive
       doesn't really do anything but register the path
       in the node's attributes
    '''
    def _eval_shadow(element):
        element.node.attributes['path'] = element.code
    return _eval_shadow


@directive('pg', 'py-globals')
@directive('imports', 'py-imports')
def eval_py_namespace(**kwds):
    """creates and registers an @imports directive
    """
    def _eval_py_imports(element):
        element.node.tree.namespace.update(kwds)
        exec element.code in element.node.tree.namespace
    return _eval_py_imports


@directive('py', 'py-expr')
def eval_py_expression(**kwds):
    """ creates and registers an @py directive
    """
    def _eval_py_expression(element):
        namespace = element.get_namespace(**kwds)
        return eval(element.code, globals(), namespace)
    return _eval_py_expression


@directive('pyc', 'py-suite')
def eval_py_suite(**kwds):
    """ creates and registers an @pyc directive
    """
    def _eval_py_suite(element):
        # namespace = element.get_namespace(**kwds)
        exec element.code in element.node.namespace
    return _eval_py_suite


@directive('shell', 'shell-suite')
def eval_shell(**kwds):
    """ creates and registers an @shell and @sh directives
    """
    def _eval_shell(element):
        # namespace = element.get_namespace(**kwds)
        for line in element.code.split('\n'):
            os.system(line)
    return _eval_shell


@directive('sh', 'shell-value')
def eval_shell_value(**kwds):
    """ creates and registers an @sh directives
    """
    import subprocess

    def _eval_shell_value(element):
        args = element.code.split()
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    return _eval_shell_value


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


@directive('template', 'tmpl-suite')
@directive('tmpl', 'tmpl-expr')
def eval_template(**kwds):
    """evaluates string templates
    """
    def _eval_template(element):
        namespace = element.get_namespace(**kwds)
        return string.Template(element.code).substitute(**namespace)
    return _eval_template


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


@directive('xt', 'xt-templates')
def eval_xtemplate(engine, **kwds):
    """ multi-type template directive
    """
    engines = {'cheetah': eval_cheetah}

    def _eval_xtemplate(element):
        eval_func = engines[engine](**kwds)
        return eval_func(element)
    return _eval_xtemplate


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
            edges.append((first, last))
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        graph.write('%s.dot' % name)
        graph.layout()
        graph.draw('%s.png' % name)
        return graph.string()
    return _eval_graph


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


@directive('doc', 'doc-attr')
def eval_doc(**kwds):
    """ creates and registers an @doc directive
    """
    def _eval_doc(element):
        element.doc = element.code
        return element.doc
    return _eval_doc


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
# Main  classes


class Element(Base):
    __abstract__ = True

    def __init__(self, text):
        """ an element takes a node as its parent and a string
            for its content
        """
        self.text = text
        self.cache = {'default': ''}
        self.parse()
        if self.directive:
            self.type = self.get_type()

    def __repr__(self):
        return "<<%s:'%s'>>" % (self.__class__.__name__, self.text)

    def get_type(self):
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

    def get_view(self):
        """ returns default object view
        """
        return self.views('default')

    def set_view(self, value):
        """ set default object view
        """
        self.cache['default'] = value

    def del_view(self):
        """del default obj view
        """
        self.cache['default'] = ''

    view = property(get_view, set_view, del_view,
                    doc="default view of object")

    def eval_view(self):
        """eval current obj view
        """
        return eval(self.view, globals(), self.get_namespace())

    def views(self, name):
        """multiple views of object with caching
        """
        view = self.cache.get(name)
        if view:
            return view
        else:
            self.render(name)
            return self.cache[name]

    def render(self, name='default', **kwds):
        """render to named view or default
        """
        self.cache[name] = self.eval(**kwds)

    def parse(self):
        """updates attributes from inpunt text
        """
        if self.text.startswith('@'):
            result = {'directive': '', 'code': '', 'data': ''}
            if '\n' in self.text.strip():
                # a block
                pattern = PATTERNS['block']
            else:
                # a line
                pattern = PATTERNS['line']
            match = pattern.match(self.text)
            if match:
                #print "MATCH:", match.groupdict()
                result.update(match.groupdict())
                for key in result:
                    setattr(self, key, result[key])
                #self.__dict__.update(result)
            else:
                self.data = self.text
        else:
            self.data = self.text

    def get_namespace(self, **kwds):
        """ retrieves namespace and combines tree.namespace

            Note: this creates an independent namespace which dies
            i.e. it is expressly not an inplace namespace.
        """
        self.node.namespace.update(kwds)
        return combine(self.node.tree.namespace, self.node.namespace)

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


class Head(Element):
    """ concrete implementation of head element
    """
    __tablename__ = "head"
    id = Column(Integer, primary_key=True)
    text = Column(String(100))
    directive = Column(String(50))
    code = Column(String(100))
    data = Column(String(100))
    type = Column(String(50))
    version = Column(Integer)


class Body(Element):
    """ concrete implementation of body element
    """
    __tablename__ = "body"
    id = Column(Integer, primary_key=True)
    text = Column(String(100))
    directive = Column(String(50))
    code = Column(String(100))
    data = Column(String(100))
    type = Column(String(50))
    version = Column(Integer)


class ReDirector(object):
    """ abstract redirection class
    """
    def __init__(self, node):
        self.node = node

    def __call__(self):
        return self.node


class ToBody(ReDirector):
    """ redirects parameters to body object
    """
    def data(self, data):
        self.node.body.data = data

    def code(self, code):
        self.node.body.code = code

    def view(self, obj):
        self.node.body.view = obj


class ToHead(ReDirector):
    """ redirects parameters to head object
    """
    def data(self, data):
        self.node.head.data = data

    def code(self, code):
        self.node.head.code = code

    def view(self, obj):
        self.node.head.view = obj


class ToParent(ReDirector):
    """ redirects the parameters to parent object
    """
    def __init__(self, node):
        super(ToParent, self).__init__(node)
        self.head = ToHead(node.parent)
        self.body = ToBody(node.parent)


class To(ReDirector):
    """ the principal redirection mechanism

        >>> node = Node('a','b')
        >>> to = To(node)
        >>> # sets the node's head to 'hello'
        >>> to.head.data('hello')
        >>> assert node.head.data == 'hello'
    """
    def __init__(self, node):
        super(To, self).__init__(node)
        self.stdout = lambda s: sys.stdout.write(s + '\n')
        self.head = ToHead(node)
        self.body = ToBody(node)
        self.parent = ToParent(node)
        self.children = lambda arg: setattr(self.node, 'children', arg)


class Tree(object):
    """placeholder for a more functional tree
    """
    namespace = {}


class Node(Base):
    __tablename__ = "node"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('node.id'))
    children = relationship("Node", backref=backref('parent',
        remote_side='Node.id'))

    head_id = Column(Integer, ForeignKey('head.id'))
    head = relationship('Head', uselist=False, backref=backref('node',
        uselist=False))
    body_id = Column(Integer, ForeignKey('body.id'))
    body = relationship('Body', uselist=False, backref=backref('node',
        uselist=False))
    version = Column(Integer)
    type = Column(String(50))

    def __init__(self, head='', body='', parent=None,
                type=None, attributes={}, namespace={}, level=''):
        """initialize the class
        """
        self.parent = parent
        self.namespace = dict(node=self, to=To(self))
        self.namespace.update(namespace)
        self.namespace.update(NAMESPACE)
        self.head = Head(head)
        self.body = Body(body)
        self.tree = Tree()
        self.attributes = attributes
        self.write = lambda x: sys.stdout.write(x)
        self.type = type
        #self.directive = ''
        self.level = level

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

    def __iter__(self):
        return self.walk(self)

    #~ def __repr__(self):
        #~ return "<%s:'%s'>" % (self.__class__.__name__, self.head.text)

    def __repr__(self):
        name = self.__class__.__name__
        return "%s<%s %s [%s]>" % (' ' * len(self.level.split('.')),
            name, self.level, self.head.text)

    def __cmp__(self, other):
        return cmp(self.level.split('.'), other.level.split('.'))

    def render(self, **kwds):
        """ renders both head and body
        """
        self.head.render(**kwds)
        self.body.render(**kwds)


if __name__ == '__main__':
    debug = False
    if debug:
        import doctest
        doctest.testmod()
    else:
        Base.metadata.create_all(engine)

        # nodes
        n1 = Node('@hello("sa") option')
        n2 = Node('@py 1+1', parent=n1)
        n3 = Node('@pyc x=100', parent=n1)

        session.add_all([n1, n2, n3])
