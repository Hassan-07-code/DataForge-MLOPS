"""
DataForge Backend Verification Runner

Run from the project root:

    python check_backend.py

The script:
1. Verifies the backend package exists.
2. Compiles all backend Python files.
3. Imports all backend modules to catch import/dependency errors.
4. Runs the complete unit-test suite.
5. Stops immediately when a stage fails.
6. Optionally runs coverage after all unit tests pass.

This is intentionally a single reusable entry point so you do not
need to create/run separate verification scripts for each backend file.
"""

from __future__ import annotations


import importlib

import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
TESTS = ROOT / "tests" / "unit"


def header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def fail(message: str) -> int:
    print(f"\n[FAIL] {message}")
    print("\nBackend verification stopped.")
    return 1


def run_command(command: list[str], title: str) -> int:
    header(title)
    print(">", " ".join(command))
    print()

    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        print(f"\n[FAIL] Command exited with code {result.returncode}")
        return result.returncode

    print(f"\n[PASS] {title}")
    return 0


def discover_backend_files() -> list[Path]:
    return sorted(
        p for p in BACKEND.rglob("*.py")
        if "__pycache__" not in p.parts
    )


def compile_backend(files: list[Path]) -> int:
    header("1/4  Python syntax / compilation check")

    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
        except Exception as exc:
            print(f"[FAIL] {path.relative_to(ROOT)}")
            print(f"       {type(exc).__name__}: {exc}")
            return 1

    print(f"[PASS] Compiled {len(files)} backend Python files.")
    return 0


def import_backend(files: list[Path]) -> int:
    header("2/4  Backend import check")

    # Convert backend/foo/bar.py -> backend.foo.bar
    modules: list[str] = []

    for path in files:
        relative = path.relative_to(ROOT).with_suffix("")
        parts = list(relative.parts)

        # __init__.py represents the package itself.
        if parts[-1] == "__init__":
            parts.pop()

        if not parts:
            continue

        modules.append(".".join(parts))

    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"[PASS] {module_name}")
        except Exception as exc:
            print(f"[FAIL] {module_name}")
            print(f"       {type(exc).__name__}: {exc}")
            return 1

    print(f"\n[PASS] Imported {len(modules)} backend modules.")
    return 0


def run_unit_tests() -> int:
    if not TESTS.exists():
        return fail(f"Unit-test directory not found: {TESTS}")

    return run_command(
        [sys.executable, "-m", "pytest", str(TESTS), "-vv", "--maxfail=1"],
        "3/4  Unit test suite"
    )


def run_coverage() -> int:
    # Coverage is informational. It runs only after all tests pass.
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            str(TESTS),
            "--cov=backend",
            "--cov-report=term-missing",
            "-q",
        ],
        "4/4  Backend coverage report"
    )


def main() -> int:
    started = time.perf_counter()

    print("=" * 72)
    print("DATAFORGE BACKEND VERIFICATION")
    print("=" * 72)
    print(f"Project : {ROOT}")
    print(f"Backend : {BACKEND}")
    print(f"Tests   : {TESTS}")

    if not BACKEND.exists():
        return fail("backend/ directory was not found.")

    if not (BACKEND / "__init__.py").exists():
        return fail("backend/__init__.py was not found.")

    files = discover_backend_files()

    if not files:
        return fail("No Python files were found inside backend/.")

    print(f"\nDiscovered {len(files)} backend Python files.")

    # Stage 1
    result = compile_backend(files)
    if result != 0:
        return result

    # Stage 2
    result = import_backend(files)
    if result != 0:
        return result

    # Stage 3
    result = run_unit_tests()
    if result != 0:
        return result

    # Stage 4
    result = run_coverage()
    if result != 0:
        return result

    elapsed = time.perf_counter() - started

    print("\n" + "=" * 72)
    print(f"[PASS] ALL BACKEND CHECKS PASSED in {elapsed:.2f}s")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())