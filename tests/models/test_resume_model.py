from resume_builder.models.resume_model import Resume, contact


def test_resume_model():
    contact_info = contact(email="test@example.com", phone="123-456-7890")
    resume = Resume(name="John Doe", title="Software Engineer", contact=contact_info)
    assert resume.name == "John Doe"
    assert resume.title == "Software Engineer"
    assert resume.contact.email == "test@example.com"
    assert resume.contact.phone == "123-456-7890"
