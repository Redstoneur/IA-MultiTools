"""Checks for the build command shared by both platform launchers."""

import subprocess
import sys
from unittest.mock import Mock

import pytest

import build


def test_build_uses_current_python_and_package_entrypoint(monkeypatch):
    runner = Mock(return_value=subprocess.CompletedProcess([], 0))
    monkeypatch.setattr(build.subprocess, "run", runner)

    assert build.build_executable()

    command = runner.call_args.args[0]
    assert command[:3] == [sys.executable, "-m", "PyInstaller"]
    assert command[command.index("--paths") + 1] == "src"
    assert "run.py" in command
    assert "src/ia_multitools/main.py" not in command
    assert runner.call_args.kwargs["check"] is True


def test_build_failure_is_reported(monkeypatch):
    monkeypatch.setattr(
        build.subprocess,
        "run",
        Mock(side_effect=subprocess.CalledProcessError(1, "PyInstaller")),
    )

    assert build.build_executable() is False


def test_wrong_working_directory_fails(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["build.py"])

    with pytest.raises(SystemExit) as error:
        build.main()

    assert error.value.code == 1
