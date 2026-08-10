from pathlib import Path

from pydantic import BaseModel


def write_model_to_markdown(model: BaseModel, file_path: Path) -> None:
    """
    Writes a Pydantic BaseModel instance to a Markdown file.
    """
    if not isinstance(model, BaseModel):
        raise ValueError("Input must be a Pydantic BaseModel instance")

    with open(file_path, "w") as f:
        f.write(f"# {model.__class__.__name__}\n\n")
        for field_name, field_value in model.model_dump().items():
            f.write(f"## {field_name}\n")
            f.write(f"{field_value}\n\n")
