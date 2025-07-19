import json
import sys
import argparse
import base64
from pathlib import Path


def convert_cell(cell, img_dir):
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
            f'<button class="copy-btn" style="position:absolute; top:8px; right:8px;" onclick="navigator.clipboard.writeText(document.getElementById(\'code-cell-{id(content)}\').innerText); this.blur();">Copy</button>'
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
                        img_path = img_dir / f"output_image_{id(content)}.png"
                        save_image(img_path, img_data, markdown_output)

                    # Handle image output (JPEG)
                    if "image/jpeg" in data:
                        img_data = data["image/jpeg"]
                        if isinstance(img_data, list):
                            img_data = "".join(img_data)
                        img_path = img_dir / f"output_image_{id(content)}.png"
                        save_image(img_path, img_data, markdown_output)

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
