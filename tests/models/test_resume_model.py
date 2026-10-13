import pytest
from pydantic import BaseModel

from resume_builder.models.resume_model import BriefEntry, Entry, Main, Resume, TitledEntry
from resume_builder.template.constants import EMAIL, EXPERIENCES, PERSONAL_WEBSITE, PHONE


# Every class have a strict structured and ordered fields
@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (Main, ["user_name", "title_position", "description"]),
        (BriefEntry, ["description"]),
        (TitledEntry, ["title", "description"]),
        (Entry, ["title", "subtitle", "location", "start_date", "end_date", "description"]),
    ],
)
def test_model_fields_are_declared_in_contract_order(model: BaseModel, expected: list[str]) -> None:
    # test
    assert list(model.model_fields.keys()) == expected


# Every class have type declared of Field info
@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (Main, {"user_name": {"markdown": 1}, "title_position": {"markdown": 3}, "description": None}),
        (BriefEntry, {"description": None}),
        (TitledEntry, {"title": {"markdown": 3}, "description": None}),
        (
            Entry,
            {
                "title": {"markdown": 3},
                "subtitle": {"markdown": 4},
                "location": None,
                "start_date": None,
                "end_date": None,
                "description": None,
            },
        ),
    ],
)
def test_model_header_field_extra(model: BaseModel, expected: dict[str, dict]) -> None:
    # test
    for field in model.model_fields:
        assert model.model_fields[field].json_schema_extra == expected[field]


def test_resume_model(default_resume: Resume) -> None:
    # when
    resume = default_resume

    # then
    assert isinstance(resume, Resume)
    assert resume.main.user_name == "John Doe"
    assert resume.main.title_position == "Project Manager"
    assert resume.main.description == "Experienced software engineer with a passion for developing innovative programs."

    description = resume.contact.description
    assert isinstance(description, str)
    blocks = description.split("\n\n")

    assert len(blocks) == 3
    assert blocks[0] == f"&#9993; {EMAIL}"
    assert blocks[1] == f"&#9742; {PHONE}"
    assert blocks[2].startswith("<svg") and blocks[2].endswith(f" {PERSONAL_WEBSITE}")

    assert len(resume.experiences) == 3
    i = 0
    for entry in default_resume.experiences:
        assert entry.model_dump() == EXPERIENCES[i]
        i = i + 1
