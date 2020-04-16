from collections import defaultdict
from typing import *

# TODO: generalize Node data type, so that it can contain generic types of data
# Currently we only support str as node type.

# Thin semantic type abstraction
Node = str
Edge = Tuple[Node, Node]
AdjacencyList = Dict[Node, Set[Node]]


class CircularDependencyError(Exception):
    pass


# Graph is represented internally as data structure adjacency list
class Graph:
    def __init__(self) -> None:
        self._adjacency_list: AdjacencyList = defaultdict(set)

    __slots__ = "_adjacency_list"

    def add_edge(self, edge: Edge) -> None:
        v, w = edge
        if not isinstance(v, str) or not isinstance(w, str):
            raise NotImplementedError
        self._adjacency_list[v].add(w)

    def has_node(self, node: Node) -> bool:
        return node in self._adjacency_list

    def bfs(self, source: Node) -> Generator[Node, Any, Any]:
        assert source in self._adjacency_list
        q = [source]
        traversed = set()
        while q:
            for node in q:
                yield node
                traversed.add(node)
                for child in self._adjacency_list[node]:
                    if child not in traversed:
                        q.append(child)

    def dfs(self, source: Node) -> Generator[Node, Any, Any]:
        assert source in self._adjacency_list
        stack = [source]
        traversed = set()
        while stack:
            for node in stack[::-1]:
                yield node
                traversed.add(node)
                for child in self._adjacency_list[node]:
                    if child not in traversed:
                        stack.append(child)

    def detect_back_edge(self, source: Node) -> Optional[Edge]:
        assert source in self._adjacency_list
        stack = [source]
        current_path = [None]
        while stack:
            node = stack[-1]
            if node != current_path[-1]:
                current_path.append(node)
                for child in self._adjacency_list[node]:
                    if child in current_path:
                        return (node, child)
                    stack.append(child)
            else:
                stack.pop()
                current_path.pop()
        return None

    def get_invert_graph(self) -> "Graph":
        new_adjlist = dict()
        for key in self._adjacency_list.keys():
            new_adjlist[key] = set()
        for node, children in self._adjacency_list.items():
            for child in children:
                new_adjlist[child].add(node)

        new_graph = Graph()
        new_graph._adjacency_list = new_adjlist
        return new_graph

    def copy(self) -> "Graph":
        # Deep copy
        new_adjlist = dict()
        for node, children in self._adjacency_list.items():
            new_adjlist[node] = children.copy()
        new_graph = Graph()
        new_graph._adjacency_list = new_adjlist
        return new_graph

    def topological_sort(self) -> Generator[Node, Any, Any]:
        def find_sources(graph: Graph) -> Set[Node]:
            adjlist = graph._adjacency_list
            sources = set(adjlist.keys())
            for children in adjlist.values():
                for child in children:
                    if child in sources:
                        sources.remove(child)
            return sources

        def remove_sources(graph: Graph) -> Set[Node]:
            srcs = find_sources(graph)
            for src in srcs:
                del graph._adjacency_list[src]
            return srcs

        _graph = self.copy()
        srcs = remove_sources(_graph)
        while srcs:
            for src in srcs:
                yield src
            srcs = remove_sources(_graph)
