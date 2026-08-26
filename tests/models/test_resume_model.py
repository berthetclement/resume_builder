from resume_builder.models.resume_model import Resume
from resume_builder.template.constants import EXPERIENCES


def test_resume_model(default_resume: Resume) -> None:
    # when
    resume = default_resume

    # then
    assert isinstance(resume, Resume)
    assert resume.main.user_name == "John Doe"
    assert resume.main.title_position == "Project Manager"
    assert resume.main.description == "Experienced software engineer with a passion for developing innovative programs."
    assert resume.contact.email == "john.doe@example.com"
    assert resume.contact.phone == "123-456-7890"

    assert len(resume.experiences) == 3
    i = 0
    for entry in default_resume.experiences:
        assert entry.model_dump() == EXPERIENCES[i]
        i = i + 1
