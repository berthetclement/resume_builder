from typing import Annotated

from pydantic import BaseModel, Field

from resume_builder.models.constants import CUSTOM_FIELD, HEADER1, HEADER2, HEADER3
from resume_builder.template.constants import CONTACT_SECTION_TITLE, WORK_EXPERIENCE_TITLE_NAME

# Hierarchy of Markdown headers
MarkdownH1 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: HEADER1}),
]

MarkdownH2 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: HEADER2}),
]

MarkdownH3 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: HEADER3}),
]

# TODO : Add MarkdownH3 to be inline convention explained in claude.md file


class Main(BaseModel):
    user_name: MarkdownH1
    title_position: MarkdownH3
    description: str


class Contact(BaseModel):
    email: str
    phone: str
    personnal_website: str | None = (
        None  # TODO may be define a list of social media links (LinkedIn, GitHub, etc.) in the future
    )


class Experience(BaseModel):
    position: MarkdownH3
    company: str
    location: str
    start_date: str
    end_date: str
    description: str | list[str] = Field(
        default_factory=list
    )  # Allow for a single string or a list of strings for the description


class Resume(BaseModel):
    main: Main
    contact: Contact = Field(title=CONTACT_SECTION_TITLE)
    experiences: list[Experience] = Field(title=WORK_EXPERIENCE_TITLE_NAME)
