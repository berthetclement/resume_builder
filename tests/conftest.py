import pytest

from resume_builder.models.resume_model import Resume
from resume_builder.template.default_resume import DEFAULT_RESUME


@pytest.fixture
def default_resume() -> Resume:
    return DEFAULT_RESUME.model_copy(deep=True)
