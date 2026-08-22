LAST_POSITION = "Project Manager"

NAME = "John Doe"
TITLE = LAST_POSITION
DESCRIPTION = "Experienced software engineer with a passion for developing innovative programs."
EMAIL = "john.doe@example.com"
PHONE = "123-456-7890"

EXPERIENCES = [
    {"company": "Acme Corp", "position": "Developer", "start_date": "2020-01-01", "end_date": "2021-01-01"},
    {
        "company": "Globex Corporation",
        "position": "Software Engineer",
        "start_date": "2021-02-01",
        "end_date": "2022-01-01",
    },
    {"company": "Initech", "position": LAST_POSITION, "start_date": "2022-02-01", "end_date": "2023-01-01"},
]


# yaml front matter example
YAML_FRONT_MATTER = """---
# Optional: add custom styling by uncommenting and editing the lines below
# css:
#   - my-theme.css
---
"""
