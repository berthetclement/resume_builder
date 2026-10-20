import re
from pathlib import Path

import pytest

from resume_builder.render.renderer_pdf import render_pdf


def test_pdf_raise_html_not_found(tmp_path: Path) -> None:
    # given
    html_path = tmp_path / "nothing.html"

    # then
    with pytest.raises(FileNotFoundError, match=re.escape(f"{html_path} does not exist or is not a file")):
        render_pdf(html_path)
