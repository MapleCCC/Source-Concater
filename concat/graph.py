from collections import defaultdict, deque
from typing import Dict, Iterator, List, Optional, Set, Tuple

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

    def add_edge(self, v: Node, w: Node) -> None:
        if not isinstance(v, str) or not isinstance(w, str):
            raise NotImplementedError
        if v == w:
            raise CircularDependencyError("Self-pointing dependency is not accepted")
        self._adjacency_list[v].add(w)
        self._adjacency_list[w]  # add w to adjacency list

    def add_node(self, node: Node) -> None:
        self._adjacency_list[node]

    def __contains__(self, node: Node) -> bool:
        return node in self._adjacency_list

    def bfs(self, source: Node) -> Iterator[Node]:
        assert source in self._adjacency_list
        queue = deque([source])
        traversed = set()
        while queue:
            node = queue.popleft()
            if node in traversed:
                continue
            yield node
            traversed.add(node)
            queue.extend(self._adjacency_list[node])

    # Optionally, we can implement dfs in iterative manner instead of recursive manner.
    # The main difference is whether user-maintain stack or runtime stack is used to contain information.
    def dfs(self, source: Node) -> Iterator[Node]:
        traversed = set()
        yield from self._dfs(source, traversed)

    def _dfs(self, node: Node, traversed: Set[Node]) -> Iterator[Node]:
        assert node in self._adjacency_list
        if node in traversed:
            return
        yield node
        traversed.add(node)
        for child in self._adjacency_list[node]:
            yield from self._dfs(child, traversed)

    def detect_back_edge(self, source: Node) -> Optional[Edge]:
        assert source in self._adjacency_list
        stack = [source]
        current_path: List[Optional[Node]] = [None]
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

    def topological_sort(self) -> Iterator[Node]:
        def find_sources(graph: Graph) -> Set[Node]:
            adjlist = graph._adjacency_list
            sources = set(adjlist.keys())
            for children in adjlist.values():
                sources -= children
            return sources

        def remove_sources(graph: Graph) -> Set[Node]:
            srcs = find_sources(graph)
            for src in srcs:
                del graph._adjacency_list[src]
            for node in graph._adjacency_list:
                graph._adjacency_list[node] -= srcs
            return srcs

        _graph = self.copy()
        srcs = remove_sources(_graph)
        while srcs:
            yield from srcs  # type: ignore
            srcs = remove_sources(_graph)

    def __str__(self) -> str:
        return "Graph({})".format(dict(self._adjacency_list))

    # TODO: ensure that eval(repr(x)) == x
    def __repr__(self) -> str:
        return self.__str__()


if __name__ == "__main__":
    g = Graph()
    g.add_edge("0", "1")
    g.add_edge("1", "2")
    g.add_edge("0", "3")
    g.add_edge("3", "4")
    g.add_edge("1", "4")
    g.add_edge("4", "2")
    print(g)
    print(list(g.bfs("0")))
    print(list(g.dfs("0")))
    print(list(g.topological_sort()))
