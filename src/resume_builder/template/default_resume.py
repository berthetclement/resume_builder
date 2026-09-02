from resume_builder.models.resume_model import Contact, Experience, Main, Resume
from resume_builder.template.constants import (
    DESCRIPTION_MAIN_VALUE,
    EMAIL,
    EXPERIENCES,
    PERSONAL_WEBSITE,
    PHONE,
    TITLE_POSITION_VALUE,
    USER_NAME_VALUE,
)

DEFAULT_RESUME = Resume(
    main=Main(user_name=USER_NAME_VALUE, title_position=TITLE_POSITION_VALUE, description=DESCRIPTION_MAIN_VALUE),
    contact=Contact(email=EMAIL, phone=PHONE, personnal_website=PERSONAL_WEBSITE),
    experiences=[Experience.model_validate(row) for row in EXPERIENCES],
)
