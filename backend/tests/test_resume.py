"""
Tests for the resume upload + parsing pipeline. The OpenAI call itself is
mocked (unit tests must not depend on a live API key/network) - the parser's
prompt/schema wiring is exercised in test_ai_parser.py's contract checks,
and here we verify the upload endpoint's validation, auth, and DB write
behavior end-to-end.
"""
import io
from unittest.mock import patch

from app.repositories.user_repository import UserRepository

SAMPLE_PARSED_RESUME = {
    "full_name": "Teja Rao",
    "headline": "Final-year IT student focused on ML",
    "phone": "+91 9000000000",
    "location": "Hyderabad, India",
    "summary": "Final-year IT student with hands-on ML and full-stack experience.",
    "linkedin_url": None,
    "github_url": "https://github.com/example",
    "portfolio_url": None,
    "languages_spoken": ["English", "Telugu"],
    "skills": [{"name": "Python", "category": "language", "proficiency": "advanced"}],
    "experiences": [],
    "internships": [
        {
            "organization": "GoFr Summer of Code",
            "role": "Open Source Contributor",
            "start_date": "2025-06",
            "end_date": "2025-08",
            "description": "Contributed to the GoFr framework.",
        }
    ],
    "education": [
        {
            "institution": "Vardhaman College of Engineering",
            "degree": "B.Tech",
            "field_of_study": "Information Technology",
            "start_date": "2023-08",
            "end_date": "2027-05",
            "grade": None,
        }
    ],
    "projects": [],
    "certifications": [],
    "achievements": [],
}


def _verified_client(client, db_session, email):
    client.post("/api/v1/auth/register", json={"email": email, "full_name": "Teja Rao", "password": "StrongPass1"})
    repo = UserRepository(db_session)
    user = repo.get_by_email(email)
    code = user.otp_codes[-1].code
    client.post("/api/v1/auth/verify-otp", json={"email": email, "code": code})
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass1"})
    return login_resp.json()["access_token"]


class TestResumeUpload:
    def test_upload_rejects_unsupported_file_type(self, client, db_session, unique_email):
        token = _verified_client(client, db_session, unique_email)
        resp = client.post(
            "/api/v1/resume/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("resume.txt", io.BytesIO(b"plain text resume"), "text/plain")},
        )
        assert resp.status_code == 415

    def test_upload_rejects_unauthenticated_request(self, client):
        resp = client.post(
            "/api/v1/resume/upload",
            files={"file": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
        )
        assert resp.status_code in (401, 403)

    @patch("app.services.resume_service.parse_resume_text")
    @patch("app.services.resume_service.extract_text")
    def test_upload_success_builds_structured_profile(self, mock_extract, mock_parse, client, db_session, unique_email):
        mock_extract.return_value = "Teja Rao\nFinal-year IT student...\n(long enough resume text)"
        mock_parse.return_value = SAMPLE_PARSED_RESUME

        token = _verified_client(client, db_session, unique_email)
        resp = client.post(
            "/api/v1/resume/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake pdf bytes"), "application/pdf")},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["parsing_status"] == "completed"

        profile_resp = client.get("/api/v1/profile/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_resp.status_code == 200
        profile = profile_resp.json()
        assert profile["full_name"] == "Teja Rao"
        assert profile["skills"][0]["name"] == "Python"
        assert profile["education"][0]["institution"] == "Vardhaman College of Engineering"
        assert profile["internships"][0]["organization"] == "GoFr Summer of Code"

    @patch("app.services.resume_service.parse_resume_text")
    @patch("app.services.resume_service.extract_text")
    def test_upload_marks_failed_status_on_parser_error(self, mock_extract, mock_parse, client, db_session, unique_email):
        from app.ai.resume_parser import ResumeParsingError

        mock_extract.return_value = "Some resume text that is long enough to pass validation checks."
        mock_parse.side_effect = ResumeParsingError("AI provider timed out")

        token = _verified_client(client, db_session, unique_email)
        resp = client.post(
            "/api/v1/resume/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake pdf bytes"), "application/pdf")},
        )
        assert resp.status_code == 502

        profile_resp = client.get("/api/v1/profile/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_resp.json()["parsing_status"] == "failed"


class TestProfileUpdate:
    @patch("app.services.resume_service.parse_resume_text")
    @patch("app.services.resume_service.extract_text")
    def test_manual_profile_edit_after_parsing(self, mock_extract, mock_parse, client, db_session, unique_email):
        mock_extract.return_value = "Resume text long enough to pass the extraction validity check."
        mock_parse.return_value = SAMPLE_PARSED_RESUME

        token = _verified_client(client, db_session, unique_email)
        client.post(
            "/api/v1/resume/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
        )

        patch_resp = client.patch(
            "/api/v1/profile/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"headline": "Aspiring ML Engineer | Data Analyst"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["headline"] == "Aspiring ML Engineer | Data Analyst"
        # Untouched fields should survive the partial update.
        assert patch_resp.json()["full_name"] == "Teja Rao"
