__all__ = ["DEFAULT_FORMATTER", "DEFAULT_FORMAT_STYLE", "DEFAULT_FORMAT_FALLBACK_STYLE"]

# TODO: possibly expose a public interface to let user specify the binary clang-format's path
DEFAULT_FORMATTER = "clang-format"

DEFAULT_FORMAT_STYLE = "file"

# TODO: break into multi-line string
DEFAULT_FORMAT_FALLBACK_STYLE = (
    "{BasedOnStyle: Google, "
    + "IndentWidth: 4, "
    + "AlwaysBreakAfterReturnType: TopLevelDefinitions, "
    + "SortIncludes: true, "
    + "IncludeBlocks: Regroup}"
)
