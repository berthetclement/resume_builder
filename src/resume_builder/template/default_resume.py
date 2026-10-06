from resume_builder.models.resume_model import BriefEntry, Entry, Main, Resume, TitledEntry
from resume_builder.template.constants import (
    CONTACT_DESCRIPTION,
    DESCRIPTION_MAIN_VALUE,
    EDUCATION,
    EXPERIENCES,
    PERSONAL_PROJECTS,
    SKILLS_DESCRIPTION,
    TITLE_POSITION_VALUE,
    USER_NAME_VALUE,
)

DEFAULT_RESUME = Resume(
    main=Main(user_name=USER_NAME_VALUE, title_position=TITLE_POSITION_VALUE, description=DESCRIPTION_MAIN_VALUE),
    contact=BriefEntry(description=CONTACT_DESCRIPTION),
    skills=BriefEntry(description=SKILLS_DESCRIPTION),
    experiences=[Entry.model_validate(row) for row in EXPERIENCES],
    education=[Entry.model_validate(row) for row in EDUCATION],
    personal_projects=[Entry.model_validate(row) for row in PERSONAL_PROJECTS],
    languages=TitledEntry(title="French", description="Reading, Writing, Speaking"),
)
