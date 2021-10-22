from copy import deepcopy
from typing import List


from .node import Node


class Path:
    """
    Representation of and utilities for paths between connected nodes
    """
    UNDIRECTED: str = '-'
    DIRECTED_LEFT: str = '<-'
    DIRECTED_RIGHT: str = '->'

    def __init__(self, nodes: List[Node]):
        self.nodes = deepcopy(nodes)

    def __len__(self) -> int:
        return len(self.nodes)
    
    def __str__(self):
        N = len(self.nodes)-1

        relations = [self.edge_type(self.nodes[ii], self.nodes[ii+1])
                     for ii in range(N)]

        out = "".join([f'{self.nodes[ii]}{relations[ii]}' for ii in range(N)])
        return out+f'{self.nodes[-1]}'
    
    def __eq__(self, other: 'Path') -> bool:
        if len(self) != len(other):
            return False

        def _eq(nodes1: List[Node], nodes2: List[Node]):
            return all([nodes1[ii]==nodes2[ii] for ii in range(len(nodes1))])

        if _eq(self.nodes, other.nodes):
            return True
        elif _eq(self.nodes, Path.reverse(other).nodes):
            # make __eq__ invariant to order of self.nodes
            return True
        else:
            return False

    def edge_type(self, node1: Node, node2: Node) -> str:
        """
        node1 <edge_type> node2
        """
        if not (node1.already_adjacent_to(node2) and node2.already_adjacent_to(node1)):
            raise ValueError(f'nodes {node1.name} and {node2.name}'
                             + ' are not adjacent'
                             )

        # location of node2 in node1.adjacent_nodes list
        idx = [ii for ii, _n in enumerate(node1.adjacent_nodes)
               if _n.id == node2.id][0]

        # relation of node2 to node1
        relation = node1.adjacent_edges[idx]
            
        if relation == Node.CHILD:
            # node2 is a child of node1
            return Path.DIRECTED_RIGHT
        elif relation == Node.PARENT:
            # node2 is a parent of node1, node1 is a child of node2
            return Path.DIRECTED_LEFT
        elif relation == Node.UNDIRECTED:
            return Path.UNDIRECTED
        else:
            raise Exception(f'Unsupported node relation {relation}')
    
    def location_in_path(self, node: Node) -> int:
        """
        Returns the integer index [0, len(self.nodes)-1] inclusive of the 
        location of node in self.nodes.
        """
        idx = [ii for ii, _n in enumerate(self.nodes) if _n.id == node.id]

        if len(idx) < 1:
            raise Exception(f'node {node.name} cannot be found in the path.')

        return idx[0]

    def is_collider(self, node: Node) -> bool:
        """
        Returns True is node is connected to parents such that

        parent of node -> node <- parent of node
        """
        idx = self.location_in_path(node)

        if idx == 0 or idx == len(self.nodes)-1:
            return False
        elif self.edge_type(self.nodes[idx-1], node) != Path.DIRECTED_RIGHT:
            return False
        elif self.edge_type(node, self.nodes[idx+1]) != Path.DIRECTED_LEFT:
            return False

        return True
    
    def has_collider(self) -> bool:
        """
        Returns true if path has a collider node
        """
        return any(list(map(self.is_collider, self.nodes)))

    @classmethod
    def reverse(cls, path: 'Path') -> 'Path':
        """
        Returns a new Path instance, whose node order is the reverse of the
        supplied path.
        """
        return Path(path.nodes[::-1])

    def is_unblocked(self, node1: Node, node2: Node) -> bool:
        """
        Returns True if both nodes are present in the path and not separated 
        by a collider node. If nodes are not d-connected, then no stastical
        correlation can occur between them.
        """
        if not self.is_node_in_path(node1, node2):
            # at least one nodes not present in path
            return False

        return not self.get_subpath(node1, node2).has_collider()

    def is_conditionally_unblocked(self,
                                   node1: Node,
                                   node2: Node,
                                   condition_on: List[Node]
                                   ):
        """
        Returns True if node1 and node2 are connected, given that we condition
        on explicit values of a list of observed variables.

        For the path between node1 and node2 to be connected given the
        explicit variable values that we condition on, the path cannot contain
        any member of the conditioned set.
        """
        if len(condition_on) < 1:
            raise ValueError('Must condition on at least 1 variable.')
        
        subpath = self.get_subpath(node1, node2)

        if any(list(map(subpath.is_node_in_path, condition_on))):
            # path cannot contain any variables that are conditioned on
            return False
        
        if subpath.has_collider():
            # colliders in subpath not do block the path, IF collider has a
            # child in the conditioned on set of variables

            colliders = [_n for _n in subpath.nodes if subpath.is_collider(_n)]

            for _collider in colliders:
                children = _collider.get_children()

                if len(children) > 0:
                    if any([_c in condition_on for _c in children]):
                        # nodes are d connected because child of a collider 
                        # is in the condition on set of variables
                        return True

            # colliders are present in path between nodes but no collider 
            # children exist in the condition on set of variables
            return False

            # NOTE: what happens if both collider node and it's child are in the
            # conditioned on set of variables??

        return True

    def is_node_in_path(self, *args) -> bool:
        """
        Returns True if all Node instances in args is present in self.nodes
        """
        return all([_node.id in [_n.id for _n in self.nodes] for _node in args])

    def get_subpath(self, node1: Node, node2: Node) -> 'Path':
        """
        Returns the subpath that begins and terminates with node1 and node2.
        """
        if not self.is_node_in_path(node1, node2):
            raise ValueError('At least one node is missing from the path')

        # keep order of self.nodes
        indices = sorted(list(map(self.location_in_path, [node1, node2])))

        return Path(self.nodes[indices[0]: indices[1]+1])
