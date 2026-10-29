"""Cria uma entrega autocontida de fontes e recursos, sem ambiente virtual."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def package():
    output = ROOT / "dist" / "base-aurora-entrega.zip"
    output.parent.mkdir(exist_ok=True)
    roots = [
        ".gitignore",
        "main.py",
        "README.md",
        "requirements.txt",
        "requirements-tested.txt",
        "pyproject.toml",
        "framework",
        "app",
        "shaders",
        "assets",
        "tools",
        "tests",
        "docs",
    ]
    count = 0
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for name in roots:
            path = ROOT / name
            paths = sorted(path.rglob("*")) if path.is_dir() else [path]
            for file in paths:
                if not file.is_file() or "__pycache__" in file.parts or file.suffix == ".pyc":
                    continue
                archive.write(file, Path("base-aurora") / file.relative_to(ROOT))
                count += 1
    print(f"{output} ({count} arquivos, {output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    package()
