from resume_builder.conventions import ASSETS_FOLDER_NAME, PATH_FILE_YAML_CSS, join_blocks

# Constants for the resume builder template

# Main part
LAST_POSITION = "Project Manager"

USER_NAME_VALUE = "John Doe"
TITLE_POSITION_VALUE = LAST_POSITION
DESCRIPTION_MAIN_VALUE = "Experienced software engineer with a passion for developing innovative programs."

# Contact part
EMAIL = "john.doe@example.com"
PHONE = "123-456-7890"
PERSONAL_WEBSITE = "https://johndoe.com"
HTML_CODE_EMAIL = "&#9993;"
HTML_CODE_PHONE = "&#9742;"

# GitHub has no Unicode character — it is a brand mark, and the Font Awesome
# codepoint we used before renders as an empty box without that font loaded.
# Inline SVG needs no font at all: `html=True` on the parser passes it through,
# `1em` makes it follow the text size and `currentColor` its colour, so the
# stylesheet needs no rule for it.
GITHUB_ICON = (
    '<svg viewBox="0 0 16 16" width="1em" height="1em" fill="currentColor"'
    ' style="vertical-align:-0.15em"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53'
    " 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09"
    "-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87"
    ".87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15"
    "-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53"
    "-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75"
    "-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012"
    ' 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'
)

EMAIL_LINE = f"{HTML_CODE_EMAIL} {EMAIL}"
PHONE_LINE = f"{HTML_CODE_PHONE} {PHONE}"
WEBSITE_LINE = f"{GITHUB_ICON} {PERSONAL_WEBSITE}"

CONTACT_DESCRIPTION = join_blocks([EMAIL_LINE, PHONE_LINE, WEBSITE_LINE])

# Skills part
STAR_SYMBOL_FULL = "&#9733;"
STAR_SYMBOL_EMPTY = "&#9734;"
R_RATING_SKILL_SYMBOL = f"R {STAR_SYMBOL_FULL * 5}"
PYTHON_RATING_SKILL_SYMBOL = f"Python {STAR_SYMBOL_FULL * 4}{STAR_SYMBOL_EMPTY * 1}"
SKILLS_DESCRIPTION = join_blocks([R_RATING_SKILL_SYMBOL, PYTHON_RATING_SKILL_SYMBOL])

# Work experience part
EXPERIENCES = [
    {
        "subtitle": "Acme Corp",
        "title": "Developer",
        "location": "Boston, MA",
        "start_date": "2022-02",
        "end_date": "2023-01",
        "description": [
            "Developed and maintained web applications.",
            "Collaborated with cross-functional teams to define, design, and ship new features.",
        ],
    },
    {
        "subtitle": "Globex Corporation",
        "title": "Software Engineer",
        "location": "New York, NY",
        "start_date": "2021-02",
        "end_date": "2022-01",
        "description": [
            "Worked on various software development projects.",
            "Collaborated with cross-functional teams to deliver high-quality products.",
        ],
    },
    {
        "subtitle": "Initech",
        "title": LAST_POSITION,
        "location": "San Francisco, CA",
        "start_date": "2020-01",
        "end_date": "2021-01",
        "description": [
            "Led a team of developers to successfully deliver multiple projects on time and within budget.",
            "Implemented agile methodologies to improve team productivity and collaboration.",
        ],
    },
]


# Education part
EDUCATION = [
    {
        "subtitle": "Massachusetts Institute of Technology",
        "title": "Bachelor of Science in Computer Science",
        "location": "Cambridge, MA",
        "start_date": "2019-09",
        "end_date": "2021-06",
        "description": [
            "Graduated with honors.",
            "Member of the Computer Science Club.",
        ],
    },
    {
        "subtitle": "Stanford University",
        "title": "Master of Science in Software Engineering",
        "location": "Stanford, CA",
        "start_date": "2015-09",
        "end_date": "2019-06",
        "description": [
            "Completed a thesis on machine learning algorithms.",
            "Participated in various hackathons and coding competitions.",
        ],
    },
]


# Personal projects part
PERSONAL_PROJECTS = [
    {
        "subtitle": "Open Source Contributor",
        "title": "Contributor to various open source projects",
        "location": "Boston, MA",
        "start_date": "2018-01",
        "end_date": "Present",
        "description": [
            "Contributed to several open source projects on GitHub.",
            "Implemented new features and fixed bugs in existing projects.",
        ],
    },
    {
        "subtitle": "Personal Website",
        "title": "Developed a personal website to showcase my portfolio",
        "location": "Boston, MA",
        "start_date": "2018",
        "end_date": "2019",
        "description": "Designed and developed a personal website using HTML, CSS, and JavaScript.",
    },
]


# Languages part
LANGUAGES = [
    {
        "title": "French",
        "description": "Reading, Writing, Speaking",
    },
    {
        "title": "Spanish",
        "description": "Reading, Writing, Speaking",
    },
]

# yaml front matter template
YAML_FRONT_MATTER = f"""---
# Optional: your own stylesheets, loaded after resume.css, in the order below.
# Put them in a folder named "{ASSETS_FOLDER_NAME}" next to your Markdown file.
# css:
#   - {PATH_FILE_YAML_CSS}
---"""
