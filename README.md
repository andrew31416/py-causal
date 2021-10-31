# py-causal
A module for analysing directed acyclic causal graphs. This is an implementation of some of the techniques for causal reasoning described in Judea Pearl's *Causal inference in statistics: An overview* [[1]](https://ftp.cs.ucla.edu/pub/stat_ser/r350.pdf "[1]"). One of the applications that this work can be used for is to design experiments. By analysing a causal graph using the techniques described by Pearl, variable sets can be identified which are necessary to observe and measure in order to identify the causal effect of one variable on another.


```Python
from pycausal.node import Node
from pycausal.graphs import DirectedGraph


# Causal graph from Figure 4 of  Judea Pearl, Causal Inference in Statistics
xi = Node('xi') # treatment in this example
xj = Node('xj') # outcome in this example
x1 = Node('x1')
x2 = Node('x2')
x3 = Node('x3')
x4 = Node('x4')
x5 = Node('x5')
x6 = Node('x6')

xi.add_parent(x3)
xi.add_parent(x4)
xi.add_child(x6)
x6.add_child(xj)
x3.add_parent(x1)
x1.add_child(x4)
x4.add_parent(x2)
x4.add_child(xj)
x2.add_child(x5)
x5.add_child(xj)

sets = DirectedGraph.get_admissible_sets(xi, xj)

for _set in sets:
	# by conditioning on the nodes in each _set, the causal effect of xi
	# on xj is identifiable as the backdoor criterion is satisfied
    print(', '.join([_n.name for _n in _set]))
```

### Install
Please download or git clone the repository and run

``
python setup.py install
``

from the repository root.

### Status
This is a pre-release and in active development.