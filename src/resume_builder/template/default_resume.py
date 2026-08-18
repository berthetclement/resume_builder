from resume_builder.models.resume_model import Resume, contact, experience
from resume_builder.template.constants import EMAIL, EXPERIENCES, NAME, PHONE, TITLE

DEFAULT_RESUME = Resume(
    name=NAME,
    title=TITLE,
    contact=contact(email=EMAIL, phone=PHONE),
    experiences=[experience(**row) for row in EXPERIENCES],
)
