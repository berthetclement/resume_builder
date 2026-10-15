import pytest
from pydantic import BaseModel

from resume_builder.models.resume_model import BriefEntry, Entry, Main, Resume, TitledEntry


# Every class have a strict structured and ordered fields
@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (Main, ["user_name", "title_position", "description"]),
        (BriefEntry, ["description"]),
        (TitledEntry, ["title", "description"]),
        (Entry, ["title", "subtitle", "location", "start_date", "end_date", "description"]),
        (Resume, ["main", "contact", "skills", "experiences", "education", "personal_projects", "languages"]),
    ],
)
def test_model_fields_are_declared_in_contract_order(model: type[BaseModel], expected: list[str]) -> None:
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
def test_model_header_field_extra(model: type[BaseModel], expected: dict[str, dict[str, int] | None]) -> None:
    # test
    model_dict_extra = {field: info.json_schema_extra for field, info in model.model_fields.items()}
    assert model_dict_extra == expected


def test_resume_section_titles() -> None:
    # given
    expected_dict_title = {
        "main": None,
        "contact": "Contact Information",
        "skills": "Skills",
        "experiences": "Work Experience",
        "education": "Education",
        "personal_projects": "Personal Projects",
        "languages": "Languages",
    }
    # test
    model_dict_title = {field: info.title for field, info in Resume.model_fields.items()}
    assert model_dict_title == expected_dict_title


# No optional fields: a default (None, "") leaves a line missing or empty
# and a hole in an Entry shifts every CSS position after it
@pytest.mark.parametrize(
    "model",
    [
        Main,
        BriefEntry,
        TitledEntry,
        Entry,
        Resume,
    ],
)
def test_model_all_fields_are_required(model: type[BaseModel]) -> None:
    # test
    for field_name, field_info in model.model_fields.items():
        assert field_info.is_required(), f"Field {field_name} in model {model.__name__} is not required"
