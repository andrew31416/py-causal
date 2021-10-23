from copy import deepcopy


from pycausal.node import Node


def test_create():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    # add directed dependency
    n1.add_child(n2)
    assert n1.already_adjacent_to(n2)
    assert n2.already_adjacent_to(n1)
    assert n1.adjacent_edges[0]==Node.CHILD
    assert n2.adjacent_edges[0]==Node.PARENT

    # add directed dependency
    n3.add_parent(n2)
    assert n2.already_adjacent_to(n3)
    assert n3.already_adjacent_to(n2)
    assert n2.adjacent_edges[1]==Node.CHILD
    assert n3.adjacent_edges[0]==Node.PARENT

    assert n1.has_child(n2)
    assert n2.has_parent(n1)
    assert n3.has_parent(n2)
    assert n2.has_child(n3)
    assert not n1.has_parent(n2)
    assert not n2.has_child(n1)
    assert not n3.has_child(n2)
    assert not n2.has_parent(n3)


def test_str():
    name = 'n1'

    n1 = Node(name)
    assert n1.name == name
    assert f'{n1}' == name


def test_equal():
    n1 = Node('n1')
    n2 = Node('n2')

    assert n1!=n2
    assert n1==n1
    # deepcopy should copy Node.id
    assert n1==deepcopy(n1)
