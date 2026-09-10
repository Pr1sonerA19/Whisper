import io
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from whisper.interpreter import run, WhisperSyntaxError


def run_and_capture(code, stdin_text=""):
    out = io.StringIO()
    in_ = io.StringIO(stdin_text)
    run(code, out=out, in_=in_)
    return out.getvalue()


def test_set_9_and_double():
    # L sets cell to 9, } doubles it, @ prints it as a char (chr(18))
    assert run_and_capture("L}@") == chr(18)


def test_add_two():
    assert run_and_capture("--@") == chr(4)


def test_subtract_one_wraps():
    assert run_and_capture("F@") == chr(255)


def test_newline():
    assert run_and_capture("_") == "\n"


def test_pointer_moves_and_wraps():
    # move forward then back should return to the same cell
    assert run_and_capture("L&3@") == chr(9)


def test_loop_runs_until_zero():
    # build 4 -> loop: print then decrement by 1 each time until 0
    code = "--[@F]"
    assert run_and_capture(code) == chr(4) + chr(3) + chr(2) + chr(1)


def test_comment_is_ignored():
    code = "L ; this comment mentions F L Y o and 3 but should be inert\n}@"
    assert run_and_capture(code) == chr(18)


def test_unmatched_open_bracket_raises():
    with pytest.raises(WhisperSyntaxError):
        run_and_capture("L[@")


def test_unmatched_close_bracket_raises():
    with pytest.raises(WhisperSyntaxError):
        run_and_capture("L@]")


def test_stdin_read():
    assert run_and_capture("+@", stdin_text="Z") == "Z"


def test_hello_world_example():
    path = os.path.join(
        os.path.dirname(__file__), "..", "examples", "hello.WIPE"
    )
    with open(path) as f:
        code = f.read()
    assert run_and_capture(code) == "Hello, world!\n"
