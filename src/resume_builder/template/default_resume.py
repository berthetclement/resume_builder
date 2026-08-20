from resume_builder.models.resume_model import Resume, contact, experience, main
from resume_builder.template.constants import DESCRIPTION, EMAIL, EXPERIENCES, NAME, PHONE, TITLE

DEFAULT_RESUME = Resume(
    main=main(name=NAME, title=TITLE, description=DESCRIPTION),
    contact=contact(email=EMAIL, phone=PHONE),
    experiences=[experience(**row) for row in EXPERIENCES],
)
