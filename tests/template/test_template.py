from pathlib import Path

from resume_builder.template.markdow_editor import write_model_to_markdown


def test_template_rendering(tmp_path: Path) -> None:
    from resume_builder.models.resume_model import Resume, contact, experience

    contact_info = contact(email="test@example.com", phone="123-456-7890")
    work_experiences = [
        experience(company="Test Company", position="Test Position", start_date="2020-01-01", end_date="2021-01-01"),
        experience(
            company="Another Company", position="Another Position", start_date="2021-02-01", end_date="2022-02-01"
        ),
    ]
    resume = Resume(name="John Doe", title="Software Engineer", contact=contact_info, experiences=work_experiences)

    write_model_to_markdown(resume, tmp_path / "test_resume.md")

    assert (tmp_path / "test_resume.md").exists()
