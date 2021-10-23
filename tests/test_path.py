from copy import deepcopy


from pycausal.path import Path
from pycausal.node import Node


def test_str():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    # n1->n2<-n3
    n1.add_child(n2)
    n3.add_child(n2)

    path = Path([n1, n2, n3])

    LEFT = Path.DIRECTED_LEFT
    RIGHT = Path.DIRECTED_RIGHT

    assert f'{path}' == f'{n1}{RIGHT}{n2}{LEFT}{n3}'
    

def test_collider():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    # n1->n2<-n3
    n1.add_child(n2)
    n3.add_child(n2)

    path = Path([n1, n2 , n3])

    assert path.is_collider(n2)
    assert not path.is_collider(n1)
    assert not path.is_collider(n3)


def test_edge_type():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    # n1->n2<-n3
    n1.add_child(n2)
    n3.add_child(n2)

    path = Path([n1, n2 , n3])

    assert path.location_in_path(n1) == 0
    assert path.location_in_path(n2) == 1
    assert path.location_in_path(n3) == 2

    assert path.edge_type(n1, n2) == Path.DIRECTED_RIGHT
    assert path.edge_type(n2, n3) == Path.DIRECTED_LEFT


def test_equal():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    # n1->n2<-n3
    n1.add_child(n2)
    n3.add_child(n2)

    p1 = Path([n1, n2 , n3])
    p2 = Path([n1, n2])

    assert p1!=p2
    assert p1==p1
    assert p1==deepcopy(p1)

    # Path.__eq__ is invariant under permutation or node order
    p3 = Path([n2, n1])
    assert p2==p3


def test_reverse():
    n1 = Node('n1')
    n2 = Node('n2')

    n1.add_child(n2)

    p1 = Path([n1, n2])
    p2 = Path.reverse(p1)

    assert p2.nodes == [n2, n1]


def test_node_in_path():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    n1.add_child(n2)
    n2.add_child(n3)

    path = Path([n1, n2])

    assert path.is_node_in_path(n1)
    assert path.is_node_in_path(n1, n2)
    assert not path.is_node_in_path(n3)
    # all supplied nodes must be in path
    assert not path.is_node_in_path(n1, n3)


def test_subpath():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    n1.add_child(n2)
    n2.add_child(n3)

    # n3->n2->n1
    path = Path([n3, n2, n1])
    # n2->n1
    subpath = path.get_subpath(n1, n2)
    # should preserver original node order
    assert subpath.nodes == [n2, n1]


def test_has_collider():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    n1.add_child(n2)
    n3.add_child(n2)

    # collider free path
    path1 = Path([n1, n2])

    # n2 is a collider: n1->n2<-n3
    path2 = Path([n1, n2, n3])

    assert not path1.has_collider()
    assert path2.has_collider()
    assert path2.is_collider(n2)


def test_is_connected():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    n1.add_child(n2)
    n3.add_child(n2)

    # collider free path
    path1 = Path([n1, n2])

    # n2 is a collider: n1->n2<-n3
    path2 = Path([n1, n2, n3])

    assert path1.is_unblocked(n1, n2)
    assert path2.is_unblocked(n1, n2)
    assert path2.is_unblocked(n2, n3)
    assert not path2.is_unblocked(n1, n3)


def test_is_conditionally_unblocked():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')
    n4 = Node('n4')

    n1.add_child(n2)
    n3.add_child(n2)
    n3.add_child(n4)

    # n1->n2<-n3->n4
    path = Path([n1, n2, n3, n4])

    # n3 blocks path from n1 to n4 when conditioned on
    # collider n2 blocks path from n1 to n4
    assert not path.is_conditionally_unblocked(n1, n4, [n3])

    # conditioning on a collider means that collider no longer blocks path
    assert path.is_conditionally_unblocked(n1, n4, [n2])

    # lets add a child to the collider node
    n5 = Node('n5')
    # n1->n2<-n3->n4
    #      v
    #     n5
    n2.add_child(n5)

    # path deepcopies nodes, so need to reinstantiate Path
    path = Path([n1, n2, n3, n4])

    # conditioning on n5 should now connect n1 and n4
    assert path.is_conditionally_unblocked(n1, n4, [n5])
    # n3 still blocks the path
    assert not path.is_conditionally_unblocked(n1, n4, [n3, n5])

    #---------------------------#
    # larger scale just for fun #
    x = Node('x')
    r = Node('r')
    w = Node('w')
    s = Node('s')
    t = Node('t')
    p = Node('p')
    u = Node('u')
    v = Node('v')
    q = Node('q')
    y = Node('y')

    x.add_child(r)
    r.add_child(w)
    r.add_child(s)
    s.add_child(t)
    t.add_child(p)
    u.add_child(t)
    u.add_child(v)
    v.add_child(q)
    v.add_child(y)

    path = Path([x, r, s, t, u, v, y])

    assert path.is_conditionally_unblocked(s, y, [p])
    assert not path.is_conditionally_unblocked(x, u, [r, p])
    #---------------------------#


def test_is_backdoor_path():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')

    # n1<-n2<-n3
    n2.add_child(n1)
    n3.add_child(n2)

    path = Path([n1, n2, n3])

    assert path.is_backdoor_path(treatment=n1, outcome=n3)
    assert not path.is_backdoor_path(treatment=n2, outcome=n1)


def test_is_directed_path():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')
    n4 = Node('n4')

    # n1->n2<-n3->n4
    n1.add_child(n2)
    n3.add_child(n2)
    n3.add_child(n4)

    path = Path([n1 ,n2, n3 , n4])
    assert path.is_directed_path(n1, n2)
    assert not path.is_directed_path(n1, n3)
    assert not path.is_directed_path(n1, n4)
    assert not path.is_directed_path(n2, n4)
    assert path.is_directed_path(n3, n4)
    assert path.is_directed_path(n3, n2)
