"""
The strict JSON schema the resume-parsing LLM call must conform to.
Passed as an OpenAI "json_schema" structured output so the model literally
cannot return malformed or freeform text - every field here maps 1:1 to a
column in app/models/profile.py.
"""

RESUME_PARSE_SCHEMA = {
    "name": "candidate_profile",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "full_name": {"type": ["string", "null"]},
            "headline": {"type": ["string", "null"], "description": "One-line professional headline, e.g. 'Final-year IT student focused on ML'"},
            "phone": {"type": ["string", "null"]},
            "location": {"type": ["string", "null"]},
            "summary": {"type": ["string", "null"], "description": "2-4 sentence professional summary, derived ONLY from resume content"},
            "linkedin_url": {"type": ["string", "null"]},
            "github_url": {"type": ["string", "null"]},
            "portfolio_url": {"type": ["string", "null"]},
            "languages_spoken": {"type": "array", "items": {"type": "string"}},
            "skills": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string"},
                        "category": {"type": ["string", "null"], "enum": ["language", "framework", "tool", "database", "cloud", "soft-skill", None]},
                        "proficiency": {"type": ["string", "null"], "enum": ["beginner", "intermediate", "advanced", None]},
                    },
                    "required": ["name", "category", "proficiency"],
                },
            },
            "experiences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "company": {"type": "string"},
                        "title": {"type": "string"},
                        "location": {"type": ["string", "null"]},
                        "start_date": {"type": ["string", "null"], "description": "Format YYYY-MM if determinable"},
                        "end_date": {"type": ["string", "null"]},
                        "is_current": {"type": "boolean"},
                        "description": {"type": ["string", "null"]},
                        "bullet_points": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["company", "title", "location", "start_date", "end_date", "is_current", "description", "bullet_points"],
                },
            },
            "internships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "organization": {"type": "string"},
                        "role": {"type": "string"},
                        "start_date": {"type": ["string", "null"]},
                        "end_date": {"type": ["string", "null"]},
                        "description": {"type": ["string", "null"]},
                    },
                    "required": ["organization", "role", "start_date", "end_date", "description"],
                },
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "institution": {"type": "string"},
                        "degree": {"type": "string"},
                        "field_of_study": {"type": ["string", "null"]},
                        "start_date": {"type": ["string", "null"]},
                        "end_date": {"type": ["string", "null"]},
                        "grade": {"type": ["string", "null"]},
                    },
                    "required": ["institution", "degree", "field_of_study", "start_date", "end_date", "grade"],
                },
            },
            "projects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": ["string", "null"]},
                        "tech_stack": {"type": "array", "items": {"type": "string"}},
                        "url": {"type": ["string", "null"]},
                    },
                    "required": ["title", "description", "tech_stack", "url"],
                },
            },
            "certifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string"},
                        "issuer": {"type": ["string", "null"]},
                        "issue_date": {"type": ["string", "null"]},
                        "credential_url": {"type": ["string", "null"]},
                    },
                    "required": ["name", "issuer", "issue_date", "credential_url"],
                },
            },
            "achievements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": ["string", "null"]},
                        "date": {"type": ["string", "null"]},
                    },
                    "required": ["title", "description", "date"],
                },
            },
        },
        "required": [
            "full_name", "headline", "phone", "location", "summary",
            "linkedin_url", "github_url", "portfolio_url", "languages_spoken",
            "skills", "experiences", "internships", "education", "projects",
            "certifications", "achievements",
        ],
    },
}

PARSER_SYSTEM_PROMPT = """You are a precise resume-parsing engine.

Extract information from the resume text into the given JSON schema.

STRICT RULES:
1. Only extract information that is explicitly present in the resume text.
2. NEVER invent, infer, or embellish experience, skills, dates, or achievements
   that are not literally stated or unambiguously implied by the text.
3. If a field is not present in the resume, return null (or an empty array for
   list fields). Do not guess.
4. Normalize dates to "YYYY-MM" where the resume gives enough information;
   otherwise leave the original text or null - never fabricate a specific date.
5. Do not editorialize, rate, or comment on the candidate's quality - only extract.
6. Preserve technical terms, tool names, and skill names exactly as written
   (correct only obvious OCR/typo artifacts, e.g. "Reaet" -> "React").
"""
