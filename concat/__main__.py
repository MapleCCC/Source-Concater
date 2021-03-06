#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List

from .config import DEFAULT_FORMAT_FALLBACK_STYLE, DEFAULT_FORMAT_STYLE
from .extra_itertools import filtertrue
from .extract_dependencies import get_dependencies_of_library, get_implem_from_header
from .graph import Graph
from .process_c_source import (
    move_include_sys_header_directive_to_top,
    reformat_source,
    remove_include_non_sys_header_directive,
)


def generate_graph(
    entry: Path, include_dir: List[Path], source_dir: List[Path]
) -> Graph:
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


def concat_source(entry: Path, include_dir: List[Path], source_dir: List[Path]) -> str:
    graph = generate_graph(entry, include_dir, source_dir)
    inv = graph.get_invert_graph()
    topo_sorted = list(inv.topological_sort())
    headers = topo_sorted[:-1]
    implems = filtertrue(map(lambda x: get_implem_from_header(x, source_dir), headers))
    concated = headers + [entry] + list(reversed(list(implems)))  # type: ignore

    # insert blank line between file contents
    output = "\n".join(file.read_text(encoding="utf-8") for file in concated)
    # Add file-end newline to be POSIX-compatible
    if output and output[-1] != "\n":
        output += "\n"
    output = remove_include_non_sys_header_directive(output)
    output = move_include_sys_header_directive_to_top(output)

    return output


# TODO: break long string literals into multi-line, to enhance readability.
def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("entry", help="The entry source file to begin searching")
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
        "--format",
        action="store_true",
        default=False,
        help="Whether to format concated code with clang-format",
    )
    parser.add_argument(
        "--format-style",
        default=DEFAULT_FORMAT_STYLE,
        help="Specify the clang-format style. Default is `file`, which means first try to detect `.clang-format` configuration file under the same directory with the entry source file, and if not found, fall back to internal fall-back format style.",
    )
    parser.add_argument(
        "--format-fallback-style",
        default=DEFAULT_FORMAT_FALLBACK_STYLE,
        help="Specify the clang-format fallback style. Default is a predefined value.",
    )
    parser.add_argument("--disable-move-sys-header-atop")
    # parser.add_argument("--mode")
    # parser.add_argument("-v", "--verbose")
    # parser.add_argument("-q", "--quiet")
    # parser.add_argument("--dump-makefile")


def main() -> None:
    parser = argparse.ArgumentParser("Automatically Concatenate C/C++ Source Files")
    add_arguments(parser)
    args = parser.parse_args()

    entry = Path(args.entry)

    include_dir = args.include_dir
    source_dir = args.source_dir
    if not include_dir:
        include_dir = []
    include_dir.insert(0, ".")
    include_dir = list(map(Path, include_dir))
    if not source_dir:
        source_dir = []
    source_dir.insert(0, ".")
    source_dir = list(map(Path, source_dir))

    lang = entry.suffix

    if args.output:
        output_filename = args.output
    else:
        output_filename = "concated" + lang

    output = concat_source(entry, include_dir, source_dir)

    if args.format:
        reformat_source(
            output, args.format_style, args.format_fallback_style, output_filename
        )

    out_file = Path(output_filename)
    if not out_file.exists():
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.touch()
    out_file.write_text(output, encoding="utf-8")
    print(f"Wrote concated output to {output_filename}")


if __name__ == "__main__":
    main()
