#!/usr/bin/env python3
"""
Convert Jupyter Notebook (.ipynb) to Markdown (.md) format.
"""

import json
import sys
import argparse
import base64
from pathlib import Path
from convert_notebook import convert_notebook


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Convert Jupyter Notebook (.ipynb) to Markdown (.md)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python notebook_to_md.py notebook.ipynb
  python notebook_to_md.py notebook.ipynb -o output.md
  python notebook_to_md.py *.ipynb
        """,
    )

    parser.add_argument(
        "notebooks", nargs="+", help="Path(s) to notebook file(s) to convert"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output markdown file path (only works with single input file)",
    )

    parser.add_argument(
        "--image-dir",
        default=None,
        help="Directory to save images when using --save-images (default: images)",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing markdown files without asking",
    )

    args = parser.parse_args()

    # Validate arguments
    if len(args.notebooks) > 1 and args.output:
        print("Error: Cannot specify output file when converting multiple notebooks")
        sys.exit(1)

    # Convert each notebook
    for notebook_path in args.notebooks:
        try:
            output_path = args.output if len(args.notebooks) == 1 else None

            # Check if output file exists
            if output_path is None:
                potential_output = Path(notebook_path).with_suffix(".md")
            else:
                potential_output = Path(output_path)

            if potential_output.exists() and not args.overwrite:
                response = input(
                    f"File '{potential_output}' already exists. Overwrite? (y/n): "
                )
                if response.lower() not in ["y", "yes"]:
                    print(f"Skipping {notebook_path}")
                    continue

            convert_notebook(notebook_path, output_path)

        except Exception as e:
            import traceback

            print(f"Error converting '{notebook_path}': {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
