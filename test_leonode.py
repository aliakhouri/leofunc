#!/usr/bin/env python
from leonode import Node, To, PATTERNS


NODES = {}      # {node:test_func}
TESTS = []      # [test_func]
TESTMAP = {}    # {'name':test_func}

VERBOSE = False


def register(node=None, match_head=None, match_body=None):
    def _register(func):
        if node:
            node.match = (match_head, match_body)
            NODES[node] = func
        TESTMAP[func.__name__] = func
        TESTS.append(func)
        return func
    return _register
    
def headline(text, top=True, bottom=True, sep='-'):
    if top:
        print sep * 70
    print text
    if bottom:
        print sep * 70

def display(root):
    def _display(node, element_type):
        obj = getattr(node, element_type)
        attrs = ['type','text', 'code', 'data', 'view']
        print
        for attr in attrs:
            print '%s.%s:' % (element_type, attr), getattr(obj, attr)

    headline('head: %s [%s]\nbody: %s' % (root.head.type, 
        root.head.text, root.body.type))
    print 'node:', root
    print 'node.parent:', root.parent
    print 'len(node.children):', len(root.children)
    _display(root, 'head')
    _display(root, 'body')
    print
    print 'structure:'
    for i in root:
        print i

def node1(head, body=''):
    n = Node(
        head.lstrip(), 
        '\n'.join([l.lstrip() for l in body.split('\n') if l])
    )
    return n


def get_tree(root, b1, b2, l1, l2, l3):
    root.children=[b1,b2]
    b1.children=[l1]
    b2.children=[l2,l3]
    list(root)
    return root


def match(node, head=0, body=0):
     '''tests whether a node is matched at least once
     '''
     for i in PATTERNS:
         p = PATTERNS[i]
         if node.match[0]: # head
             m = p.match(node.head.text)
             if m: head = 1
         if node.match[1]: # head
             m = p.match(node.body.text)
             if m: body = 1
     if node.match == (head, body):
         return True
     else:
         return False


def standard(n):
    assert n == n.namespace['node']
    assert n.head.text
    assert match(n)
    # n.render()
    # display(n)


# ---------------------------------------------------
# TESTING Directives
# ---------------------------------------------------

@register()
def test_signature():

    def test(directive):
        node = Node(directive)
        if VERBOSE:
            print directive,':', node.head.view

    from leonode import directive

    @directive('func')
    def func(**kwds):
        def _func(element):
            return element
        return _func

    f1 = directive('f1')(
        lambda *args, **kwds: lambda element: element)

    f2 = directive('f2')(
        lambda **kwds: lambda element: kwds)

    f3 = directive('f3')(
        lambda *args: lambda element: args)

    f4 = directive('f4')(
        lambda x: lambda element: x + id(element))

    f5 = directive('f5')(
        lambda x, y: lambda element: x+y)

    f5 = directive('f5')(
        lambda x, y, a=1: lambda element: x+y+a)

    h1 = directive('h1', 'h-expr')(
        lambda **kwds: lambda element: element.type)

    directives = [
        '@func', 
        '@f1', 
        '@f2(a=1,b=2)',
        '@f3(1,2)', 
        '@f4(1)', 
        '@f5(1,2)',
        '@h1'
    ]
    for d in directives:
        test(d)

py_expr_1 = node1(
    "@py 'Hello'.upper()", 
    "@py 'some lovely texts'.upper()"
)

@register(py_expr_1, 1, 1)
def test_py_expr_1():
    n = py_expr_1
    standard(n)
    # print n.namespace
    assert py_expr_1 == py_expr_1.namespace['node']
    assert n.head.code
    n.head.render()
    assert n.head.view == 'HELLO'
    assert n.body.code
    n.body.render()
    assert n.body.view == 'SOME LOVELY TEXTS'
    if VERBOSE: display(n)




py_expr_2 = node1(
    "@pyc y = 1", 
    "@py y * 32"
)

@register(py_expr_2, 1, 1)
def test_py_expr_2():
    n = py_expr_2
    standard(n)
    n.head.render()
    n.body.render()
    assert n.body.view == 32
    assert n.body.code
    if VERBOSE: display(n)

py_expr_3 = node1(
    "@py 'i like a ' + sandwhich", 
    "@pyc sandwhich = 'special'"
)

@register(py_expr_3, 1, 1)
def test_py_expr_3():
    n = py_expr_3
    standard(n)
    n.body.render()
    n.head.render()
    assert n.head.view == "i like a special"
    # assert n.body.code
    if VERBOSE: display(n)

py_expr_4 = node1("@py sum(n.head.view for n in node.children)")
py_expr_4_1 = node1("@py 1 + 21")
py_expr_4_2 = node1("@py 10 + 32")

@register(py_expr_4, 1, 0)
def test_py_expr_4():
    n = py_expr_4
    n.children = [py_expr_4_1, py_expr_4_2]
    standard(n)
    assert n.head.view == 64
    if VERBOSE: display(n)

py_suite_1 = node1(
    "@pyc import os", 
    """
    @pyc
    node.body.data = a * 2132
    @
    some data in the body
    """
)

@register(py_suite_1, 1, 1)
def test_py_suite_1():
    n = py_suite_1
    standard(n)
    assert n.head.code
    assert n.body.code
    n.body.view
    assert n.body.data == 2 * 2132
    if VERBOSE: display(n)

py_suite_2 = node1(
    "a block of python code",
    """
    @pyc
    import math

    a = 10
    b = a * math.pi
    assert a < b

    node.body.data = a * 2132
    node.body.view = "hello"
    @
    some data in the body
    """
)


@register(py_suite_2, 0, 1)
def test_py_suite_2():
    n = py_suite_2
    standard(n)
    assert n.body.code
    n.body.view
    assert n.body.data == 21320
    if VERBOSE: display(n)

pipe_1 = node1(
    "@pipe 'd' | upper",
    "this is a body"
)


@register(pipe_1, 1, 0)
def test_pipe_1():
    n = pipe_1
    standard(n)
    assert n.head.code
    n.render()
    assert n.head.view == 'D'
    if VERBOSE: display(n)

pipe_2 = node1(
    "@pipe node.body.data | upper", 
    "a body"
)

@register(pipe_2, 1, 0)
def test_pipe_2():
    n = pipe_2
    standard(n)
    assert n.head.code
    n.render()
    assert n.head.view == 'A BODY'
    if VERBOSE: display(n)


pipe_3 = node1(
    "@pipe 'ok' | upper | to.body.data"
)



@register(pipe_3, 1, 0)
def test_pipe_3():
    n = pipe_3
    standard(n)
    n.render()
    assert n.body.data == 'OK'



pipe_4 = Node(
    "@pipe node.children | sorted | to.children",
    "")
pipe_4.children = [Node('a','c', level='3.1'), 
         Node('b','d', level='1.1')]

@register(pipe_4, 1, 0)
def test_pipe_4():
    n = pipe_4
    standard(n)
    a = n.children[0].head.text
    assert a == 'a'
    n.render()
    b = n.children[0].head.text
    assert b == 'b'
    assert a != b

pipe_5 = node1(
    "@pipe node.body.data | upper | to.head.data",
    "this is a body"
)

@register(pipe_5, 1, 0)
def test_pipe_5():
    n = pipe_5
    standard(n)
    assert n.head.code
    n.head.render()
    assert n.head.data == n.body.data.upper()
    # display(n)


shell_1 = node1(
    "@shell rm *.pyc",
    "@sh ls -l"
)


@register(shell_1, 1, 1)
def test_shell_1():
    n = shell_1
    standard(n)
    assert n.head.code
    assert n.body.code
    n.render()

shell_2 = node1("@sh cat go")

@register(shell_2, 1, 0)
def test_shell_2():
    n = shell_2
    n.render()
    assert n.head.view

imports_1 = node1(
    "a basic headline", 
    """
    @imports
    import xml    
    @
    hello
    """
)

@register(imports_1, 0, 1)
def test_imports_1():
    n1 = imports_1
    standard(n1)
    assert n1.body.code
    n1.render()
    assert 'xml' in n1.tree.namespace
    assert 'hello' in n1.body.data

imports_2 = node1(
    "a basic headline", 
    """
    @imports

    t1 = "ok"
    @
    hello
    """
)

@register(imports_2, 0, 1)
def test_complex_imports():
    n1 = imports_2
    standard(n1)
    assert n1.body.code
    n1.render()
    assert 't1' in n1.tree.namespace
    assert 'hello' in n1.body.data

    n2 = Node("h2", "@py upper(t1)")
    # standard(n2)
    assert n2.body.code
    assert 't1' in n2.tree.namespace
    #~ assert n2.body.type == 'py-expr'
    n2.body.render()
    assert n2.body.view == "OK"

@register()
def test_sorting_levels():
    headline('sorting outlines')
    n1 = Node('h1', 'b1')
    n1.level = '1.3.1'
    n2 = Node('h2', 'b2')
    n2.level = '1.1'
    n3 = Node('h3', 'b3')
    n3.level = '1.2'
    nodes = [n1,n2,n3]
    if VERBOSE:
        print nodes
        print sorted(nodes)
    assert sorted(nodes)[0] == n2 

@register()
def test_sort_directive():
    n = node1('@sort ', "body")
    n1 = node1('a','b')
    n2 = node1('c', 'd')
    n1.level = '1.9'
    n2.level = '1.1'
    n.children = [n1, n2]
    n.render()
    if VERBOSE:
        display(n) # visual confirmation (-:


tmpl_1 = node1(
    "@tmpl this a=$a is embedded in the body",
    """
    @template

    Is it really $date ?

    @
    some body text
    """
)

@register(tmpl_1, 1, 1)
def test_template():
    n = tmpl_1
    standard(n)
    if VERBOSE: display(n)

cheetah_1 = node1(
    "@ch this a=${a+2} is a ${100 * 43}",
    """
    @cheetah

    #def pod(person)
    Mr. Pod $person
    #end def

    Is it really a $date ? $pod('OK')

    @
    """
)


@register(cheetah_1, 1, 1)
def test_cheetah():
    n = cheetah_1
    standard(n)
    if VERBOSE: display(n)

@register()
def test_param_1():
    n = Node(head="@hello('world')")
    n.head.render()
    assert n.head.view == 'hello world' 
    if VERBOSE: display(n)

@register()
def test_param_2():
    n = Node(head="@py(b=2) b * 100")
    n.head.render()
    assert n.head.view == 200
    if VERBOSE: display(n)

@register()
def test_param_3():
    n = Node(head="@tmpl(oops=32) they said $oops today")
    n.head.render()
    assert n.head.view == "they said 32 today"
    if VERBOSE: display(n)

@register()
def test_param_4():
    n = Node(head="@pipe(to='sky') 1 + 1")
    n.head.render()
    assert n.head.view == 2
    if VERBOSE: display(n)

@register()
def test_param_5():
    n = Node(head="@xt('cheetah') 1 + $a")
    n.head.render()
    assert n.head.view == "1 + 2"
    if VERBOSE: display(n)

@register()
def test_param_6():
    n = Node(head="@attr(handsome='devil')")
    n.head.render()
    assert n.attributes['handsome'] == 'devil'
    if VERBOSE: display(n)

@register()
def test_person():
    "tests a class instance as directive"

    class Person(object):
        def __init__(self, name):
            self.name = name
        def __call__(self, **kwds):
            def _get_person(element):
                element.data = "Hello %s" % self.name
                return element.data
            return _get_person

    from leonode import directive
    person = Person('sam')

    # registers the instance as a directive
    # use this method until class decorators
    # become more popular
    p = directive('person', 'person-obj')(person)
    n = node1('@person says hello')
    if VERBOSE: display(n)

@register()
def test_csum_1():
    "tests the csum or child-sum function"

    n = node1('@csum')
    n1 = node1('sam = 10')
    n2 = node1('don = 30')
    n.children = [n1,n2]
    assert n.head.view == 40


@register()
def test_csum_2():
    "tests csum and namespace assignment"

    n = node1('@csum sandwhich')
    n1 = node1('cheese = 10')
    n2 = node1('pickle = 30')
    n.children = [n1,n2]
    assert n.head.view == 40
    assert 'sandwhich' in n.namespace

tree1 = get_tree(py_expr_1, py_suite_1, py_suite_2, imports_1, tmpl_1, pipe_1)


@register()
def test_del_view():
    root = tree1
    root.head.view = 'ok'
    assert root.head.view == 'ok'
    del root.head.view
    assert not root.head.cache['default']


@register()
def test_tree1():
    "test tree self-iteration"
    n = tree1
    assert n == n.namespace['node']
    for i in n:
        if VERBOSE: 
            print i.level, i.head.text

@register()
def test_redirectors():
    n = Node('a','b')
    n.children = [Node('x','y')]
    list(n)
    to = To(n)

    to.stdout('hello there')

    n1 = to()
    assert n1 == n

    to.head.data('c')
    assert n.head.data == 'c'

    to.head.code('e')
    assert n.head.code == 'e'

    to.head.view('m')
    assert n.head.view == 'm'

    to.body.code('f')
    assert n.body.code == 'f'

    to.body.data('d')
    assert n.body.data == 'd'

    to.body.view('h')
    assert n.body.view == 'h'

    nc = n.children[0]
    assert nc.parent == n

    to = To(nc)
    to.parent.body.data('ko')
    assert n.body.data == 'ko'

@register()
def test_pattern_1():
    matched_heads, matched_bodies = {}, {}
    unmatched_heads, unmatched_bodies = {}, {}
    for node in NODES:
        label = NODES[node].__name__
        for name in PATTERNS:
            p = PATTERNS[name]
            m = p.match(node.head.text)
            if m:
                if label in matched_heads:
                    matched_heads[label].append(name)
                else:
                    matched_heads[label] = [name]
            else:
                if label in unmatched_heads:
                    unmatched_heads[label].append(name)
                else:
                    unmatched_heads[label] = [name]
            m = p.match(node.body.text)
            if m:
                if label in matched_bodies:
                    matched_bodies[label].append(name)
                else:
                    matched_bodies[label] = [name]
            else:
                if label in unmatched_bodies:
                    unmatched_bodies[label].append(name)
                else:
                    unmatched_bodies[label] = [name]

    check_in = lambda k,d: int(k in d)
    sort = lambda d: sorted(d.keys())
    for node in NODES:
        label = NODES[node].__name__
        try: match = node.match
        except: match = ''
        head_matched = check_in(label, matched_heads)
        body_matched = check_in(label, matched_bodies)
        matched = (head_matched, body_matched)
        if VERBOSE:
            print label.ljust(20),':', match, '==' if (
                match==matched) else '!=', matched
        assert match == matched





dot_1 = node1(
    "@graph a -> b",
    """
    @graph
    d -> c
    d -> d
    c -> goodbye
    @
    data
    """
)


@register(dot_1, 1, 1)
def test_dot():
    n = dot_1
    standard(n)
    if VERBOSE: display(n)

#~ @register()
#~ def test_rss():
    #~ n = node1('@rss http://planet.python.org/rss10.xml')
    #~ n.render()
    #~ assert n.head.view
    #~ display(n)







doc_1 = node1(
    "@doc I like this",
    """
    @doc
    I mean really
    @
    data
    """
)

@register(doc_1, 1, 1)
def test_doc():
    n = doc_1
    n.render()
    assert n.head.doc == "I like this"
    assert n.body.doc == "I mean really"

shadow_1 = node1("@shadow ./love.py")

@register(shadow_1, 1, 0)
def test_shadow():
    n = shadow_1
    n.render()
    assert "./love.py" == n.head.node.attributes['path']


def _test():
    for t in TESTS:
        print
        headline(t.__name__.upper(), False, sep='=')
        t()

if __name__ == '__main__':
    mode = 'nose'
    if mode == 'test':
        try:
            import nose
            nose.run()
        except ImportError:
            print 'nose not available'
            _test()
    elif mode == 'test':
        _test()
    else:
        import cProfile
        cProfile.run('_test()', 'test_leofunc.profile')
        import pstats
        p = pstats.Stats('test_leofunc.profile')
        print '#'*70
        p.sort_stats('cumulative').print_stats(10)
        print '#'*70
        p.sort_stats('time').print_stats(10)



