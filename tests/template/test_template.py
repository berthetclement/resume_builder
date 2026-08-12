from pathlib import Path

from resume_builder.models.resume_model import Resume
from resume_builder.template.markdow_editor import write_model_to_markdown


def test_write_model_to_markdown(tmp_path: Path, default_resume: Resume) -> None:

    write_model_to_markdown(default_resume, tmp_path / "test_resume.md")

    assert (tmp_path / "test_resume.md").exists()

    # check markdown content is in line with the model data
    with open(tmp_path / "test_resume.md") as f:
        content = f.read()
        # main sections
        assert "# Resume" in content
        assert "## name" in content
        assert "## title" in content
        assert "## contact" in content
        assert "## experiences" in content

        # check contact details
        assert "John Doe" in content
        assert "- **email**: john.doe@example.com" in content
        assert "- **phone**: 123-456-7890" in content

        # check experiences details
        assert "### Acme Corp" in content
        assert "- **position**: Developer" in content
        assert "- **start_date**: 2020-01-01" in content
        assert "- **end_date**: 2021-01-01" in content

        assert "### Globex Corporation" in content
        assert "Software Engineer" in content
        assert "- **start_date**: 2021-02-01" in content
        assert "- **end_date**: 2022-01-01" in content

        assert "### Initech" in content
        assert "Project Manager" in content
        assert "- **start_date**: 2022-02-01" in content
        assert "- **end_date**: 2023-01-01" in content
