from pathlib import Path

from pydantic import BaseModel

from resume_builder.models.constants import CUSTOM_FIELD, MARKDOWN_HEADERS
from resume_builder.template.constants import YAML_FRONT_MATTER
from resume_builder.template.default_resume import DEFAULT_RESUME


def _render_entry(item: BaseModel) -> list[str]:
    lines = []
    for field_name, field_info in type(item).model_fields.items():
        # value of flat field
        value = getattr(item, field_name)

        # extract the custom field metadata
        extra = field_info.json_schema_extra
        markdown_header = extra.get(CUSTOM_FIELD) if isinstance(extra, dict) else None

        if markdown_header in MARKDOWN_HEADERS:
            lines.append(f"{MARKDOWN_HEADERS[markdown_header]} {value}")
        else:
            # Default to a simple string if no model specification
            lines.append(str(value))

        lines.append("")  # Add a blank line after each field for better Markdown formatting

    return lines


def _render_section(model: BaseModel, section_name: str) -> list[str]:
    """
    Renders a Pydantic BaseModel instance as a Markdown section.
    Args:
        model (BaseModel): The Pydantic model instance to render.
        section_name (str): The name of the section, used for the "attrs_block_plugin".
        Returns:
            list[str]: The rendered Markdown lines for the section.
    """
    # [HEADER LINES] : Meta information for the "attrs_block_plugin" to identify the section
    attrs_block_content = f"{{#{section_name}}}"
    attrs_container_section_content_start = "::: section"
    attrs_container_section_content_end = ":::"

    lines = [
        attrs_block_content,
        attrs_container_section_content_start,
    ]

    # [BODY] : Append each field of the model as a Markdown line
    # Use the model's field metadata to determine if a field should be rendered as a Markdown header
    for field_name, field_info in type(model).model_fields.items():
        # Flat value of the field
        value = getattr(model, field_name)

        # extract the custom field metadata
        extra = field_info.json_schema_extra
        markdown_header = extra.get(CUSTOM_FIELD) if isinstance(extra, dict) else None

        if markdown_header in MARKDOWN_HEADERS:
            lines.append(f"{MARKDOWN_HEADERS[markdown_header]} {value}")
        else:
            # Default to a simple string if no model specification
            lines.append(str(value))

        lines.append("")

    # [FOOTER LINES] : Close the section for the "attrs_block_plugin"
    lines.extend(
        [
            attrs_container_section_content_end,
            "",
        ]
    )

    return lines


def _render_section_entries(entries: list[BaseModel], section_name: str) -> list[str]:
    """
    Renders a list of Pydantic BaseModel instances as a Markdown section.
    Args:
        entries (list[BaseModel]): The list of Pydantic model instances to render.
        section_name (str): The name of the section, used for the "attrs_block_plugin".
    Returns:
        list[str]: The rendered Markdown lines for the section.
    """
    # [HEADER LINES]
    attrs_block_content = f"{{#{section_name}}}"
    attrs_container_section_content_start = "::: section"
    attrs_container_section_content_end = ":::"

    lines = [
        attrs_block_content,
        attrs_container_section_content_start,
    ]

    # [BODY] : Append each entry in the list as a Markdown sub-section
    for item in entries:
        lines.extend(_render_entry(item))

    # [FOOTER LINES]
    lines.extend(
        [
            attrs_container_section_content_end,
            "",
        ]
    )

    return lines


def write_model_to_markdown(model: BaseModel, file_path: Path) -> None:
    """
    Writes a Pydantic BaseModel instance to a Markdown file.
    """
    # [HEADER] : Add YAML front matter for optional custom styling
    lines = [YAML_FRONT_MATTER]
    lines.append("")

    # [BODY] : Render each field of the model as a Markdown section
    for field_name in type(model).model_fields:
        value = getattr(model, field_name)

        if isinstance(value, BaseModel):
            lines.extend(_render_section(value, field_name))
        else:
            lines.extend(_render_section_entries(value, field_name))

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
