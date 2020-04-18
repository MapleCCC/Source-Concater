# Source-Concater

[![License](https://img.shields.io/github/license/MapleCCC/Source-Concater?color=00BFFF)](http://www.wtfpl.net/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Introduction

A Python script to automatically search for dependent source files and concatenate multiple source files together into one unified source file. It's useful when you are fed up with writing hard-to-remember Makefile syntax, and resolving all kinds of cryptic linker errors.

No need to write obscure Makefile recipes anymore. Simply concatenate source files and compile the single output file is all. Sweet and straighforward. Just one click.

No more bunch of linker errors to resolve.

Currently only support C/C++ language. More to come in the future.

## Installation

Prerequisites: Python>=3.6, [Git](https://git-scm.com/), [pip](https://pip.pypa.io/en/stable/).

```bash
$ git clone https://github.com/MapleCCC/Source-Concater.git

$ cd Source-Concater

# You can optionally create a virtual environment for isolation purpose
$ python -m virtualenv .venv
$ source .venv/Scripts/activate

# Install requirements
$ python -m pip install -r requirements.txt

# Install in editable mode
$ python -m pip install -e .  # Mind the dot at the end
```

## Usage

After installation, a command line tool `concat` is available for use.

```bash
$ concat main.cpp -I include -S src
'Wrote concated output to concated.cpp'

$ concat --help
'''
usage: Automatically Concatenate C/C++ Source Files [-h] [--build] [--cpp]
                                                    [-I [INCLUDE_DIR [INCLUDE_DIR ...]]]
                                                    [-S [SOURCE_DIR [SOURCE_DIR ...]]]
                                                    [-o OUTPUT]
                                                    entry

positional arguments:
  entry                 The entry source file to begin searching

optional arguments:
  -h, --help            show this help message and exit
  --build               Control whether to build the concatenated source file
                        after concatenation
  --cpp                 Specify language mode to be C++
  -I [INCLUDE_DIR [INCLUDE_DIR ...]], --include-dir [INCLUDE_DIR [INCLUDE_DIR ...]]
                        Sepcify search path for include headers. Can specify
                        multiple paths. Current working directory will be
                        inserted before all paths.
  -S [SOURCE_DIR [SOURCE_DIR ...]], --source-dir [SOURCE_DIR [SOURCE_DIR ...]]
                        Sepcify search path for source files corresponding to
                        headers. Can specify multiple paths. Current working
                        directory will be inserted before all paths.
  -o OUTPUT, --output OUTPUT
                        Specify output file name
'''
```

Optionally, use as module, progrmmatically

```python
from concat import concat_source

output = concat_source("main.lzw", include_dir="include", source_dir="src")
print(output)
```

## License

[WTFPL 2.0](./LICENSE)

[![WTFPL](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-1.png)](http://www.wtfpl.net/)
