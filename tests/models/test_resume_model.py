from resume_builder.models.resume_model import Resume


def test_resume_model(default_resume: Resume) -> None:
    # when
    resume = default_resume

    # then
    assert isinstance(resume, Resume)
    assert resume.main.name == "John Doe"
    assert resume.main.title == "Project Manager"
    assert resume.main.description == "Experienced software engineer with a passion for developing innovative programs."
    assert resume.contact.email == "john.doe@example.com"
    assert resume.contact.phone == "123-456-7890"
    assert len(resume.experiences) == 3
    assert resume.experiences[0].company == "Acme Corp"
    assert resume.experiences[0].position == "Developer"
    assert resume.experiences[0].start_date == "2020-01-01"
    assert resume.experiences[0].end_date == "2021-01-01"
    assert resume.experiences[1].company == "Globex Corporation"
    assert resume.experiences[1].position == "Software Engineer"
    assert resume.experiences[1].start_date == "2021-02-01"
    assert resume.experiences[1].end_date == "2022-01-01"
    assert resume.experiences[2].company == "Initech"
    assert resume.experiences[2].position == "Project Manager"
    assert resume.experiences[2].start_date == "2022-02-01"
    assert resume.experiences[2].end_date == "2023-01-01"
