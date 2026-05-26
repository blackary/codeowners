import json
from pathlib import Path
from unittest.mock import patch

import pytest

from codeowners.cli import find_codeowners, main

CODEOWNERS_CONTENT = """\
*.py @python-team
*.js @js-team
docs/ @docs-team user@example.com
"""


@pytest.fixture
def codeowners_file(tmp_path: Path) -> Path:
    f = tmp_path / "CODEOWNERS"
    f.write_text(CODEOWNERS_CONTENT)
    return f


def run_main(argv: list[str]) -> tuple[str, str, int]:
    exit_code = 0

    import io

    with (
        patch("sys.argv", ["codeowners-cli", *argv]),
        patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
        patch("sys.stderr", new_callable=io.StringIO) as mock_stderr,
    ):
        try:
            main()
        except SystemExit as e:
            exit_code = e.code if isinstance(e.code, int) else 1
        return mock_stdout.getvalue(), mock_stderr.getvalue(), exit_code


def test_default_text_output(codeowners_file: Path) -> None:
    out, _, code = run_main(
        ["--codeowners", str(codeowners_file), "src/foo.py", "src/bar.js"]
    )
    assert code == 0
    lines = out.strip().splitlines()
    assert lines[0] == "filename\towners"
    assert "src/foo.py\t@python-team" in lines
    assert "src/bar.js\t@js-team" in lines


def test_only_owners_filters_unowned(codeowners_file: Path) -> None:
    out, _, code = run_main(
        [
            "--codeowners",
            str(codeowners_file),
            "--only-owners",
            "src/foo.py",
            "something.txt",
        ]
    )
    assert code == 0
    lines = out.strip().splitlines()
    assert any("src/foo.py" in line for line in lines)
    assert not any("something.txt" in line for line in lines)


def test_csv_output(codeowners_file: Path) -> None:
    out, _, code = run_main(
        ["--codeowners", str(codeowners_file), "--output", "csv", "src/foo.py"]
    )
    assert code == 0
    lines = out.strip().splitlines()
    assert lines[0] == "filename,owners"
    assert "src/foo.py,@python-team" in lines


def test_tsv_output(codeowners_file: Path) -> None:
    out, _, code = run_main(
        ["--codeowners", str(codeowners_file), "--output", "tsv", "src/bar.js"]
    )
    assert code == 0
    lines = out.strip().splitlines()
    assert lines[0] == "filename\towners"
    assert "src/bar.js\t@js-team" in lines


def test_json_output(codeowners_file: Path) -> None:
    out, _, code = run_main(
        ["--codeowners", str(codeowners_file), "--output", "json", "src/foo.py"]
    )
    assert code == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["filename"] == "src/foo.py"
    assert data[0]["owners"] == ["@python-team"]


def test_json_multiple_owners(codeowners_file: Path) -> None:
    out, _, code = run_main(
        ["--codeowners", str(codeowners_file), "--output", "json", "docs/readme.md"]
    )
    assert code == 0
    data = json.loads(out)
    assert data[0]["owners"] == ["@docs-team", "user@example.com"]


def test_missing_codeowners_file_exits(tmp_path: Path) -> None:
    _, err, code = run_main(
        ["--codeowners", str(tmp_path / "DOES_NOT_EXIST"), "foo.py"]
    )
    assert code != 0
    assert "not found" in err


def test_no_codeowners_file_found(tmp_path: Path) -> None:
    with patch("codeowners.cli.find_codeowners", return_value=None):
        _, err, code = run_main(["foo.py"])
    assert code != 0
    assert "no CODEOWNERS file found" in err


def test_find_codeowners_walks_up(tmp_path: Path) -> None:
    codeowners = tmp_path / "CODEOWNERS"
    codeowners.write_text("*.py @team\n")
    sub = tmp_path / "src" / "deep"
    sub.mkdir(parents=True)
    found = find_codeowners(sub)
    assert found == codeowners


def test_find_codeowners_github_dir(tmp_path: Path) -> None:
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    codeowners = github_dir / "CODEOWNERS"
    codeowners.write_text("*.py @team\n")
    found = find_codeowners(tmp_path)
    assert found == codeowners


def test_find_codeowners_returns_none_when_missing(tmp_path: Path) -> None:
    assert find_codeowners(tmp_path) is None
