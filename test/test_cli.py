"""Command-line behavior shared by the console command and module runner."""

import subprocess
import sys


def invoke(*arguments):
    return subprocess.run(
        [sys.executable, "-m", "unit_syntax", *map(str, arguments)],
        capture_output=True,
        text=True,
    )


def test_script_receives_arguments_and_can_import_units(tmp_path):
    (tmp_path / "helper.py").write_text("distance = 15 meters\n")
    script = tmp_path / "model.py"
    script.write_text(
        "import sys\n"
        "from helper import distance\n"
        "assert __name__ == '__main__'\n"
        "assert __file__ == sys.argv[0]\n"
        "assert sys.argv[1:] == ['value', '--check', '--project', 'root', '--help']\n"
        "print(distance.to('meter').magnitude)\n"
    )
    result = invoke(script, "value", "--check", "--project", "root", "--help")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "15\n"


def test_check_does_not_execute_script(tmp_path):
    sentinel = tmp_path / "executed"
    script = tmp_path / "model.py"
    script.write_text(
        f"open({str(sentinel)!r}, 'w').write('executed')\nvalue = 5 mm\n"
    )
    result = invoke("--check", script)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not sentinel.exists()


def test_check_accepts_multiple_paths_and_project_option(tmp_path):
    first = tmp_path / "first.py"
    first.write_text("length = 5 mm\n")
    second = tmp_path / "second.py"
    second.write_text("duration = 2 seconds\n")
    result = invoke("--check", first, "--project", tmp_path, second)
    assert result.returncode == 0, result.stdout + result.stderr


def test_script_exit_code_is_preserved(tmp_path):
    script = tmp_path / "model.py"
    script.write_text("distance = 5 mm\nraise SystemExit(7)\n")
    assert invoke(script).returncode == 7


def test_project_option_requires_check_mode(tmp_path):
    script = tmp_path / "model.py"
    script.write_text("raise AssertionError('must not execute')\n")
    result = invoke("--project", tmp_path, script)
    assert result.returncode == 2
    assert "--project requires --check" in result.stderr


def test_help_describes_check_flag():
    result = invoke("--help")
    assert result.returncode == 0
    assert "--check" in result.stdout
    assert "without executing" in result.stdout
