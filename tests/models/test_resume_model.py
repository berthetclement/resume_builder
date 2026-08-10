from resume_builder.models.resume_model import Resume, contact, experience


def test_resume_model() -> None:
    contact_info = contact(email="test@example.com", phone="123-456-7890")
    work_experiences = [
        experience(company="Test Company", position="Test Position", start_date="2020-01-01", end_date="2021-01-01"),
        experience(
            company="Another Company", position="Another Position", start_date="2021-02-01", end_date="2022-02-01"
        ),
    ]
    resume = Resume(name="John Doe", title="Software Engineer", contact=contact_info, experiences=work_experiences)
    assert resume.name == "John Doe"
    assert resume.title == "Software Engineer"
    assert resume.contact.email == "test@example.com"
    assert resume.contact.phone == "123-456-7890"
    assert len(resume.experiences) == 2
    assert resume.experiences[0].company == "Test Company"
    assert resume.experiences[0].position == "Test Position"
    assert resume.experiences[0].start_date == "2020-01-01"
    assert resume.experiences[0].end_date == "2021-01-01"
