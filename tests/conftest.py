from pathlib import Path

import pytest

from resume_builder.models.resume_model import Resume
from resume_builder.template.default_resume import DEFAULT_RESUME
from resume_builder.template.markdown_editor import write_model_to_markdown


# Instance of Pydantic base model
@pytest.fixture
def default_resume() -> Resume:
    return DEFAULT_RESUME.model_copy(deep=True)


# Markdown file parse to str
@pytest.fixture
def default_markdown_resume_content(tmp_path: Path, default_resume: Resume) -> str:
    name_file = "test_resume.md"
    write_model_to_markdown(default_resume, tmp_path / name_file)
    return (tmp_path / name_file).read_text(encoding="utf-8")
