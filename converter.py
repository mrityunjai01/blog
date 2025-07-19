#!/usr/bin/env python3
"""
Convert Jupyter Notebook (.ipynb) to Markdown (.md) format.
"""

import json
import sys
import argparse
import base64
from pathlib import Path


def convert_cell_to_markdown(cell):
    """Convert a single notebook cell to markdown format."""
    cell_type = cell.get("cell_type", "")
    source = cell.get("source", [])

    # Join source lines if it's a list
    if isinstance(source, list):
        content = "".join(source)
    else:
        content = source

    markdown_output = []

    if cell_type == "markdown":
        # Markdown cells: output as-is
        markdown_output.append(content)

    elif cell_type == "code":
        # Code cells: wrap in code blocks
        markdown_output.append(
            f'<div class="code-cell" style="position:relative;">'
            f'<button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById(\'code-cell-{id(content)}\').innerText)">Copy</button>'
            f'<pre id="code-cell-{id(content)}"><code class="language-python">{content}</code></pre>'
            f"</div>"
        )
        # Handle outputs if present
        outputs = cell.get("outputs", [])
        if outputs:
            markdown_output.append("\n**Output:**")
            for output in outputs:
                output_type = output.get("output_type", "")

                if output_type == "stream":
                    # Text output (print statements, etc.)
                    text = "".join(output.get("text", []))
                    markdown_output.append(f"\n```\n{text}\n```")

                elif output_type == "execute_result" or output_type == "display_data":
                    # Result output
                    data = output.get("data", {})

                    # Handle text/plain output
                    if "text/plain" in data:
                        text = "".join(data["text/plain"])
                        markdown_output.append(f"\n```\n{text}\n```")

                    # Handle HTML output
                    if "text/html" in data:
                        html = (
                            "".join(data["text/html"])
                            if isinstance(data["text/html"], list)
                            else data["text/html"]
                        )
                        # Add HTML directly to markdown
                        markdown_output.append(f"\n{html}")

                    # Handle LaTeX/math output
                    if "text/latex" in data:
                        latex = (
                            "".join(data["text/latex"])
                            if isinstance(data["text/latex"], list)
                            else data["text/latex"]
                        )
                        # Wrap LaTeX in math blocks
                        markdown_output.append(f"\n$\n{latex}\n$")

                    # Handle image output (PNG)
                    if "image/png" in data:
                        img_data = data["image/png"]
                        if isinstance(img_data, list):
                            img_data = "".join(img_data)
                        markdown_output.append(
                            f'\n<img src="data:image/png;base64,{img_data}" alt="Output image" style="max-width: 100%;" />'
                        )

                    # Handle image output (JPEG)
                    if "image/jpeg" in data:
                        img_data = data["image/jpeg"]
                        if isinstance(img_data, list):
                            img_data = "".join(img_data)
                        markdown_output.append(
                            f'\n<img src="data:image/jpeg;base64,{img_data}" alt="Output image" style="max-width: 100%;" />'
                        )

                    # Handle SVG output
                    if "image/svg+xml" in data:
                        svg_data = data["image/svg+xml"]
                        if isinstance(svg_data, list):
                            svg_data = "".join(svg_data)
                        markdown_output.append(f"\n{svg_data}")

                elif output_type == "error":
                    # Error output
                    error_name = output.get("ename", "Error")
                    error_value = output.get("evalue", "")
                    traceback = output.get("traceback", [])

                    markdown_output.append(f"\n**Error: {error_name}**")
                    markdown_output.append(f"```\n{error_value}")
                    if traceback:
                        markdown_output.append("\n".join(traceback))
                    markdown_output.append("```")

    elif cell_type == "raw":
        # Raw cells: output in code block
        markdown_output.append(f"```\n{content}\n```")

    return "\n".join(markdown_output)


def convert_notebook_to_markdown_with_images(
    notebook_path, output_path=None, image_dir=None
):
    """Convert a Jupyter notebook to markdown format, saving images as separate files."""
    notebook_path = Path(notebook_path)

    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook file not found: {notebook_path}")

    # Determine output path
    if output_path is None:
        output_path = notebook_path.with_suffix(".md")
    else:
        output_path = Path(output_path)

    if image_dir is None:
        image_dir = output_path.parent / "images"

    # Load the notebook
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in notebook file: {e}")

    # Extract notebook metadata for title
    metadata = notebook.get("metadata", {})
    title = metadata.get("title", notebook_path.stem)

    # Convert cells to markdown
    markdown_content = [f"# {title}\n"]
    image_counter = 0

    cells = notebook.get("cells", [])
    for i, cell in enumerate(cells):
        cell_markdown, img_count = convert_cell_to_markdown_with_images(
            cell, output_path.stem, image_counter, image_dir
        )
        image_counter += img_count

        if cell_markdown.strip():  # Only add non-empty cells
            markdown_content.append(cell_markdown)
            # Add spacing between cells (except for the last cell)
            if i < len(cells) - 1:
                markdown_content.append("\n---\n")

    # Write to output file
    final_content = "\n".join(markdown_content)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"Successfully converted '{notebook_path}' to '{output_path}'")
        if image_counter > 0:
            print(f"Saved {image_counter} images to '{image_dir}'")
    except Exception as e:
        raise IOError(f"Failed to write output file: {e}")

    return output_path


def convert_cell_to_markdown_with_images(cell, notebook_name, image_counter, image_dir):
    """Convert a single notebook cell to markdown format, saving images as files."""
    cell_type = cell.get("cell_type", "")
    source = cell.get("source", [])

    # Join source lines if it's a list
    if isinstance(source, list):
        content = "".join(source)
    else:
        content = source

    markdown_output = []
    images_saved = 0

    if cell_type == "markdown":
        # Markdown cells: output as-is
        markdown_output.append(content)

    elif cell_type == "code":
        # Code cells: wrap in code blocks
        markdown_output.append(f"```python\n{content}\n```")

        # Handle outputs if present
        outputs = cell.get("outputs", [])
        if outputs:
            markdown_output.append("\n**Output:**")
            for output in outputs:
                output_type = output.get("output_type", "")

                if output_type == "stream":
                    # Text output (print statements, etc.)
                    text = "".join(output.get("text", []))
                    markdown_output.append(f"\n```\n{text}\n```")

                elif output_type == "execute_result" or output_type == "display_data":
                    # Result output
                    data = output.get("data", {})

                    # Handle text/plain output
                    if "text/plain" in data:
                        text = "".join(data["text/plain"])
                        markdown_output.append(f"\n```\n{text}\n```")

                    # Handle HTML output
                    if "text/html" in data:
                        html = (
                            "".join(data["text/html"])
                            if isinstance(data["text/html"], list)
                            else data["text/html"]
                        )
                        markdown_output.append(f"\n{html}")

                    # Handle LaTeX/math output
                    if "text/latex" in data:
                        latex = (
                            "".join(data["text/latex"])
                            if isinstance(data["text/latex"], list)
                            else data["text/latex"]
                        )
                        markdown_output.append(f"\n$\n{latex}\n$")

                    # Handle image output (PNG) - save as file
                    if "image/png" in data:
                        img_data = data["image/png"]
                        if isinstance(img_data, list):
                            img_data = "".join(img_data)

                        # Save image to file
                        img_filename = (
                            f"{notebook_name}_image_{image_counter + images_saved}.png"
                        )
                        img_path = image_dir / img_filename

                        try:
                            with open(img_path, "wb") as f:
                                f.write(base64.b64decode(img_data))
                            markdown_output.append(
                                f'\n<img src="{image_dir.name}/{img_filename}" alt="Output image" style="max-width: 100%;" />'
                            )
                            images_saved += 1
                        except Exception as e:
                            print(f"Warning: Could not save image {img_filename}: {e}")
                            markdown_output.append(
                                f'\n<img src="data:image/png;base64,{img_data}" alt="Output image" style="max-width: 100%;" />'
                            )

                    # Handle image output (JPEG) - save as file
                    if "image/jpeg" in data:
                        img_data = data["image/jpeg"]
                        if isinstance(img_data, list):
                            img_data = "".join(img_data)

                        # Save image to file
                        img_filename = (
                            f"{notebook_name}_image_{image_counter + images_saved}.jpg"
                        )
                        img_path = image_dir / img_filename

                        try:
                            with open(img_path, "wb") as f:
                                f.write(base64.b64decode(img_data))
                            markdown_output.append(
                                f'\n<img src="{image_dir.name}/{img_filename}" alt="Output image" style="max-width: 100%;" />'
                            )
                            images_saved += 1
                        except Exception as e:
                            print(f"Warning: Could not save image {img_filename}: {e}")
                            markdown_output.append(
                                f'\n<img src="data:image/jpeg;base64,{img_data}" alt="Output image" style="max-width: 100%;" />'
                            )

                    # Handle SVG output
                    if "image/svg+xml" in data:
                        svg_data = data["image/svg+xml"]
                        if isinstance(svg_data, list):
                            svg_data = "".join(svg_data)
                        markdown_output.append(f"\n{svg_data}")

                elif output_type == "error":
                    # Error output
                    error_name = output.get("ename", "Error")
                    error_value = output.get("evalue", "")
                    traceback = output.get("traceback", [])

                    markdown_output.append(f"\n**Error: {error_name}**")
                    markdown_output.append(f"```\n{error_value}")
                    if traceback:
                        markdown_output.append("\n".join(traceback))
                    markdown_output.append("```")

    elif cell_type == "raw":
        # Raw cells: output in code block
        markdown_output.append(f"```\n{content}\n```")

    return "\n".join(markdown_output), images_saved

    """Convert a Jupyter notebook to markdown format."""
    notebook_path = Path(notebook_path)

    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook file not found: {notebook_path}")

    # Determine output path
    if output_path is None:
        output_path = notebook_path.with_suffix(".md")
    else:
        output_path = Path(output_path)

    # Load the notebook
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in notebook file: {e}")

    # Extract notebook metadata for title
    metadata = notebook.get("metadata", {})
    title = metadata.get("title", notebook_path.stem)

    # Convert cells to markdown
    markdown_content = [f"# {title}\n"]

    cells = notebook.get("cells", [])
    for i, cell in enumerate(cells):
        cell_markdown = convert_cell_to_markdown(cell)
        if cell_markdown.strip():  # Only add non-empty cells
            markdown_content.append(cell_markdown)
            # Add spacing between cells (except for the last cell)
            if i < len(cells) - 1:
                markdown_content.append("\n---\n")

    # Write to output file
    final_content = "\n".join(markdown_content)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"Successfully converted '{notebook_path}' to '{output_path}'")
    except Exception as e:
        raise IOError(f"Failed to write output file: {e}")

    return output_path


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
        "--save-images",
        action="store_true",
        help="Save images as separate files instead of embedding as base64",
    )

    parser.add_argument(
        "--image-dir",
        default="images",
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

            # Create image directory if saving images separately
            if args.save_images:
                image_dir = Path(args.image_dir)
                image_dir.mkdir(exist_ok=True)
                convert_notebook_to_markdown_with_images(
                    notebook_path, output_path, image_dir
                )
            else:
                convert_notebook_to_markdown(notebook_path, output_path)

        except Exception as e:
            print(f"Error converting '{notebook_path}': {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
