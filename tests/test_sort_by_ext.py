import sys
from pathlib import Path
import subprocess

import pytest


def run_cli(module_path: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(module_path), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )

@pytest.fixture
def script_path(tmp_path_factory):
    return Path(__file__).resolve().parent.parent / "sort_by_ext.py"


def test_copy_basic(tmp_path, script_path):
    src = tmp_path / "src"
    dest = tmp_path / "dist"
    (src / "sub").mkdir(parents=True)
    (src / "a.txt").write_text("a")
    (src / "sub" / "b.TXT").write_text("b")
    (src / "README").write_text("noext")

    result = run_cli(script_path, src, dest)
    assert result.returncode == 0, result.stderr

    assert (dest / "txt" / "a.txt").exists()
    assert (dest / "txt" / "b.txt").exists()
    assert (dest / "_no_ext" / "README").exists()

def test_move_mode(tmp_path, script_path):
    src = tmp_path / "src"
    dest = tmp_path / "dist"
    src.mkdir()
    (src / "x.jpg").write_bytes(b"\xFF\xD8\xFF")

    result = run_cli(script_path, src, dest, "--move")
    assert result.returncode == 0, result.stderr

    assert not (src / "x.jpg").exists()
    assert (dest / "jpg" / "x.jpg").exists()

def test_name_collision(tmp_path, script_path):
    src = tmp_path / "src"
    dest = tmp_path / "dist"
    (src / "a").mkdir(parents=True)
    (src / "b").mkdir(parents=True)
    (src / "a" / "same.txt").write_text("one")
    (src / "b" / "same.txt").write_text("two")

    result = run_cli(script_path, src, dest)
    assert result.returncode == 0, result.stderr

    txt_dir = dest / "txt"
    files = sorted(p.name for p in txt_dir.iterdir())
    assert "same.txt" in files
    assert any(name.startswith("same (") and name.endswith(").txt") for name in files)

def test_dest_inside_src_is_skipped(tmp_path, script_path):
    src = tmp_path / "src"
    dest = src / "inner_dist"
    src.mkdir()
    (src / "file.txt").write_text("data")
    dest.mkdir()

    result = run_cli(script_path, src, dest)
    assert result.returncode == 0, result.stderr

    assert (dest / "txt" / "file.txt").exists()

def test_no_ext_folder(tmp_path, script_path):
    src = tmp_path / "src"
    dest = tmp_path / "dist"
    src.mkdir()
    (src / "LICENSE").write_text("text")

    result = run_cli(script_path, src, dest)
    assert result.returncode == 0, result.stderr
    assert (dest / "_no_ext" / "LICENSE").exists()
