__all__ = ["INCLUDE_NON_STD_LIB_PATTERN", "INCLUDE_STD_LIB_PATTERN"]

# TODO: relax the regex
# TODO: Take care of the unlikely case when standard lib is surrounded by "" instead of <> in the #include directive.
# TODO: take care of any corner/edge cases that we could think of.
# TODO: it's possible to include .cpp files
# TODO: it's possible to include .hpp files
# TODO: it's possible to include .tpp files
INCLUDE_NON_STD_LIB_PATTERN = r"#include\s+\"(.*\.(?:h|hpp|tpp))\""
INCLUDE_STD_LIB_PATTERN = r"#include\s+<(.*)>"

# TODO: rename "standard lbrary" to "system header"
