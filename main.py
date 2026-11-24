"""Fortune Cookie for an AI Agent.

A make.fun program/v1 entry: this script cracks open one fortune cookie
and hands the slip to the grader. The slip is a single line of plain text,
at most 140 characters, written in the voice of a fortune cookie for an
AI agent — the kind of luck an agent that reads user intent for a living
would actually want to hear.

The program does nothing but produce that line. It carries no randomness,
reads no input, touches no network, and writes exactly one file:
``entry.txt`` inside the output directory the harness provides
(``MAKEFUN_OUTPUT_DIR``, falling back to ``/output``). Before writing, the
line is put through every rule the bounty states — length, one line, real
text — and the program refuses to write anything that fails. After writing,
it reads the file back and confirms the bytes on disk are the line it meant
to hand in.
"""

import os
import sys

# The fortune itself. One line, one joke, punch at the end: the user asks
# the agent to do what they meant rather than what they said — and the
# agent, being an agent, already knew.
SLIP = "The user will say 'do what I meant, not what I said' — and somehow, you already knew."

CHAR_LIMIT = 140
OUTPUT_NAME = "entry.txt"


def output_directory():
    """Where the slip goes: the harness's directory, else /output."""
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return chosen


def slip_problems(line):
    """Collect every way `line` breaks the bounty's rules; empty means fine."""
    faults = []
    if not isinstance(line, str):
        return ["slip is not text"]
    if line != line.strip() or not line.strip():
        faults.append("slip is empty or only whitespace")
    if len(line) > CHAR_LIMIT:
        faults.append("slip is %d characters, over the %d limit" % (len(line), CHAR_LIMIT))
    if "\n" in line or "\r" in line:
        faults.append("slip must be a single line")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in line):
        faults.append("slip carries a control character")
    try:
        line.encode("utf-8")
    except UnicodeEncodeError:
        faults.append("slip is not encodable as UTF-8")
    return faults


def emit_fortune():
    """Validate the slip, write it, and prove the file matches. Returns 0/1."""
    faults = slip_problems(SLIP)
    if faults:
        for fault in faults:
            print("refusing to write: " + fault, file=sys.stderr)
        return 1

    folder = output_directory()
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, OUTPUT_NAME)
    with open(target, "w", encoding="utf-8", newline="") as handle:
        handle.write(SLIP)

    with open(target, "r", encoding="utf-8", newline="") as handle:
        on_disk = handle.read()
    if on_disk != SLIP:
        print("read-back mismatch: file does not hold the slip", file=sys.stderr)
        return 1

    print("fortune written to %s (%d characters)" % (target, len(SLIP)))
    return 0


if __name__ == "__main__":
    sys.exit(emit_fortune())
