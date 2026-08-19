from pathlib import Path

from pydantic import BaseModel

from resume_builder.template.constants import YAML_FRONT_MATTER
from resume_builder.template.default_resume import DEFAULT_RESUME


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
    lines = [YAML_FRONT_MATTER]
    lines.append(f"# {type(model).__name__}")
    lines.append("")

    for field_name in type(model).model_fields:
        value = getattr(model, field_name)

        lines.append(f"{{#{field_name}}}")
        lines.append("::: section")
        lines.append(f"## {field_name}")

        if isinstance(value, BaseModel):
            lines.extend(_render_bullets(value))
        elif isinstance(value, list):
            for item in value:
                lines.extend(_render_entry(item))
                lines.append("")
        else:
            lines.append(str(value))

        lines.append(":::")
        lines.append("")

        lines.append("")

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
