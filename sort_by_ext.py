from __future__ import annotations
import argparse
import shutil
import sys
from tempfile import TemporaryDirectory
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively copy/move files and sort them by extensions."
    )
    parser.add_argument(
        "src",
        type=Path,
        help="Path to the source directory",
    )
    parser.add_argument(
        "dest",
        nargs="?",
        type=Path,
        default=Path("dist"),
        help="Path to the destination directory (default: ./dist)",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying",
    )
    return parser.parse_args()


def is_subpath(child: Path, parent: Path) -> bool:
    """Check if `child` is a subpath of `parent` (based on resolved paths)."""
    try:
        child_r = child.resolve()
        parent_r = parent.resolve()
        return parent_r in child_r.parents or child_r == parent_r
    except Exception:
        return False


def unique_target_path(target_dir: Path, name: str) -> Path:
    """
    Return a path that does not conflict with existing files.
    Example: file.txt → file.txt, file (1).txt, file (2).txt ...
    """
    base = Path(name).stem
    suffix = Path(name).suffix
    candidate = target_dir / f"{base}{suffix}"
    counter = 1
    while candidate.exists():
        candidate = target_dir / f"{base} ({counter}){suffix}"
        counter += 1
    return candidate


def process_directory(src_dir: Path, dest_root: Path, move: bool) -> tuple[int, int]:
    """
    Recursively process `src_dir` and copy/move files into `dest_root` sorted by extension.
    Returns (number_of_files, number_of_errors).
    """
    files_count = 0
    errors_count = 0

    try:
        entries = list(src_dir.iterdir())
    except Exception as e:
        print(f"[ERROR] Could not read directory: {src_dir} -> {e}", file=sys.stderr)
        return 0, 1

    for entry in entries:
        if entry.is_dir():
            if is_subpath(entry, dest_root):
                continue
            c_files, c_errs = process_directory(entry, dest_root, move)
            files_count += c_files
            errors_count += c_errs
        elif entry.is_file():
            ext = entry.suffix.lower().lstrip(".") if entry.suffix else "_no_ext"
            target_dir = dest_root / ext
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"[ERROR] Could not create directory: {target_dir} -> {e}", file=sys.stderr)
                errors_count += 1
                continue

            try:
                target_path = unique_target_path(target_dir, entry.name)
                if move:
                    shutil.move(str(entry), str(target_path))
                else:
                    shutil.copy2(str(entry), str(target_path))
                files_count += 1
                print(f"{'Moved' if move else 'Copied'}: {entry} -> {target_path}")
            except PermissionError as e:
                print(f"[ERROR] No permission for file: {entry} -> {e}", file=sys.stderr)
                errors_count += 1
            except FileNotFoundError as e:
                print(f"[ERROR] File missing or inaccessible: {entry} -> {e}", file=sys.stderr)
                errors_count += 1
            except OSError as e:
                print(f"[ERROR] File system error: {entry} -> {e}", file=sys.stderr)
                errors_count += 1
        else:
            continue

    return files_count, errors_count


def main(src: Path | None = None, dest: Path | None = None, move: bool | None = None) -> int:
    if src is None or dest is None or move is None:
        args = parse_args()
        src = args.src
        dest = args.dest
        move = args.move

    if not src.exists():
        print(f"[ERROR] Source directory does not exist: {src}", file=sys.stderr)
        return 2
    if not src.is_dir():
        print(f"[ERROR] Source path is not a directory: {src}", file=sys.stderr)
        return 2

    if is_subpath(src, dest):
        print(f"[ERROR] Source directory cannot be inside the destination directory.", file=sys.stderr)
        return 2

    try:
        dest.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Could not create destination directory: {dest} -> {e}", file=sys.stderr)
        return 2

    print(f"Starting {'move' if move else 'copy'} operation")
    print(f"Source: {src.resolve()}")
    print(f"Destination: {dest.resolve()}")

    total_files, total_errors = process_directory(src, dest, move)

    print("\n=== SUMMARY ===")
    print(f"Files processed: {total_files}")
    print(f"Errors:          {total_errors}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    with TemporaryDirectory() as src, TemporaryDirectory() as dest:
        src_path = Path(src)
        dest_path = Path(dest)

        (src_path / "a.txt").write_text("hello")
        (src_path / "b.jpg").write_text("world")
        (src_path / "nested").mkdir()
        (src_path / "nested" / "c.md").write_text("nested file")

        raise SystemExit(main(src=src_path, dest=dest_path, move=False))
