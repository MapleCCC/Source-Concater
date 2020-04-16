#!/usr/bin/env python3

import argparse
import os
import subprocess
from pprint import PrettyPrinter
from typing import *

from .extract_dependencies import (
    extract_dependencies_of_file,
    get_dependencies_of_library,
    move_include_std_lib_directive_to_top,
    remove_include_non_std_lib_directive,
)
from .graph import *
from .utils import get_file_content, write_file_content, get_implem_from_header

print = PrettyPrinter().pprint

# TODO: implement in more sane way. Reduce McCabe complexity. Consider use queue.
def generate_graph(entry: str) -> Graph:
    graph = Graph()
    waitlist = {entry}
    while waitlist:
        newlist = set()
        for elem in waitlist:
            if not graph.has_node(elem):
                if elem.endswith(".h"):
                    deps = get_dependencies_of_library(elem)
                else:
                    deps = extract_dependencies_of_file(elem)
                for dep in deps:
                    graph.add_edge((elem, dep))
                    if not graph.has_node(dep):
                        newlist.add(dep)
        waitlist = newlist
    return graph


def concat_source(entry: str) -> str:
    graph = generate_graph(entry)
    back_edge = graph.detect_back_edge(entry)
    if back_edge:
        raise CircularDependencyError(
            f"Circular dependency detected!: '{back_edge[0]}'->'{back_edge[1]}'"
        )

    inv = graph.get_invert_graph()
    topo_sorted = list(inv.topological_sort())
    headers = topo_sorted[:-1]
    implems = list(filter(None, map(get_implem_from_header, headers)))
    concated = headers + [entry] + implems[::-1]  # type: ignore

    # insert blank line between file contents
    output = "\n".join(map(get_file_content, concated))
    output = remove_include_non_std_lib_directive(output)
    output = move_include_std_lib_directive_to_top(output)

    return output


def main():
    parser = argparse.ArgumentParser("Concatenate C Source Files")
    parser.add_argument("entry")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--cpp", action="store_true")
    # parser.add_argument("-I", "--include-dir")
    # parser.add_argument("-s", "--source-dir")
    # parser.add_argument("--mode")
    # parser.add_argument("-o", "--output")
    args = parser.parse_args()

    output = concat_source(args.entry)

    lang_mode = "cpp" if args.cpp or args.entry.endswith(".cpp") else "c"

    output_filename = "concated.cpp" if lang_mode == "cpp" else "concated.c"
    # Consider use flag "x" (ie, exclusive creation)
    write_file_content(output_filename, output)
    print(f"Wrote concated output to {output_filename}")

    if args.build:
        # Alternative, use clang/clang++ as compiler
        compiler = "g++" if lang_mode == "cpp" else "gcc"
        exe_name = os.path.splitext(os.path.basename(args.entry))[0]

        complproc = subprocess.run([compiler, output_filename, "-o", exe_name])
        if complproc.returncode == 0:
            print("Build succeeds")
        else:
            print("Build failed")


if __name__ == "__main__":
    main()
