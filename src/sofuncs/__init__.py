"""List exported native functions in Linux shared objects (.so)."""

from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import subprocess
from typing import Iterable, List


@dataclass(frozen=True)
class ToolResult:
    tool: str
    symbols: List[str]


def _run_command(args: List[str]) -> str:
    result = subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout


def _parse_nm_output(output: str) -> List[str]:
    symbols = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        if len(parts) == 2:
            sym_type, name = parts
        else:
            _, sym_type, name = parts[:3]
        if sym_type in {"T", "t", "W", "w"}:
            symbols.append(name)
    return symbols


def _parse_readelf_output(output: str) -> List[str]:
    symbols = []
    for line in output.splitlines():
        if " FUNC " not in line:
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        name = parts[-1]
        symbols.append(name)
    return symbols


def _unique_sorted(items: Iterable[str]) -> List[str]:
    return sorted({item for item in items if item})


def list_native_functions(path: str, tool: str = "auto") -> ToolResult:
    """List exported function symbols from a Linux shared object.

    Args:
        path: Path to the .so file.
        tool: "auto", "nm", or "readelf".
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    if tool not in {"auto", "nm", "readelf"}:
        raise ValueError("tool must be 'auto', 'nm', or 'readelf'")

    tool_choice = tool
    if tool == "auto":
        if shutil.which("nm"):
            tool_choice = "nm"
        elif shutil.which("readelf"):
            tool_choice = "readelf"
        else:
            raise RuntimeError("Neither 'nm' nor 'readelf' is available")

    if tool_choice == "nm":
        output = _run_command(["nm", "-D", "--defined-only", path])
        symbols = _parse_nm_output(output)
    else:
        output = _run_command(["readelf", "--dyn-syms", path])
        symbols = _parse_readelf_output(output)

    return ToolResult(tool=tool_choice, symbols=_unique_sorted(symbols))


__all__ = ["list_native_functions", "ToolResult"]
