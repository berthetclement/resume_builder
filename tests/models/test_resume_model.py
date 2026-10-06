from resume_builder.models.resume_model import Resume
from resume_builder.template.constants import EXPERIENCES, GITHUB_ICON


def test_resume_model(default_resume: Resume) -> None:
    # when
    resume = default_resume

    # then
    assert isinstance(resume, Resume)
    assert resume.main.user_name == "John Doe"
    assert resume.main.title_position == "Project Manager"
    assert resume.main.description == "Experienced software engineer with a passion for developing innovative programs."
    assert (
        resume.contact.description
        == f"&#9993; john.doe@example.com\n\n&#9742; 123-456-7890\n\n{GITHUB_ICON} https://johndoe.com"
    )

    assert len(resume.experiences) == 3
    i = 0
    for entry in default_resume.experiences:
        assert entry.model_dump() == EXPERIENCES[i]
        i = i + 1
