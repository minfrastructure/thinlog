"""Internal helpers for parsing stack traces."""


def parse_stack_info(stack_str: str) -> list[dict[str, str | int | None]]:
    """
    Parse a 'stack_info' string without regex, returning a list of structlog.tracebacks.Stack.

    :param stack_str: A string like that from logging.error(..., stack_info=True)
    :return: A list of Stack objects (usually of length 1), each with its frames populated.
    """
    frames: list[dict[str, str | int | None]] = []
    lines = stack_str.splitlines()

    for idx, raw in enumerate(lines):
        line = raw.strip()
        # We're looking for lines that start with: File "..."
        if not line.startswith("File "):
            continue

        # Remove the leading 'File '
        remainder = line[len("File ") :]  # '"<path>", line 12, in func_name'
        # 1) extract filename between the first pair of quotes
        if not remainder.startswith('"'):
            continue
        end_quote = remainder.find('"', 1)
        if end_quote == -1:
            continue
        filename = remainder[1:end_quote]

        # 2) skip past '",'
        remainder = remainder[end_quote + 1 :].lstrip()
        if remainder.startswith(","):
            remainder = remainder[1:].lstrip()

        # 3) expect 'line '
        if not remainder.startswith("line "):
            continue
        remainder = remainder[len("line ") :]  # '123, in func_name'

        # 4) split off the line number before the next comma
        comma = remainder.find(",")
        if comma == -1:
            continue
        lineno_str = remainder[:comma].strip()
        try:
            lineno = int(lineno_str)
        except ValueError:
            continue

        # 5) skip past ','
        remainder = remainder[comma + 1 :].lstrip()
        # 6) expect 'in '
        if remainder.startswith("in "):
            func_name = remainder[len("in ") :].strip()
        else:
            func_name = remainder

        code_line = None
        if idx + 1 < len(lines):
            nxt = lines[idx + 1]
            if nxt.startswith(" ") and not nxt.strip().startswith("File "):
                code_line = nxt.strip()

        frames.append(
            dict(
                filename=filename,
                lineno=lineno,
                name=func_name,
                line=code_line,
            )
        )

    if not frames:
        return []

    return frames
