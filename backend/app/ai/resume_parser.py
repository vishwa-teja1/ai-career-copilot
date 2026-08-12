"""
Resume Parser AI module.

Turns raw resume text into the structured JSON contract defined in
app/ai/schema.py via an OpenAI structured-output call. Retries on
transient API errors; raises a typed exception on repeated failure so
the caller (ResumeService) can mark parsing_status="failed" instead of
leaving a profile stuck in "processing" forever.
"""
import json
import logging

from openai import OpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.ai.schema import PARSER_SYSTEM_PROMPT, RESUME_PARSE_SCHEMA
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ResumeParsingError(Exception):
    pass


def _client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise ResumeParsingError(
            "OPENAI_API_KEY is not configured. Set it in your .env to enable AI resume parsing."
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
)
def _call_openai(resume_text: str) -> str:
    client = _client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": PARSER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Resume text:\n\n{resume_text}"},
        ],
        response_format={"type": "json_schema", "json_schema": RESUME_PARSE_SCHEMA},
        temperature=0,  # deterministic extraction, not creative writing
        max_tokens=4000,
    )
    content = response.choices[0].message.content
    if not content:
        raise ResumeParsingError("Empty response from AI parser")
    return content


def parse_resume_text(resume_text: str) -> dict:
    """
    Truncates absurdly long resumes (defensive - real resumes are 1-3 pages)
    and returns the parsed dict, or raises ResumeParsingError.
    """
    max_chars = 20000
    truncated = resume_text[:max_chars]

    try:
        raw_json = _call_openai(truncated)
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        logger.error("AI parser returned invalid JSON: %s", exc)
        raise ResumeParsingError("AI parser returned malformed JSON") from exc
    except Exception as exc:  # noqa: BLE001 - genuinely want to catch/wrap any provider error
        logger.error("AI parser call failed: %s", exc)
        raise ResumeParsingError(f"AI parsing failed: {exc}") from exc

    return parsed
