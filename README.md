# Whisper

[![tests](https://github.com/Pr1sonerA19/whisper-lang/actions/workflows/test.yml/badge.svg)](https://github.com/Pr1sonerA19/whisper-lang/actions/workflows/test.yml)

Whisper is an esoteric programming language with no direct way to add 1
to a value. You get `+2`, `-1`, `×2`, `÷2`, "set to 9", and "set to 0" —
and that's the whole toolbox for building numbers. The memory pointer
can only leap 10 cells at a time, though neighboring cells can always
peek at and swap with each other.

Whisper source files use the `.WIPE` extension.

## Install

```bash
pip install whisper-lang
```

Or straight from GitHub, before it's published to PyPI:

```bash
pip install git+https://github.com/Pr1sonerA19/whisper-lang.git
```

Either way, this installs a `whisper` command.

## Quick start

```bash
whisper examples/hello.WIPE
```

```
Hello, world!
```

That file looks like this — one line builds each letter's ASCII value
from scratch (there's no direct `+1`, only `+2`/`-1`/`×2`/`÷2`/set-9/
set-0), then a single loop prints them all:

```
; Whisper has no comment syntax of its own, but every character
; outside the instruction set is a no-op — so plain-English notes
; work fine as long as they avoid F, L, Y, o, and the digit 3.

; --- build phase: construct one letter per memory station ---
; each station is 10 cells apart; & advances to the next one
L}}}&              ; H
L--}}F}F&           ; e
L--}}-}&            ; l
L--}}-}&            ; l
FF}}}F}=&           ; o
L-}}&               ; ,
LF}}&               ; (space)
FF}}F}=&            ; w
FF}}}F}=&           ; o
FFF}F}}=&           ; r
L--}}-}&            ; l
L--}F}}&            ; d
F===-               ; !

; --- rewind to station 0 ---
333333333333

; --- print phase: one loop replaces 13 manual print/move pairs ---
[@&]
_
```

Run with `--debug` to see a step-by-step execution trace on stderr:

```bash
whisper --debug examples/hello.WIPE
```

Full instruction reference, a build-your-own-character walkthrough, and
more examples live in **[the documentation](docs/index.md)**.

## Language reference

Memory is a tape of 30,000 byte cells (0-255), wrapping in both
directions. Every character not listed below is a no-op, so you're
free to format and comment code however you like.

The full instruction table, a comments guide, and a step-by-step
walkthrough of building a character from scratch are in
**[the documentation](docs/index.md)**.

## Examples

- `examples/hello.WIPE` — the classic "Hello, world!", built one
  character per memory station and printed with a single loop.
- `examples/cat.WIPE` — reads stdin and echoes it back byte for byte.
  Feed it its own source and it reproduces the file exactly:
  `whisper examples/cat.WIPE < examples/cat.WIPE`.

## Development

```bash
git clone https://github.com/Pr1sonerA19/whisper-lang.git
cd whisper-lang
pip install -e ".[dev]"
pytest
```

## License

MIT
