"""
Integration tests for the auth module, run against the FastAPI TestClient
+ in-memory SQLite (see conftest.py). Covers the full register -> verify OTP
-> login -> refresh lifecycle plus the security-relevant edge cases
(duplicate email, wrong password, unverified login, expired/garbage tokens).
"""
from app.repositories.user_repository import UserRepository


def _register(client, email, password="StrongPass1", full_name="Teja Rao"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": full_name, "password": password},
    )


def _get_otp_for(db_session, email):
    repo = UserRepository(db_session)
    user = repo.get_by_email(email)
    otp = user.otp_codes[-1]
    return otp.code


class TestRegister:
    def test_register_creates_unverified_user(self, client, unique_email):
        resp = _register(client, unique_email)
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == unique_email
        assert body["is_email_verified"] is False

    def test_register_duplicate_email_rejected(self, client, unique_email):
        _register(client, unique_email)
        resp = _register(client, unique_email)
        assert resp.status_code == 400

    def test_register_weak_password_rejected(self, client, unique_email):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "full_name": "Teja Rao", "password": "weak"},
        )
        assert resp.status_code == 422

    def test_register_password_without_uppercase_rejected(self, client, unique_email):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": unique_email, "full_name": "Teja Rao", "password": "lowercase123"},
        )
        assert resp.status_code == 422


class TestOTPAndLogin:
    def test_login_before_verification_fails(self, client, unique_email):
        _register(client, unique_email)
        resp = client.post("/api/v1/auth/login", json={"email": unique_email, "password": "StrongPass1"})
        assert resp.status_code == 403

    def test_verify_otp_then_login_succeeds(self, client, db_session, unique_email):
        _register(client, unique_email)
        code = _get_otp_for(db_session, unique_email)

        verify_resp = client.post("/api/v1/auth/verify-otp", json={"email": unique_email, "code": code})
        assert verify_resp.status_code == 200
        assert "access_token" in verify_resp.json()

        login_resp = client.post("/api/v1/auth/login", json={"email": unique_email, "password": "StrongPass1"})
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        assert tokens["token_type"] == "bearer"

    def test_wrong_otp_rejected(self, client, unique_email):
        _register(client, unique_email)
        resp = client.post("/api/v1/auth/verify-otp", json={"email": unique_email, "code": "000000"})
        assert resp.status_code == 400

    def test_login_wrong_password_rejected(self, client, db_session, unique_email):
        _register(client, unique_email)
        code = _get_otp_for(db_session, unique_email)
        client.post("/api/v1/auth/verify-otp", json={"email": unique_email, "code": code})

        resp = client.post("/api/v1/auth/login", json={"email": unique_email, "password": "WrongPass1"})
        assert resp.status_code == 401

    def test_login_nonexistent_user_rejected(self, client):
        resp = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "StrongPass1"})
        assert resp.status_code == 401


class TestTokensAndMe:
    def _verified_tokens(self, client, db_session, email):
        _register(client, email)
        code = _get_otp_for(db_session, email)
        client.post("/api/v1/auth/verify-otp", json={"email": email, "code": code})
        login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass1"})
        return login_resp.json()

    def test_get_me_with_valid_token(self, client, db_session, unique_email):
        tokens = self._verified_tokens(client, db_session, unique_email)
        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == unique_email

    def test_get_me_without_token_rejected(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)

    def test_get_me_with_garbage_token_rejected(self, client):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.valid.token"})
        assert resp.status_code == 401

    def test_refresh_token_issues_new_access_token(self, client, db_session, unique_email):
        tokens = self._verified_tokens(client, db_session, unique_email)
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_refresh_with_access_token_rejected(self, client, db_session, unique_email):
        """An access token must not be usable as a refresh token."""
        tokens = self._verified_tokens(client, db_session, unique_email)
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
        assert resp.status_code == 401
