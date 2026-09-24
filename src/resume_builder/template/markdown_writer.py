from pathlib import Path

from pydantic import BaseModel

from resume_builder.conventions import (
    CUSTOM_FIELD,
    FENCE_CLOSE,
    FENCE_OPEN,
    SECTION_TITLE_LEVEL,
    anchor,
    heading_marker,
)
from resume_builder.template.constants import YAML_FRONT_MATTER
from resume_builder.template.default_resume import DEFAULT_RESUME


def _field_lines(model: BaseModel) -> list[str]:
    """Markdown lines for every field of a model instance - the body of a section."""
    lines = []
    for field_name, field_info in type(model).model_fields.items():
        # value of flat field
        value = getattr(model, field_name)

        # extract the custom field metadata
        extra = field_info.json_schema_extra
        marker = heading_marker(extra.get(CUSTOM_FIELD)) if isinstance(extra, dict) else None

        if marker is not None:
            lines.append(f"{marker} {value}")
        elif isinstance(value, list):
            lines.extend(f"- {line}" for line in value)
        else:
            lines.append(str(value))

        # every field on its own paragraph — and a readable file to hand-edit
        # not necessary for CommonMark except to separate two strings
        lines.append("")

    return lines


def _section_lines(section_id: str, title: str | None, body: list[str]) -> list[str]:
    """
    Wrap a body in the section container: anchor, fence, optional title.
    Args:
        section_id (str): The ID of the section, used for the 'attrs_block_plugin'
        title (str | None): The title of the section.
        body (list[str]): The body content of the section.
    Returns:
        list[str]: The Markdown lines for the section.
    """
    lines = [anchor(section_id), FENCE_OPEN]
    if title is not None:
        lines += [f"{heading_marker(SECTION_TITLE_LEVEL)} {title}", ""]
    lines += body
    lines += [FENCE_CLOSE, ""]
    return lines


def write_model_to_markdown(model: BaseModel, file_path: Path) -> None:
    """
    Create a structured Markdown file from a Pydantic BaseModel instance, with each field written as a separate section.
    Args:
        model (BaseModel): The Pydantic model instance to write.
        file_path (Path): The path to the output Markdown file.
    """
    # [HEADER] : Add YAML front matter for optional custom styling
    lines = [YAML_FRONT_MATTER]
    lines.append("")

    # [BODY] : Write each field of the model as a Markdown section
    for field_name, field_info in type(model).model_fields.items():
        value = getattr(model, field_name)
        models = [value] if isinstance(value, BaseModel) else value
        body: list[str] = []
        for m in models:
            body.extend(_field_lines(m))
        lines.extend(_section_lines(field_name, field_info.title, body))

    file_path.write_text("\n".join(lines), encoding="utf-8")


def init_resume(
    target_dir: Path = Path("."),
    filename: str = "resume.md",
    force: bool = False,
) -> Path:
    """
    Initializes a new resume Markdown file in the specified directory.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    resume_path = target_dir / filename

    if resume_path.exists() and not force:
        raise FileExistsError(f"{resume_path} already exists — pass force=True to overwrite")

    write_model_to_markdown(DEFAULT_RESUME, resume_path)
    return resume_path
