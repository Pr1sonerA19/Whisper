[index.md](https://github.com/user-attachments/files/32047732/index.md)
# Whisper documentation

- [Overview](#overview)
- [Install](#install)
- [CLI usage](#cli-usage)
- [Memory model](#memory-model)
- [Instruction reference](#instruction-reference)
- [Comments](#comments)
- [Tutorial: building a character from scratch](#tutorial-building-a-character-from-scratch)
- [Tutorial: loops](#tutorial-loops)
- [Examples](#examples)
- [Design notes](#design-notes)

## Overview

Whisper is an esoteric programming language built around one central
restriction: there's no instruction that adds 1 to a value. Every byte
you want has to be reached using only:

- `+2`
- `-1`
- `×2` (mod 256)
- `÷2` (floor)
- set to `9`
- set to `0`

Every value 0-255 is still reachable from 0 with these six operations —
it just takes some arithmetic. Whisper source files use the `.WIPE`
extension.

## Install

```bash
pip install whisper-lang
```

or, before it's on PyPI:

```bash
pip install git+https://github.com/Pr1sonerA19/whisper-lang.git
```

Both install a `whisper` command on your PATH.

## CLI usage

```bash
whisper path/to/program.WIPE
```

Flags:

| Flag | Effect |
|---|---|
| `--debug` | print a step-by-step execution trace (pointer, cell value, instruction) to stderr after every instruction |

Exit behavior:

- A syntax error (unmatched `[` or `]`) prints a message to stderr and exits with status 1.
- The `(` instruction exits immediately with status 0.
- Reaching the end of the program exits normally with status 0.

## Memory model

- The tape has **30,000 cells**, each holding an integer **0-255**.
- All cells start at **0**.
- The pointer starts at cell **0**.
- Pointer movement (`&` / `3`) always jumps by exactly **10 cells**,
  and wraps around at both ends of the tape.
- Arithmetic (`-`, `F`, `}`, `=`) always wraps or clamps into the
  0-255 range — nothing overflows or throws.
- The only way to reach a cell's immediate neighbors (`ptr+1` /
  `ptr-1`) is with `#`, `o`, `Y`, `!` — there is **no arbitrary/indexed
  addressing**. You cannot compute an address and jump to it; every
  move is either a fixed ±10 stride or a fixed ±1 neighbor peek.

That last point is the language's sharpest constraint: without
indexed addressing, you can't build lookup tables the way you would in
most languages. Any "which of N things do I want" decision has to be
made structurally (with loops and arithmetic), not by computing an
offset.

## Instruction reference

| Symbol | Effect |
|---|---|
| `@` | output the current cell as a character |
| `&` | move the pointer forward 10 cells (wraps) |
| `3` | move the pointer backward 10 cells (wraps) |
| `+` | read one byte of stdin into the current cell (0 on EOF) |
| `-` | add 2 to the current cell (mod 256) |
| `F` | subtract 1 from the current cell (mod 256) |
| `_` | output a newline |
| `)` | set the current cell to 0 |
| `(` | exit the program immediately |
| `L` | set the current cell to 9 |
| `>` | print the pointer position to stderr (debug aid) |
| `#` | copy the value from the next cell into the current cell |
| `Y` | swap the current cell with the next cell |
| `!` | swap the current cell with the previous cell |
| `o` | copy the value from the previous cell into the current cell |
| `}` | double the current cell (mod 256) |
| `=` | halve the current cell (floor division) |
| `[` | jump past the matching `]` if the current cell is 0 |
| `]` | jump back to the matching `[` if the current cell is not 0 |

Every other character — spaces, newlines, letters like `H` or `e`,
punctuation — is a **no-op**. It's skipped with no effect, which is
what lets you format and comment `.WIPE` files freely.

## Comments

A `;` starts a comment that runs to the end of the line:

```
L}}}  ; this text is ignored
```

This is worth calling out explicitly because Whisper reuses ordinary
letters (`F`, `L`, `Y`, `o`) and the digit `3` as instructions. Plain
English notes *without* a leading `;` are not safe — a word like "for"
contains a live `F` and `o`, and running it as code will quietly
corrupt whatever cell the pointer happens to be on.

## Tutorial: building a character from scratch

Say you want the ASCII code for `H`, which is 72. You start at 0 and
only have `+2`, `-1`, `×2`, `÷2`, set-9, and set-0 to work with.

A short path: set the cell to 9, then double it three times.

```
9 → 18 → 36 → 72
L   }    }    }
```

In Whisper: `L}}}`. Then `@` prints it:

```
L}}}@
```

Not every target is a clean chain of doublings. `e` is 101, and one
working path adds 2 twice before doubling: 9→11→13 (set-9, `+2`,
`+2`), then double twice to 52 (13→26→52), subtract 1 to 51, double to
102, subtract 1 to land on 101. In Whisper: `L--}}F}F`. There's more
than one way to reach most targets; shorter is nicer to read but not
required for correctness.

## Tutorial: loops

`[` and `]` work like a standard while-loop: *while the current cell
is not zero, run the body.* Combined with the fixed ±10 stride, this
gives you a clean way to process a run of cells without writing out
one instruction per cell.

For example, if cells 0, 10, 20, ... each hold a character's value,
followed by a cell that's still 0 (untouched), this loop prints all of
them and stops on its own:

```
[@&]
```

Trace through it: check the current cell — if it's 0, skip the loop
entirely; otherwise print it (`@`), move to the next station (`&`),
and check again. It naturally halts the first time it lands on a cell
that's still 0, so you don't need to track how many cells you built —
just make sure there's an untouched (zero) cell right after the last
one.

## Examples

- **`examples/hello.WIPE`** — builds each letter of "Hello, world!" at
  its own memory station, then prints them all with `[@&]`.
- **`examples/cat.WIPE`** — a 6-character program, `+[@&+]`, that
  reads stdin and echoes it back byte for byte until EOF. Run it
  against its own source and the output matches the file exactly:

  ```bash
  whisper examples/cat.WIPE < examples/cat.WIPE
  ```

  Worth noting: this only reproduces its own text because it's handed
  its own source *as input* at invocation time — it doesn't contain or
  reconstruct that text internally. It's a common practical answer for
  a language this constrained, but not a true quine in the strict
  sense (a program that reproduces its own source with no input).

## Design notes

A few open questions if you want to extend the language yourself:

- **Indexed addressing.** Adding an instruction to jump to an
  address stored in a cell (rather than always ±10 or ±1) would open
  up lookup tables and make a true, input-free quine dramatically more
  tractable.
- **A true quine.** Whisper currently has no known from-scratch quine.
  Because there are no string literals, every output character must be
  numerically rebuilt, and a naive per-character approach requires
  more source code than it produces — a real one would need a build
  sequence that happens to tile into repeats of itself, found by
  search rather than derived by hand.
- **More arithmetic.** Right now there's no subtraction of arbitrary
  amounts, no modulo other than the implicit 256-wrap, and no
  comparison other than "is this cell zero." Any of these would change
  what's easy versus hard to write in Whisper.
