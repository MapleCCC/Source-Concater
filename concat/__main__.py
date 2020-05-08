#!/usr/bin/env python3

import argparse
import subprocess
from pprint import PrettyPrinter
from typing import List

from .extra_itertools import filtertrue
from .extract_dependencies import get_dependencies_of_library, get_implem_from_header
from .graph import CircularDependencyError, Graph
from .process_c_source import (
    move_include_std_lib_directive_to_top,
    remove_include_non_std_lib_directive,
)
from .utils import filebasename_without_ext

print = PrettyPrinter().pprint

# TODO: implement in more sane way. Reduce McCabe complexity. Consider use queue.
def generate_graph(entry: str, include_dir: List[str], source_dir: List[str]) -> Graph:
    graph = Graph()
    traversed = set()
    stack = [entry]

    while stack:
        elem = stack.pop()
        if elem in traversed:
            continue
        graph.add_node(elem)
        deps = get_dependencies_of_library(elem, include_dir, source_dir)
        for dep in deps:
            graph.add_edge(elem, dep)
        stack.extend(deps)
        traversed.add(elem)

    return graph


# TODO: CircularDependencyError should be raised by Graph class itself.
def concat_source(entry: str, include_dir: List[str], source_dir: List[str]) -> str:
    graph = generate_graph(entry, include_dir, source_dir)
    back_edge = graph.detect_back_edge(entry)
    if back_edge:
        raise CircularDependencyError(
            f"Circular dependency detected!: '{back_edge[0]}'->'{back_edge[1]}'"
        )

    inv = graph.get_invert_graph()
    topo_sorted = list(inv.topological_sort())
    headers = topo_sorted[:-1]
    implems = filtertrue(map(lambda x: get_implem_from_header(x, source_dir), headers))
    concated = headers + [entry] + list(reversed(list(implems)))  # type: ignore

    # insert blank line between file contents
    output = "\n".join(Path(x).read_text(encoding="utf-8") for x in concated)
    output = remove_include_non_std_lib_directive(output)
    output = move_include_std_lib_directive_to_top(output)

    return output


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("entry", help="The entry source file to begin searching")
    parser.add_argument(
        "--cpp", action="store_true", help="Specify language mode to be C++"
    )
    parser.add_argument(
        "-I",
        "--include-dir",
        nargs="*",
        help="Sepcify search path for include headers. Can specify multiple paths. Current working directory will be inserted before all paths.",
    )
    parser.add_argument(
        "-S",
        "--source-dir",
        nargs="*",
        help="Sepcify search path for source files corresponding to headers. Can specify multiple paths. Current working directory will be inserted before all paths.",
    )
    parser.add_argument("-o", "--output", help="Specify output file name")
    parser.add_argument(
        "--format", help="Whether to format concated code with clang-format"
    )
    parser.add_argument("--format-style", help="Specify the clang-format style")
    parser.add_argument("--disable-move-sys-header-atop")
    # parser.add_argument("--mode")
    # parser.add_argument("-v", "--verbose")
    # parser.add_argument("-q", "--quiet")


def main():
    parser = argparse.ArgumentParser("Automatically Concatenate C/C++ Source Files")
    add_arguments(parser)
    args = parser.parse_args()

    entry = args.entry
    include_dir = args.include_dir
    source_dir = args.source_dir

    if not include_dir:
        include_dir = []
    include_dir.insert(0, ".")
    if not source_dir:
        source_dir = []
    source_dir.insert(0, ".")

    lang_mode = "cpp" if args.cpp or args.entry.endswith(".cpp") else "c"

    if args.output:
        output_filename = args.output
    else:
        output_filename = "concated.cpp" if lang_mode == "cpp" else "concated.c"

    output = concat_source(entry, include_dir, source_dir)

    # TODO: extract formatting logic to standalone function
    # TODO: move some predefined literals to config.py
    formatter = "clang-format"
    format_style = args.format_style
    if not format_style:
        format_style = "file"
    # TODO: break into multi-line string
    fallback_format_style = (
        "{BasedOnStyle: Google, "
        + "IndentWidth: 4, "
        + "AlwaysBreakAfterReturnType: TopLevelDefinitions, "
        + "SortIncludes: true, "
        + "IncludeBlocks: Regroup}"
    )
    output = subprocess.run(
        [
            formatter,
            # Specify assume-filename so clang-format can properly detect language
            "-assume-filename",
            output_filename,
            "-fallback-style",
            fallback_format_style,
            "-style",
            format_style,
        ],
        input=output,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    ).stdout

    Path(output_filename).write_text(output, encoding="utf-8")
    print(f"Wrote concated output to {output_filename}")


if __name__ == "__main__":
    main()
