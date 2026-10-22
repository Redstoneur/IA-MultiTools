"""Checks for the build command shared by both platform launchers."""

import subprocess
import sys
from types import ModuleType
from unittest.mock import Mock

import pytest

import build


@pytest.fixture(autouse=True)
def isolate_pyinstaller_import(monkeypatch):
    # PyInstaller probes the host with subprocess.run during import on Linux.
    monkeypatch.setitem(sys.modules, "PyInstaller", ModuleType("PyInstaller"))


@pytest.mark.parametrize("system,separator,icon", [
    ("Windows", ";", "logo.ico"),
    ("Linux", ":", "logo.png"),
])
def test_build_uses_current_python_and_package_entrypoint(
    monkeypatch, system, separator, icon
):
    monkeypatch.setattr(build.platform, "system", lambda: system)
    runner = Mock(return_value=subprocess.CompletedProcess([], 0))
    monkeypatch.setattr(build.subprocess, "run", runner)

    assert build.build_executable()

    command = runner.call_args.args[0]
    assert command[:3] == [sys.executable, "-m", "PyInstaller"]
    assert command[command.index("--paths") + 1] == "src"
    assert "run.py" in command
    assert "src/ia_multitools/main.py" not in command
    assert command[command.index("--add-data") + 1] == f"assets{separator}assets"
    assert command[command.index("--icon") + 1] == str(build.Path("assets") / icon)
    runner.assert_called_once()
    assert runner.call_args.kwargs["check"] is True


@pytest.mark.parametrize("system", ["Windows", "Linux"])
def test_build_failure_is_reported(monkeypatch, system):
    monkeypatch.setattr(build.platform, "system", lambda: system)
    monkeypatch.setattr(
        build.subprocess,
        "run",
        Mock(side_effect=subprocess.CalledProcessError(1, "PyInstaller")),
    )

    assert build.build_executable() is False


def test_missing_pyinstaller_is_reported(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "PyInstaller", None)
    runner = Mock()
    monkeypatch.setattr(build.subprocess, "run", runner)

    assert build.build_executable() is False
    runner.assert_not_called()
    assert "pip install pyinstaller" in capsys.readouterr().out


def test_wrong_working_directory_fails(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["build.py"])

    with pytest.raises(SystemExit) as error:
        build.main()

    assert error.value.code == 1
