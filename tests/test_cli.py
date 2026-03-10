from unittest.mock import patch

import pytest

from search_openclaw.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        with patch("sys.argv", ["search-openclaw", "version"]):
            main()
    assert exc.value.code == 0
    assert "Search OpenClaw v" in capsys.readouterr().out


def test_no_command_shows_help():
    with pytest.raises(SystemExit) as exc:
        with patch("sys.argv", ["search-openclaw"]):
            main()
    assert exc.value.code == 0


def test_doctor_runs(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    with patch("sys.argv", ["search-openclaw", "doctor"]):
        main()
    captured = capsys.readouterr()
    assert "Search OpenClaw" in captured.out
    assert "网页读取" in captured.out


def test_search_json_output(capsys):
    fake_results = []

    with patch("search_openclaw.cli.search", return_value=("brave", fake_results)):
        with patch("sys.argv", ["search-openclaw", "search", "test", "--json"]):
            main()

    captured = capsys.readouterr()
    assert '"provider": "brave"' in captured.out


def test_doctor_fix_runs(capsys):
    with patch("search_openclaw.cli._install_skill", return_value=None):
        with patch("sys.argv", ["search-openclaw", "doctor", "--fix"]):
            main()
    captured = capsys.readouterr()
    assert "Search OpenClaw" in captured.out
