"""Copy the prepared competition entry to make.fun's output directory."""

import os
from pathlib import Path
import shutil


def main() -> None:
    source = Path(__file__).resolve().parent / "assets" / "entry.png"
    output_directory = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_directory.mkdir(parents=True, exist_ok=True)
    destination = output_directory / "entry.png"
    source_size = source.stat().st_size
    shutil.copyfile(source, destination)
    copied_size = destination.stat().st_size
    if copied_size != source_size:
        raise OSError(f"Copy size mismatch: expected {source_size} bytes, got {copied_size}")
    print(f"Copied entry.png: {copied_size} bytes to {destination}")


if __name__ == "__main__":
    main()
