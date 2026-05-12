EXIT_STDIN = 3
EXIT_EVAL = 4
EXIT_OUTPUT = 5


class JpqError(Exception):
    """Base class for jpq errors. Subclasses set `exit_code`."""

    exit_code: int = 1


class StdinError(JpqError):
    """Input on stdin was not valid JSON (or unreadable)."""

    exit_code = EXIT_STDIN


class EvalError(JpqError):
    """The expression failed to parse or raised at runtime."""

    exit_code = EXIT_EVAL


class OutputError(JpqError):
    """The result could not be serialized to JSON."""

    exit_code = EXIT_OUTPUT
