# Constants for the resume builder template
BLANK_LINE = "\n\n"

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
HTML_PHONE_CODE = "&#9742;"
HTML_GITHUB_CODE = "&#xf09b;"
CONTACT_DESCRIPTION = (
    f"{HTML_CODE_EMAIL} {EMAIL}{BLANK_LINE}{HTML_PHONE_CODE} {PHONE}{BLANK_LINE}{HTML_GITHUB_CODE} {PERSONAL_WEBSITE}"
)

# Skills part
SKILLS_DESCRIPTION = "R &#9733;&#9733;&#9733;\n\nPython &#9733;&#9733;&#9733;"

# Work experience part
EXPERIENCES = [
    {
        "subtitle": "Acme Corp",
        "title": "Developer",
        "location": "Boston, MA",
        "start_date": "2020-01",
        "end_date": "2021-01",
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
        "start_date": "2022-02",
        "end_date": "2023-01",
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
        "start_date": "2015-09",
        "end_date": "2019-06",
        "description": [
            "Graduated with honors.",
            "Member of the Computer Science Club.",
        ],
    },
    {
        "subtitle": "Stanford University",
        "title": "Master of Science in Software Engineering",
        "location": "Stanford, CA",
        "start_date": "2019-09",
        "end_date": "2021-06",
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
        "start_date": "2019-01",
        "end_date": "2020",
        "description": [
            "Designed and developed a personal website using HTML, CSS, and JavaScript.",
            "Showcased my projects, skills, and experience on the website.",
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
