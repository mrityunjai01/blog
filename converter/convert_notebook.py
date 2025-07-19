import json
import sys
import argparse
import base64
from pathlib import Path
from convert_cell import convert_cell


def convert_notebook(notebook_path, output_path=None, image_dir=None):
    """Convert a Jupyter notebook to markdown format, saving images as separate files."""
    notebook_path = Path(notebook_path)

    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook file not found: {notebook_path}")

    # Determine output path
    if output_path is None:
        output_path = notebook_path.with_suffix(".md")
    else:
        output_path = Path(output_path)
    print(f"Output path: {output_path}")

    if image_dir is None:
        image_dir = output_path.parent / "images"
    print(f"Image directory pare: {output_path.parent}")
    print(f"Image directory: {image_dir}")
    image_dir.mkdir(parents=True, exist_ok=True)

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
        cell_markdown = convert_cell(cell, image_dir)

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


def save_image(img_path, img_data, markdown_output):
    try:
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(img_data))
        print(f"saved image to {img_path}")
        markdown_output.append(
            f'\n<img src="{img_path.parent.name}/{img_path.name}" alt="Output image" style="max-width: 100%;" />'
        )
    except Exception as e:
        print(f"Warning: Could not save image {img_path}: {e}")
        markdown_output.append(
            f'\n<img src="data:image/png;base64,{img_data}" alt="Output image" style="max-width: 100%;" />'
        )
