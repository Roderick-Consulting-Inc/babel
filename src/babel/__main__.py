# Copyright 2026 Roderick Consulting Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command-line entry point for the Babel runtime.

Two subcommands:

* ``babel run <yaml> --program <source>`` — interpret ``source`` against
  the language defined by the YAML parameter sheet, writing output to
  stdout.
* ``babel transpile <yaml> --program <source>`` — transpile ``source``
  to vanilla Brainfuck, writing the lowered source to stdout.

Either subcommand can read the program from stdin instead by passing
``--program -``.
"""

from __future__ import annotations

import argparse
import sys

from babel import run  # base-machine-dispatching entry point (v0.4.0)
from babel.loader import load_spec
from babel.transpiler import transpile


def _read_program(arg: str) -> str:
    if arg == "-":
        return sys.stdin.read()
    return arg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="babel", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="interpret a program against a parameter sheet")
    p_run.add_argument("yaml", help="path to the language parameter sheet (YAML)")
    p_run.add_argument(
        "--program",
        required=True,
        help="program source string, or '-' to read from stdin",
    )

    p_tx = sub.add_parser("transpile", help="transpile a program to vanilla Brainfuck")
    p_tx.add_argument("yaml", help="path to the source-language parameter sheet (YAML)")
    p_tx.add_argument(
        "--program",
        required=True,
        help="program source string, or '-' to read from stdin",
    )

    args = parser.parse_args(argv)

    spec = load_spec(args.yaml)
    program = _read_program(args.program)

    if args.command == "run":
        run(program, spec)
        return 0
    if args.command == "transpile":
        sys.stdout.write(transpile(program, spec))
        return 0

    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
