## TODO

- Add cli option to remove multiple-inclusion guard
- Add testing. Add unit test for Graph class.
- Add cli argument to not concatenate excluded headers.
- How to handle `extern`
- Use clang's Python binding to extract AST, analyze AST, reformat.
- parser.add_argument("--dump-makefile")
- Add feature: dump dependencies. Useful in specifying Makefile prerequisite.
- Remove the assumption that include directives are each in a single line. Need syntax analysis then.
- Automate testing. Setup pytest workflow.
- Add support for more language.
- Use some pre-existed library to detect programming language (with some confidence). Refer to the chardet library.
- Use click or fire to replace argparse.

## Done

- Add cli argument to specify output filepath
- Use pathlib.Path to replace plain str. Improve readability. Construct proper abstraction (i.e. Path type to represent path).
- Polish the newline numbers. Remove trailing blank space of removed include directives.
- Rename "standard include" to "system header"
- Update README
- Add use example in README


