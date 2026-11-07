from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from fastapi.testclient import TestClient
from src.api.main import app


client = TestClient(app)


@pytest.fixture
def credentials(tmp_path, monkeypatch):
    private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    public_path = tmp_path / "public.pem"
    public_path.write_bytes(public_pem)

    monkeypatch.setenv("A05_JWT_PUBLIC_KEY", str(public_path))

    def token(subject="finance-agent"):
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                "sub": subject,
                "iss": "ai-a05-dev-issuer",
                "aud": "ai-a05-governance",
                "iat": now,
                "exp": now + timedelta(minutes=5),
                "jti": str(uuid4()),
                "roles": ["finance"],
            },
            private,
            algorithm="RS256",
        )

    return token


def payment_request(agent="finance-agent"):
    return {
        "agent_id": agent,
        "action": "payment.create",
        "resource": "erp.payments",
        "context": {
            "amount": 2500,
            "currency": "EUR",
        },
    }


def test_authenticated_request_permitted(credentials):
    response = client.post(
        "/governance/evaluate",
        json=payment_request(),
        headers={
            "Authorization": f"Bearer {credentials()}"
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "PERMIT"


def test_missing_token_rejected(credentials):
    response = client.post(
        "/governance/evaluate",
        json=payment_request(),
    )

    assert response.status_code == 401


def test_agent_impersonation_rejected(credentials):
    response = client.post(
        "/governance/evaluate",
        json=payment_request("finance-agent"),
        headers={
            "Authorization": (
                f"Bearer {credentials('unknown-agent')}"
            )
        },
    )

    assert response.status_code == 403


def test_invalid_token_rejected(credentials):
    response = client.post(
        "/governance/evaluate",
        json=payment_request(),
        headers={"Authorization": "Bearer invalid.token"},
    )

    assert response.status_code == 401


def test_missing_verifier_configuration_fails_closed(
    credentials, monkeypatch
):
    monkeypatch.delenv("A05_JWT_PUBLIC_KEY")

    response = client.post(
        "/governance/evaluate",
        json=payment_request(),
        headers={
            "Authorization": f"Bearer {credentials()}"
        },
    )

    assert response.status_code == 503
