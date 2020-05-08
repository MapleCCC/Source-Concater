## TODO

- Add cli option to remove multiple-inclusion guard
- Add testing. Add unit test for Graph class.
- Add cli argument to not concatenate excluded headers.
- How to handle `extern`
- Use clang's Python binding to extract AST, analyze AST, reformat.
- Rename "standard include" to "system header"
- parser.add_argument("--dump-makefile")
- Add feature: dump dependencies. Useful in specifying Makefile prerequisite.
- Update README
- Add use example in README
- Remove the assumption that include directives are each in a single line. Need syntax analysis then.

## Done

- Add cli argument to specify output filepath
- Use pathlib.Path to replace plain str. Improve readability. Construct proper abstraction (i.e. Path type to represent path).
- Polish the newline numbers. Remove trailing blank space of removed include directives.


