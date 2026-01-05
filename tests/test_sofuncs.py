import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from sofuncs import list_native_functions


@pytest.mark.skipif(platform.system() != "Linux", reason="Requires Linux shared objects")
def test_list_native_functions(tmp_path: Path) -> None:
    if shutil.which("gcc") is None:
        pytest.skip("gcc is required to build test shared object")

    source = tmp_path / "sample.c"
    lib = tmp_path / "libsample.so"

    source.write_text(
        """
        #include <stdio.h>
        static int hidden(int x) { return x + 1; }
        int add(int a, int b) { return a + b; }
        void hello(void) { puts(\"hello\"); }
        """,
        encoding="ascii",
    )

    subprocess.run(
        ["gcc", "-shared", "-fPIC", "-o", str(lib), str(source)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    result = list_native_functions(str(lib))
    assert "add" in result.symbols
    assert "hello" in result.symbols
    assert "hidden" not in result.symbols


@pytest.mark.skipif(platform.system() != "Linux", reason="Requires Linux shared objects")
def test_cli_output(tmp_path: Path) -> None:
    if shutil.which("gcc") is None:
        pytest.skip("gcc is required to build test shared object")

    source = tmp_path / "sample.c"
    lib = tmp_path / "libsample.so"

    source.write_text(
        """
        int add(int a, int b) { return a + b; }
        void hello(void) {}
        """,
        encoding="ascii",
    )

    subprocess.run(
        ["gcc", "-shared", "-fPIC", "-o", str(lib), str(source)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = str(repo_root / "src")

    result = subprocess.run(
        [sys.executable, "-m", "sofuncs", str(lib)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    output = set(result.stdout.splitlines())
    assert "add" in output
    assert "hello" in output
