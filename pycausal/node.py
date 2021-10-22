import numpy as np
from typing import List


class Node:
    PARENT: str = 'parent'
    CHILD: str = 'child'
    UNDIRECTED: str = 'undirected'

    def __init__(self, name: str):
        self.name = name
        self.id = id(self)
        self.adjacent_nodes = []
        self.adjacent_edges = []

    def __eq__(self, other: 'Node') -> bool:
        return self.id == other.id

    def __ne__(self, other: 'Node') -> bool:
        return self.id != other.id

    def __str__(self) -> str:
        return self.name

    def already_adjacent_to(self, node: 'Node') -> bool:
        """
        Returns True if node is already in self.adjacent_nodes
        """
        return node.id in [_n.id for _n in self.adjacent_nodes]

    def _add_adjacent_node(self, node: 'Node', edge_type: str):
        if not self.already_adjacent_to(node):
            self.adjacent_nodes.append(node)
            self.adjacent_edges.append(edge_type)

        if not node.already_adjacent_to(self):
            if edge_type == Node.CHILD:
                getattr(node, 'add_parent')(self)
            elif edge_type == Node.PARENT:
                getattr(node, 'add_child')(self)

    def add_child(self, node: 'Node'):
        self._add_adjacent_node(node, Node.CHILD)

    def add_parent(self, node: 'Node'):
        self._add_adjacent_node(node, Node.PARENT)

    def _query_dependency(self, node: 'Node', edge_type: str) -> bool:
        """
        Returns true if node is a dependent of edge_type of self and False
        otherwise
        """
        idx = np.where([_e==edge_type for _e in self.adjacent_edges])[0]

        if len(idx) < 1:
            return False

        return any([self.adjacent_nodes[ii].id==node.id for ii in idx])

    def has_child(self, node: 'Node') -> bool:
        """
        Returns True if node is a child of self, False otherwise.
        """
        return self._query_dependency(node, Node.CHILD)

    def has_parent(self, node: 'Node') -> bool:
        """
        Returns True if node is a parent of self, False otherwise.
        """
        return self._query_dependency(node, Node.PARENT)
    
    def _get_dependents(self, edge_type: str) -> List['Node']:
        return [_n for ii, _n in enumerate(self.adjacent_nodes)
                    if self.adjacent_edges[ii]==edge_type]

    def get_children(self) -> List['Node']:
        """
        Returns list of children to this node. List is empty if no children
        exist.
        """
        return self._get_dependents(Node.CHILD)

    def get_parents(self) -> List['Node']:
        """
        Returns list of parents to this node. List is empty if no parents
        exist.
        """
        return self._get_dependents(Node.PARENTS)
