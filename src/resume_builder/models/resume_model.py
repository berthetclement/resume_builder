from typing import Annotated

from pydantic import BaseModel, Field

from resume_builder.models.constants import CUSTOM_FIELD, HEADER1, HEADER2

# Hierarchy of Markdown headers
MarkdownH1 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: HEADER1}),
]

MarkdownH2 = Annotated[
    str,
    Field(json_schema_extra={CUSTOM_FIELD: HEADER2}),
]


class main(BaseModel):
    name: MarkdownH1
    title: MarkdownH2
    description: str


class contact(BaseModel):
    email: str
    phone: str


class experience(BaseModel):
    company: MarkdownH1
    position: MarkdownH2
    start_date: str
    end_date: str


class Resume(BaseModel):
    main: main
    contact: contact
    experiences: list[experience]
