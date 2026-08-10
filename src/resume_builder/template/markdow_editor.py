from pathlib import Path

from pydantic import BaseModel


def _render_bullets(nested: BaseModel) -> list[str]:
    return [f"- **{name}**: {getattr(nested, name)}" for name in type(nested).model_fields]


def _render_entry(item: BaseModel) -> list[str]:
    heading_field, *bullet_fields = type(item).model_fields
    lines = [f"### {getattr(item, heading_field)}", ""]
    lines.extend(f"- **{name}**: {getattr(item, name)}" for name in bullet_fields)
    return lines


def write_model_to_markdown(model: BaseModel, file_path: Path) -> None:
    """
    Writes a Pydantic BaseModel instance to a Markdown file.
    """
    lines = [f"# {type(model).__name__}", ""]

    for field_name in type(model).model_fields:
        value = getattr(model, field_name)
        lines.append(f"## {field_name}")

        if isinstance(value, BaseModel):
            lines.extend(_render_bullets(value))
        elif isinstance(value, list):
            for item in value:
                lines.extend(_render_entry(item))
                lines.append("")
        else:
            lines.append(str(value))

        lines.append("")

    file_path.write_text("\n".join(lines), encoding="utf-8")
