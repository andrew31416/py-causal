from pycausal.graphs import DirectedGraph
from pycausal.node import Node
from pycausal.path import Path


def test_get_paths_acylic():
    """
    Test DirectedGraph.get_paths for acylic graphs
    """
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')
    n4 = Node('n4')
    n5 = Node('n5')

    n1.add_child(n2)
    n2.add_child(n3)
    n2.add_child(n4)
    n3.add_child(n5)
    n4.add_child(n5)

    # return paths between n1 and n5 (inclusive)
    paths = DirectedGraph.get_paths(n1, n5)

    # should get:
    # n1->n2->n3->n5
    # n1->n2->n4->n5
    p1 = Path([n1, n2, n3, n5])
    p2 = Path([n1, n2, n4, n5])
    assert len(paths)==2
    assert paths == [p1, p2] or paths == [p2, p1]


def test_get_paths_cylic():
    """
    Test DirectedGraph.get_paths for cylic graphs
    """

    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')
    n4 = Node('n4')

    n1.add_child(n2)
    n2.add_child(n3)
    n3.add_child(n1)
    n1.add_child(n4)
    n4.add_child(n3)

    paths = DirectedGraph.get_paths(n1, n3)

    # should get:
    # n1->n2->n3
    # n1->n4->n3
    # n1<-n3
    p1 = Path([n1, n2, n3])
    p2 = Path([n1, n4, n3])
    p3 = Path([n1, n3])

    assert len(paths)==3
    # to equate list, must match order of elements
    # DirectedGraph.get_paths returns an unsorted list of Paths
    combinations = [[p1, p2, p3],
                    [p1, p3, p2],
                    [p2, p1, p3],
                    [p2, p3, p2],
                    [p3, p1, p2],
                    [p3, p2, p1]]
    assert sum([_list==paths for _list in combinations])==1


def test_is_d_connected():
    n1 = Node('n1')
    n2 = Node('n2')
    n3 = Node('n3')
    n4 = Node('n4')

    # paths between n1 and n4:
    # n1->n2<-n3->n4
    # n1->n4
    # paths between n1 and n3:
    # n1->n2<-n3
    # n1->n4<-n3
    n1.add_child(n2)
    n3.add_child(n2)
    n3.add_child(n4)
    n1.add_child(n4)

    assert DirectedGraph.is_d_connected(n1, n4)
    # blocked by colliders n2 and n4
    assert not DirectedGraph.is_d_connected(n1, n3)

    n5 = Node('n5')
    # add children to collider so that can be conditioned on
    n2.add_child(n5)

    # need to condition on children of only 1 collider to open a path
    # n1->n2<-n3
    #     v
    #     n5
    # is unblocked path from n1 to n3 when we condition on n5
    assert DirectedGraph.is_conditionally_d_connected(n1, n3, [n5])


def test_is_backdoor_criterion_satisfied():
    #-----------#
    # Example 1 #
    xi = Node('xi') # treatment in this example
    xj = Node('xj') # outcome in this example
    x1 = Node('x1')
    x2 = Node('x2')
    x3 = Node('x3')
    x4 = Node('x4')
    x5 = Node('x5')
    x6 = Node('x6')

    xi.add_parent(x3) # back door path
    xi.add_parent(x4) # back door path
    xi.add_child(x6)  # front door path
    x6.add_child(xj)
    x3.add_parent(x1)
    x1.add_child(x4)
    x4.add_parent(x2)
    x4.add_child(xj)
    x2.add_child(x5)
    x5.add_child(xj)

    assert DirectedGraph.is_backdoor_criterion_satisfied(treatment=xi,
                                                         outcome=xj,
                                                         conditioned_on=[x3, x4],
                                                         )
    assert DirectedGraph.is_backdoor_criterion_satisfied(treatment=xi,
                                                         outcome=xj,
                                                         conditioned_on=[x4, x5],
                                                         )
    assert not DirectedGraph.is_backdoor_criterion_satisfied(treatment=xi,
                                                             outcome=xj,
                                                             conditioned_on=[x4],
                                                             )
    #-----------#

    #-----------#
    # Example 2 #
    x = Node('x')
    y = Node('y')
    z = Node('z')

    z.add_child(x)
    z.add_child(y)
    x.add_child(y)

    assert DirectedGraph.is_backdoor_criterion_satisfied(treatment=x,
                                                         outcome=y,
                                                         conditioned_on=[z]
                                                         )
    #-----------#


def test_is_frontdoor_criterion_satisfied():
    x = Node('x')
    y = Node('y')
    z = Node('z')
    u = Node('u')

    x.add_child(z)
    z.add_child(y)
    u.add_child(y)
    u.add_child(x)

    assert DirectedGraph.is_frontdoor_criterion_satisfied(x, y, [z])
