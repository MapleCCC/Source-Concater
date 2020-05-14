# Source-Concater

[![License](https://img.shields.io/github/license/MapleCCC/Source-Concater?color=00BFFF)](http://www.wtfpl.net/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Introduction

A Python script to automatically search for dependent source files, and concatenate multiple source files together into one unified source file. It's useful when you are fed up with writing hard-to-remember Makefile syntax, and resolving all kinds of cryptic linker errors.

No need to write obscure Makefile recipes anymore. Simply concatenate source files and compile the single output file is all. Sweet and straighforward. Just one click.

No more bunch of linker errors to resolve.

**Currently only support C/C++ language**. More to come in the future.

## Installation

Prerequisites: Python>=3.6, [Git](https://git-scm.com/), [pip](https://pip.pypa.io/en/stable/).

One-liner installation recipe:

```bash
$ python -m pip install git+https://github.com/MapleCCC/Source-Concater.git
```

If editable mode installation is preferred:

```bash
# You can optionally create a virtual environment for isolation purpose
$ python -m virtualenv .venv
$ source .venv/Scripts/activate

# Install in editable mode
$ python -m pip install -e git+https://github.com/MapleCCC/Source-Concater.git
```

## Usage

After installation, a command line tool `concat` is available for use.

```bash
$ concat main.cpp -I include -S src
'Wrote concated output to concated.cpp'

$ concat --help
'''
usage: Automatically Concatenate C/C++ Source Files [-h]
                                                    [-I [INCLUDE_DIR [INCLUDE_DIR ...]]]
                                                    [-S [SOURCE_DIR [SOURCE_DIR ...]]]
                                                    [-o OUTPUT] [--format]
                                                    [--format-style FORMAT_STYLE]
                                                    [--format-fallback-style FORMAT_FALLBACK_STYLE]
                                                    entry

positional arguments:
  entry                 The entry source file to begin searching

optional arguments:
  -h, --help            show this help message and exit
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
  --format              Whether to format concated code with clang-format
  --format-style FORMAT_STYLE
                        Specify the clang-format style. Default is `file`,
                        which means first try to detect `.clang-format`
                        configuration file under the same directory with the
                        entry source file, and if not found, fall back to
                        internal fall-back format style.
  --format-fallback-style FORMAT_FALLBACK_STYLE
                        Specify the clang-format fallback style. Default is a
                        predefined value.
'''
```

Optionally, use as module, progrmmatically

```python
from concat import concat_source

output = concat_source("main.cpp", include_dir="include", source_dir="src")
print(output)
```

## Example

Suppose there are three files: `main.cpp`, `utils.h` and `utils.cpp`. The directory layout is:

```
.
 |-src
 | |-main.cpp
 | |-utils.cpp
 |-include
 | |-utils.h
```

And the file contents are:

```cpp
// content of main.cpp
#include <iostream>
#include "utils.h"

int main() {
  std::cout << int2str(10) << std::endl;
  return 0;
}
```

```cpp
// content of utils.h
#include <string>

std::string int2str(int);
```

```cpp
// content of utils.cpp
#include "utils.h"

std::string int2str(int x) {
  return "To Be Implemented";
}
```

After executing command `concat src/main.cpp -I include -S src`, a concated new file `concated.cpp` is generated.

```cpp
// content of concated.cpp
#include <iostream>
#include <string>

std::string int2str(int);

int main() {
    std::cout << int2str(10) << std::endl;
    return 0;
}

std::string int2str(int x) {
  return "To Be Implemented";
}
```

## License

[WTFPL 2.0](./LICENSE)

[![WTFPL](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-1.png)](http://www.wtfpl.net/)
