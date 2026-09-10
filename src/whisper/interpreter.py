"""
Whisper — an esoteric programming language.

Whisper programs consist of the following instructions. Every other
character (whitespace, letters not listed below, punctuation used for
comments, etc.) is ignored, so program authors are free to format and
annotate their .WIPE files however they like.

    @   output the current cell as a character
    &   move the pointer forward 10 cells (wraps around)
    3   move the pointer backward 10 cells (wraps around)
    +   read one byte of stdin into the current cell
    -   add 2 to the current cell (mod 256)
    F   subtract 1 from the current cell (mod 256)
    _   output a newline
    )   set the current cell to 0
    (   exit the program immediately
    L   set the current cell to 9
    >   print the current pointer position (debug aid)
    #   copy the value from the next cell into the current cell
    Y   swap the current cell with the next cell
    !   swap the current cell with the previous cell
    o   copy the value from the previous cell into the current cell
    }   double the current cell (mod 256)
    =   halve the current cell (floor division)
    [   jump past the matching ] if the current cell is 0
    ]   jump back to the matching [ if the current cell is not 0

Memory is a tape of 30,000 cells, each holding a byte (0-255), wrapping
in both directions.

Comments: a ';' begins a comment that runs to the end of the line. This
matters because Whisper reuses ordinary letters (F, L, Y, o) as
instructions, so plain-English notes are NOT safe as bare text — always
prefix them with ';'.
"""

import argparse
import sys

MEMORY_SIZE = 30000
FILE_EXTENSION = ".WIPE"


def _strip_comments(code):
    """Remove ';' -> end-of-line comments before execution."""
    return "\n".join(line.split(";", 1)[0] for line in code.split("\n"))


class WhisperSyntaxError(Exception):
    """Raised when a Whisper program has malformed loop brackets."""


def _build_loop_map(code):
    """Pair up '[' and ']' instructions, or raise WhisperSyntaxError."""
    stack = []
    loop_map = {}
    for i, char in enumerate(code):
        if char == "[":
            stack.append(i)
        elif char == "]":
            if not stack:
                raise WhisperSyntaxError(
                    f"unmatched ']' at position {i}"
                )
            start = stack.pop()
            loop_map[start] = i
            loop_map[i] = start
    if stack:
        raise WhisperSyntaxError(
            f"unmatched '[' at position {stack[-1]}"
        )
    return loop_map


def run(code, debug=False, out=sys.stdout, in_=sys.stdin):
    """Execute a Whisper program (a string of source code)."""
    code = _strip_comments(code)
    memory = [0] * MEMORY_SIZE
    ptr = 0
    code_ptr = 0

    loop_map = _build_loop_map(code)

    while code_ptr < len(code):
        char = code[code_ptr]

        if char == "@":
            out.write(chr(memory[ptr]))
        elif char == "&":
            ptr = (ptr + 10) % MEMORY_SIZE
        elif char == "3":
            ptr = (ptr - 10) % MEMORY_SIZE
        elif char == "+":
            byte = in_.read(1)
            memory[ptr] = ord(byte) if byte else 0
        elif char == "-":
            memory[ptr] = (memory[ptr] + 2) % 256
        elif char == "F":
            memory[ptr] = (memory[ptr] - 1) % 256
        elif char == "_":
            out.write("\n")
        elif char == ")":
            memory[ptr] = 0
        elif char == "(":
            out.flush()
            sys.exit(0)
        elif char == "L":
            memory[ptr] = 9
        elif char == ">":
            print(ptr, file=sys.stderr)
        elif char == "#":
            memory[ptr] = memory[(ptr + 1) % MEMORY_SIZE]
        elif char == "Y":
            nxt = (ptr + 1) % MEMORY_SIZE
            memory[ptr], memory[nxt] = memory[nxt], memory[ptr]
        elif char == "!":
            prv = (ptr - 1) % MEMORY_SIZE
            memory[ptr], memory[prv] = memory[prv], memory[ptr]
        elif char == "o":
            memory[ptr] = memory[(ptr - 1) % MEMORY_SIZE]
        elif char == "}":
            memory[ptr] = (memory[ptr] * 2) % 256
        elif char == "=":
            memory[ptr] = memory[ptr] // 2
        elif char == "[":
            if memory[ptr] == 0:
                code_ptr = loop_map[code_ptr]
        elif char == "]":
            if memory[ptr] != 0:
                code_ptr = loop_map[code_ptr]

        if debug and char in "@&3+-F_)L#Y!o}=[]":
            print(
                f"[{code_ptr:>5}] {char!r:>4}  ptr={ptr:<6} "
                f"cell={memory[ptr]}",
                file=sys.stderr,
            )

        code_ptr += 1

    out.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="whisper",
        description="Run a Whisper (.WIPE) esoteric language program.",
    )
    parser.add_argument("file", help="path to a .WIPE source file")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print a step-by-step execution trace to stderr",
    )
    args = parser.parse_args(argv)

    if not args.file.endswith(FILE_EXTENSION):
        print(
            f"warning: '{args.file}' does not end in '{FILE_EXTENSION}' "
            "— running it anyway",
            file=sys.stderr,
        )

    try:
        with open(args.file, "r") as f:
            source = f.read()
    except OSError as e:
        print(f"whisper: could not read '{args.file}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        run(source, debug=args.debug)
    except WhisperSyntaxError as e:
        print(f"whisper: syntax error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
