from typing import Annotated

from pydantic import BaseModel, Field

from resume_builder.conventions import CUSTOM_FIELD
from resume_builder.models.constants import (
    CONTACT_SECTION_TITLE,
    EDUCATION_SECTION_TITLE,
    EXPERIENCES_SECTION_TITLE,
    LANGUAGES_SECTION_TITLE,
    PERSONAL_PROJECTS_SECTION_TITLE,
    SKILLS_SECTION_TITLE,
)

# Hierarchy of Markdown headers
MarkdownH1 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: 1}),
]

MarkdownH3 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: 3}),
]


# Every model class below keeps all its fields required. Making one optional
# (`str | None = None`) would also mean teaching `_write_model_to_markdown` to
# skip it: it writes `str(value)` with no None branch, so an unset field puts
# the literal string "None" in the generated resume.


class Main(BaseModel):
    user_name: MarkdownH1
    title_position: MarkdownH3
    description: str


class BriefEntry(BaseModel):
    description: str | list[str] = Field(default_factory=list)


class TitledEntry(BaseModel):
    title: MarkdownH3
    description: str | list[str] = Field(default_factory=list)


class Entry(BaseModel):
    title: MarkdownH3
    subtitle: str
    location: str
    start_date: str
    end_date: str
    description: str | list[str] = Field(default_factory=list)


# Use the `Field` function to provide titles for the sections in the resume model
class Resume(BaseModel):
    main: Main
    contact: BriefEntry = Field(title=CONTACT_SECTION_TITLE)
    skills: BriefEntry = Field(title=SKILLS_SECTION_TITLE)
    experiences: list[Entry] = Field(title=EXPERIENCES_SECTION_TITLE)
    education: list[Entry] = Field(title=EDUCATION_SECTION_TITLE)
    personal_projects: list[Entry] = Field(title=PERSONAL_PROJECTS_SECTION_TITLE)
    languages: TitledEntry = Field(title=LANGUAGES_SECTION_TITLE)
