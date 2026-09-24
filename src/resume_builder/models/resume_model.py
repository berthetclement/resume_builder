from typing import Annotated

from pydantic import BaseModel, Field

from resume_builder.conventions import CUSTOM_FIELD
from resume_builder.models.constants import CONTACT_SECTION_TITLE, EXPERIENCES_SECTION_TITLE

# Hierarchy of Markdown headers
MarkdownH1 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: 1}),
]

MarkdownH3 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: 3}),
]


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
    experiences: list[Experience] = Field(title=EXPERIENCES_SECTION_TITLE)
