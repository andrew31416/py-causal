from copy import deepcopy
from typing import List
from warnings import warn


from .node import Node
from .path import Path


class DirectedGraph:
    @classmethod
    def _get_path(cls,
                  target_node: Node,
                  path: List[Node],
                  paths: List[List[Node]]
                  ):
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

        When 2 nodes are d-connected, they are statistically correlated.
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

        When 2 nodes are d-connected, they are statistically correlated.
        """
        paths = cls.get_paths(node1, node2)

        res = [_p.is_conditionally_unblocked(node1, node2, conditioned_on)
                for _p in paths]

        return any(res)

    @classmethod
    def is_backdoor_criterion_satisfied(cls,
                                        treatment: Node,
                                        outcome: Node,
                                        conditioned_on: List[Node]
                                        ) -> bool:
        """
        Returns True if the backdoor criterion is satisfied for a given
        treatment, outcome node and a list of conditioned on variables.

        When the backdoor criterion between a treament and outnode is satisfied,
        conditioning on a list of variable values, we have blocked all
        non-causal paths between the treatment and outcome. This means that all
        non-causal statistical dependence between the treatment and outcome
        node has been removed.

        In other words, the causal effect of the treatment on the outcome
        variable is identifiable if we can observe the conditioned on set of
        variables.

        Conditions for criterion to be satisfied:
            - no conditioned on node is a child of the treatment node.
            - the list of variables that we condition on blocks, or d-separates,
              all paths between the treatment and outcome node. These paths must
              end with an arrow into the treatment node to be considered.
        """
        if any(list(map(treatment.has_child, conditioned_on))):
            return False

        # all paths between treatment and outcome nodes
        paths = cls.get_paths(treatment, outcome)

        # only paths that end with an arrow into treatment node
        paths = [_p for _p in paths if _p.is_backdoor_path(treatment, outcome)]

        if len(paths) < 1:
            # no backdoor paths between treatment, outcome nodes exist
            return True

        # backdoor criterion is satisfied when every backdoor path between
        # treatment and outcome is blocked by conditioned on variables
        return all([not _p.is_conditionally_unblocked(treatment,
                                                      outcome,
                                                      conditioned_on
                                                     )
                    for _p in paths])
    
    @classmethod
    def is_frontdoor_criterion_satisfied(cls,
                                         treatment: Node,
                                         outcome: Node,
                                         conditioned_on: List[Node]
                                         ) -> bool:
        """
        Returns True if the front door criterion is satisfied between the
        treatment and outcome node when conditioning on a given list of variable
        observations.

        The criterion is satisfied when all 3 criterion below are met:
            - The conditioned on nodes block all paths between treatment and
              outcome nodes.
            - There is no backdoor path from treatment to any of the conditioned
              on nodes.
            - All backdoor paths from conditioned on nodes to the outcome are
              blocked by conditioning on the treatment.
        """
        # dev warning
        warn('DirectedGraph.is_frontdoor_criterion_satisfied has not been tested')

        # all paths between treatment and outcome
        paths = cls.get_paths(treatment, outcome)

        # get directed paths only, arrows only propagate info from 
        # treatment to outcome
        paths = [_p for _p in paths if _p.is_directed_path(treatment, outcome)]

        # condition 1:
        # Z intercepts all directed paths from treatment to outcome
        for _path in paths:
            if not any([_z in _path.nodes for _z in conditioned_on]):
                return False

        # condition 2:
        # there is no unblocked back door path from treatment to Z
        for _Z in conditioned_on:
            paths = cls.get_paths(treatment, _Z)

            # back door paths
            paths = [_p for _p in paths if _p.is_backdoor_path(treatment, _Z)]

            if any([_p.is_unblocked(treatment, _Z) for _p in paths]):
                # there cannot be any unblocked backdoor paths between
                # treatment and conditioned on nodes
                return False

        # condition 3:
        # all back-door paths from Z to outcome are blocked by treatment
        for _Z in conditioned_on:
            # all paths between _Z and outcome
            paths = cls.get_paths(_Z, outcome)

            # backdoor paths only
            paths = [_p for _p in paths if _p.is_backdoor_path(_Z, outcome)]

            for _p in paths:
                if _p.is_conditionally_unblocked(_Z, outcome, [treatment]):
                    # all backdoor paths between _Z and outcome must be blocked
                    return False
        return True
