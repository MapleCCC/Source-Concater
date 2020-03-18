import argparse
import re
import os
from typing import *
from pprint import PrettyPrinter
from collections import defaultdict

# print = PrettyPrinter().pprint

Node = str
Edge = Tuple[Node, Node]
# Graph is represented internally as data structure adjacency list
Graph = Dict[Node, Set[Node]]


class CircularDependencyError(Exception):
    pass


# TODO: implement Graph data structure as class. More integrated and streamlined.
# class Graph:
#     def __init__(self, ):
#         self._storage =


# Naive and simple path join utility.
# Further revision is required to enhance portability and robustness.
def join_path(*paths) -> str:
    return "/".join(filter(lambda path: path is not "", paths))


# TODO: relax the regex
# TODO: Take care of the unlikely case when standard lib is surrounded by "" instead of <> in the #include directive.
# TODO: take care of any corner/edge cases that we could think of.
INCLUDE_PATTERN = r"#include \"(.*\.h)\"\n"


def extract_dependencies(filepath: str) -> Set[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        matches = (re.fullmatch(INCLUDE_PATTERN, line) for line in f.readlines())
        return set(
            # WARNING: On Windows, os.sep is '\\' (ie, a backslash character).
            # But the header file path in C file's #include directive uses '/' most of time.
            # We should not use os.path.join to do the path join job if we want portability.
            # os.path.join(os.path.dirname(filepath), match.group(1))
            join_path(os.path.dirname(filepath), match.group(1))
            for match in matches
            if match
        )


# TODO: implement in more sane way. Use queue.
# TODO: add detection of circular
def generate_graph(entry: str) -> Graph:
    graph = dict()
    waitlist = {entry}
    while waitlist:
        newlist = set()
        for elem in waitlist:
            if elem not in graph:
                deps = extract_dependencies(elem)
                graph[elem] = deps
                for dep in deps:
                    if dep not in graph:
                        newlist.add(dep)
        waitlist = newlist
    return graph


def bfs(source: Node, graph: Graph) -> Generator[Node, Any, Any]:
    assert source in graph
    q = [source]
    traversed = set()
    while q:
        for node in q:
            yield node
            traversed.add(node)
            for child in graph[node]:
                if child not in traversed:
                    q.append(child)


def dfs(source: Node, graph: Graph) -> Generator[Node, Any, Any]:
    assert source in graph
    stack = [source]
    traversed = set()
    while stack:
        for node in stack[::-1]:
            yield node
            traversed.add(node)
            for child in graph[node]:
                if child not in traversed:
                    stack.append(child)


def detect_back_edge(source: Node, graph: Graph) -> Optional[Edge]:
    assert source in graph
    stack = [source]
    current_path = [None]
    while stack:
        node = stack[-1]
        if node != current_path[-1]:
            current_path.append(node)
            for child in graph[node]:
                if child in current_path:
                    return (node, child)
                stack.append(child)
        else:
            stack.pop()
            current_path.pop()
    return None


def get_invert_graph(graph: Graph) -> Graph:
    new_graph: Graph = dict()
    for key in graph.keys():
        new_graph[key] = set()
    for node, children in graph.items():
        for child in children:
            new_graph[child].add(node)
    return new_graph


def copy_graph(graph: Graph) -> Graph:
    new_graph = dict()
    for node, children in graph.items():
        new_graph[node] = children.copy()
    return new_graph


def topological_sort(graph: Graph) -> Generator[Node, Any, Any]:
    def find_sources(graph: Graph) -> Set[Node]:
        sources = set(graph.keys())
        for children in graph.values():
            for child in children:
                if child in sources:
                    sources.remove(child)
        return sources

    def remove_sources(graph: Graph) -> Set[Node]:
        srcs = find_sources(graph)
        for src in srcs:
            del graph[src]
        return srcs

    _graph = copy_graph(graph)
    srcs = remove_sources(_graph)
    while srcs:
        for src in srcs:
            yield src
        srcs = remove_sources(_graph)


def get_file_content(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# TODO: further revision is needed to add robustness to the search
# Heuristic search
# Return None is no corresponding implementation file is found
def get_implem_from_header(filepath: str) -> Optional[str]:
    # sanity check
    assert filepath.endswith(".h")
    implem = filepath[: -len(".h")] + ".c"
    if os.path.isfile(implem):
        return implem
    return None


def remove_include_directive(file: str) -> str:
    return "".join(
        line
        for line in file.splitlines(keepends=True)
        if not re.fullmatch(INCLUDE_PATTERN, line)
    )


def main():
    parser = argparse.ArgumentParser("Concatenate C Source Files")
    parser.add_argument("entry")
    args = parser.parse_args()
    entry = args.entry

    graph = generate_graph(entry)
    back_edge = detect_back_edge(args.entry, graph)
    if back_edge:
        raise CircularDependencyError(
            f"Circular dependency detected!: '{back_edge[0]}'->'{back_edge[1]}'"
        )

    inv = get_invert_graph(graph)
    topo_sorted = list(topological_sort(inv))
    headers = topo_sorted[:-1]
    implems = list(filter(None, map(get_implem_from_header, headers[::-1])))
    concated = headers + [entry] + implems  # type: ignore

    # insert blank line between headers
    output = "\n".join(map(remove_include_directive, map(get_file_content, concated)))

    with open("concated.c", "w", encoding="utf-8") as f:
        f.write(output)


if __name__ == "__main__":
    main()
