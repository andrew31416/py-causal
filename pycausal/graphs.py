from copy import deepcopy
from typing import List


from .node import Node
from .path import Path


class DirectedGraph:
    @classmethod
    def _get_path(cls, target_node: Node, path: List[Node], paths: List[List[Node]]):
        current_node = path[-1]

        for _n in current_node.adjacent_nodes:
            # check for _n.id in existing path

            if not _n.id in [_p.id for _p in path]:
                new_path = deepcopy(path)
                new_path.append(_n)

                if _n.id != target_node.id:
                    cls._get_path(target_node, new_path, paths)
                else:
                    paths.append(new_path)

    @classmethod
    def get_paths(cls, start_node: Node, end_node: Node) -> List['Path']:
        paths = []
        cls._get_path(target_node=end_node, path=[start_node], paths=paths)
        return [Path(_p) for _p in paths]
    
    @classmethod
    def is_d_connected(cls, node1: Node, node2: Node) -> bool:
        """
        Returns True if node1 and node2 are d connected. This occurs when at
        least 1 unblocked path between node1 and node2 exists.
        """
        paths = cls.get_paths(node1, node2)

        return any([_p.is_unblocked(node1, node2) for _p in paths])
     
    @classmethod
    def is_conditionally_d_connected(cls,
                                     node1: Node,
                                     node2: Node,
                                     conditioned_on: List[Node]
                                     ) -> bool:
        """
        Returns True if node1 and node2 are d connected after conditioning on
        a given set of variables. This occurs if at least one conditionally
        unblocked path exists between the 2 nodes.
        """
        paths = cls.get_paths(node1, node2)

        res = [_p.is_conditionally_unblocked(node1, node2, conditioned_on)
                for _p in paths]

        return any(res)
