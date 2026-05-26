import argparse
import csv
import json
import sys
from pathlib import Path

from codeowners import CodeOwners

CODEOWNERS_LOCATIONS = ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]


def find_codeowners(start: Path) -> Path | None:
    for directory in [start, *start.parents]:
        for rel in CODEOWNERS_LOCATIONS:
            candidate = directory / rel
            if candidate.is_file():
                return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="codeowners-cli",
        description="Show owners for files according to a CODEOWNERS file.",
    )
    parser.add_argument("filenames", nargs="+", metavar="FILE")
    parser.add_argument("--codeowners", metavar="PATH", help="Path to CODEOWNERS file")
    parser.add_argument(
        "--only-owners",
        action="store_true",
        help="Only output files that have at least one owner",
    )
    parser.add_argument(
        "--output",
        choices=["text", "csv", "tsv", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Omit the header row",
    )
    args = parser.parse_args()

    if args.codeowners:
        codeowners_path = Path(args.codeowners)
        if not codeowners_path.is_file():
            print(
                f"error: CODEOWNERS file not found: {args.codeowners}", file=sys.stderr
            )
            sys.exit(1)
    else:
        codeowners_path = find_codeowners(Path.cwd())
        if codeowners_path is None:
            print("error: no CODEOWNERS file found", file=sys.stderr)
            sys.exit(1)

    owners = CodeOwners(codeowners_path.read_text())

    rows: list[tuple[str, list[str]]] = []
    for filename in args.filenames:
        owner_tuples = owners.of(filename)
        owner_names = [o[1] for o in owner_tuples]
        if args.only_owners and not owner_names:
            continue
        rows.append((filename, owner_names))

    if args.output == "json":
        print(
            json.dumps(
                [{"filename": f, "owners": o} for f, o in rows],
                indent=2,
            )
        )
    elif args.output in ("csv", "tsv"):
        delimiter = "," if args.output == "csv" else "\t"
        writer = csv.writer(sys.stdout, delimiter=delimiter)
        if not args.no_header:
            writer.writerow(["filename", "owners"])
        for filename, owner_names in rows:
            writer.writerow([filename, " ".join(owner_names)])
    else:
        if not args.no_header:
            print("filename\towners")
        for filename, owner_names in rows:
            print(f"{filename}\t{' '.join(owner_names)}")
