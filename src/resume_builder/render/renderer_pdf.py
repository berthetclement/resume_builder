from pathlib import Path


def render_pdf(html_path: Path) -> Path:
    # checks
    if not html_path.is_file():
        raise FileNotFoundError(f"{html_path} does not exist or is not a file")

    return html_path
