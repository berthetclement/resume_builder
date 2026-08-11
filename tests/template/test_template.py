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

    # check markdown content is in line with the model data
    with open(tmp_path / "test_resume.md") as f:
        content = f.read()
        assert "# Resume" in content
        assert "## name" in content
        assert "John Doe" in content
        assert "## title" in content
        assert "Software Engineer" in content
        assert "## contact" in content
        assert "- **email**: test@example.com" in content
        assert "- **phone**: 123-456-7890" in content
        assert "## experiences" in content
        assert "### Test Company" in content
        assert "### Another Company" in content
        assert "- **position**: Test Position" in content
        assert "- **position**: Another Position" in content
        assert "- **start_date**: 2020-01-01" in content
        assert "- **end_date**: 2021-01-01" in content
        assert "- **start_date**: 2021-02-01" in content
        assert "- **end_date**: 2022-02-01" in content
