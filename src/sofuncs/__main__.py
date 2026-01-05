"""CLI entrypoint for listing functions in shared objects."""

from __future__ import annotations

import argparse
import sys

from . import list_native_functions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List exported native functions from a Linux .so"
    )
    parser.add_argument("path", help="Path to the .so file")
    parser.add_argument(
        "--tool",
        choices=["auto", "nm", "readelf"],
        default="auto",
        help="Symbol listing backend",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    result = list_native_functions(args.path, tool=args.tool)
    for name in result.symbols:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
