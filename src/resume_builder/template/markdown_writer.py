import shutil
from pathlib import Path

from pydantic import BaseModel

from resume_builder.conventions import (
    ASSET_CSS_BUILTIN_FILE_NAME,
    ASSET_CSS_USER_FILE_NAME,
    ASSET_JS_BUILTIN_FILE_NAME,
    ASSETS_FOLDER_NAME,
    CUSTOM_FIELD,
    FENCE_CLOSE,
    FENCE_OPEN,
    INIT_RESUME_FILE_NAME,
    SECTION_BREAK,
    SECTION_TITLE_LEVEL,
    anchor,
    heading_marker,
    join_blocks,
)
from resume_builder.models.resume_model import Resume
from resume_builder.template.constants import YAML_FRONT_MATTER
from resume_builder.template.default_resume import DEFAULT_RESUME

RESOURCE_ASSETS_PATH = Path(__file__).parent.parent / "assets"


def _field_blocks(model: BaseModel) -> list[str]:
    """One Markdown block per field - a list field becomes a single block of `- item` lines."""
    blocks: list[str] = []

    for field_name, field_info in type(model).model_fields.items():
        value = getattr(model, field_name)

        extra = field_info.json_schema_extra
        marker = heading_marker(extra.get(CUSTOM_FIELD)) if isinstance(extra, dict) else None

        if marker is not None:
            blocks.append(f"{marker} {value}")
        elif isinstance(value, list):
            blocks.append("\n".join(f"- {item}" for item in value))
        else:
            blocks.append(str(value))

    return blocks


def _section(section_id: str, title: str | None, body: list[str]) -> str:
    """Wrap body blocks in the section container."""
    blocks = [anchor(section_id), FENCE_OPEN]
    if title is not None:
        blocks.append(f"{heading_marker(SECTION_TITLE_LEVEL)} {title}")
    blocks += body
    blocks.append(FENCE_CLOSE)
    return join_blocks(blocks)


def _write_model_to_markdown(model: Resume, file_path: Path) -> None:
    """
    Create a structured Markdown file from a Pydantic BaseModel instance, with each field written as a separate section.
    Args:
        model (Resume): The internal model instance to write (not a generic BaseModel).
        file_path (Path): The path to the output Markdown file.
    """
    sections: list[str] = []

    for field_name, field_info in type(model).model_fields.items():
        value = getattr(model, field_name)

        # a section holds either one model (contact) or a list of them (experiences)
        section_models = [value] if isinstance(value, BaseModel) else value

        body: list[str] = []
        for section_model in section_models:
            body.extend(_field_blocks(section_model))

        sections.append(_section(field_name, field_info.title, body))

    document = join_blocks([YAML_FRONT_MATTER] + sections, SECTION_BREAK)
    file_path.write_text(document + "\n", encoding="utf-8")


def init_resume(path: str | Path = INIT_RESUME_FILE_NAME) -> Path:
    """
    Initializes a new resume Markdown file in a folder (file and folder have same name).
     Rendering needs assets: they are copied into the `resume_builder_files` folder next to it.
    Args:
        path (str | Path): Used both as a name folder or as a filename (with '.md' extension or not).
    Returns:
        Path: The path of the markdown file on the disk.
    Raises:
        ValueError: If path has an extension other than '.md'.
        FileExistsError: If the directory already exists (even empty).
    Examples:
        >>> init_resume()  # resume/resume.md
        >>> init_resume("cvs/jane")  # cvs/jane/jane.md, assets in cvs/jane/resume_builder_files/
    """
    md_path = Path(path)
    if md_path.suffix not in ("", ".md"):
        raise ValueError("Only '.md' extension is accepted")

    name = md_path.stem if md_path.suffix == ".md" else md_path.name
    output_dir = md_path.parent / name
    md_path = output_dir / f"{name}.md"

    output_dir.mkdir(parents=True, exist_ok=False)

    _write_model_to_markdown(DEFAULT_RESUME, md_path)

    # copy on disk all files needed for rendering
    dir_assets = output_dir / ASSETS_FOLDER_NAME
    dir_assets.mkdir(parents=True, exist_ok=False)

    files = [ASSET_CSS_USER_FILE_NAME, ASSET_CSS_BUILTIN_FILE_NAME, ASSET_JS_BUILTIN_FILE_NAME]
    for asset_name in files:
        shutil.copy(RESOURCE_ASSETS_PATH / asset_name, dir_assets)
    return md_path
