# Constants for the resume builder template
# Main part
LAST_POSITION = "Project Manager"

USER_NAME_VALUE = "John Doe"
TITLE_POSITION_VALUE = LAST_POSITION
DESCRIPTION_MAIN_VALUE = "Experienced software engineer with a passion for developing innovative programs."

# Contact part
CONTACT_SECTION_TITLE = "Contact Information"
EMAIL = "john.doe@example.com"
PHONE = "123-456-7890"
PERSONAL_WEBSITE = "https://johndoe.com"

# Work experience part
WORK_EXPERIENCE_TITLE_NAME = "WORK EXPERIENCE"
EXPERIENCES = [
    {
        "company": "Acme Corp",
        "position": "Developer",
        "location": "Boston, MA",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01",
        "description": [
            "Developed and maintained web applications.",
            "Collaborated with cross-functional teams to define, design, and ship new features.",
        ],
    },
    {
        "company": "Globex Corporation",
        "position": "Software Engineer",
        "location": "New York, NY",
        "start_date": "2021-02-01",
        "end_date": "2022-01-01",
        "description": [
            "Worked on various software development projects.",
            "Collaborated with cross-functional teams to deliver high-quality products.",
        ],
    },
    {
        "company": "Initech",
        "position": LAST_POSITION,
        "location": "San Francisco, CA",
        "start_date": "2022-02-01",
        "end_date": "2023-01-01",
        "description": [
            "Led a team of developers to successfully deliver multiple projects on time and within budget.",
            "Implemented agile methodologies to improve team productivity and collaboration.",
        ],
    },
]


# yaml front matter example
YAML_FRONT_MATTER = """---
# Optional: add custom styling by uncommenting and editing the lines below
# css:
#   - my-theme.css
---
"""
