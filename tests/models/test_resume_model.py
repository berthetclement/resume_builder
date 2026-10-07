from resume_builder.models.resume_model import Resume
from resume_builder.template.constants import EMAIL, EXPERIENCES, PERSONAL_WEBSITE, PHONE


def test_resume_model(default_resume: Resume) -> None:
    # when
    resume = default_resume

    # then
    assert isinstance(resume, Resume)
    assert resume.main.user_name == "John Doe"
    assert resume.main.title_position == "Project Manager"
    assert resume.main.description == "Experienced software engineer with a passion for developing innovative programs."

    description = resume.contact.description
    assert isinstance(description, str)
    blocks = description.split("\n\n")

    assert len(blocks) == 3
    assert blocks[0] == f"&#9993; {EMAIL}"
    assert blocks[1] == f"&#9742; {PHONE}"
    assert blocks[2].startswith("<svg") and blocks[2].endswith(f" {PERSONAL_WEBSITE}")

    assert len(resume.experiences) == 3
    i = 0
    for entry in default_resume.experiences:
        assert entry.model_dump() == EXPERIENCES[i]
        i = i + 1
