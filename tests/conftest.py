import os

import pytest

from auth.tokens import create_token

TEST_JWT_SECRET = "ci-test-jwt-secret"


@pytest.fixture
def jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", TEST_JWT_SECRET)
    return TEST_JWT_SECRET


@pytest.fixture
def auth_event():
    def _event(organization_id=1, role="client", username="client"):
        return {
            "requestContext": {
                "authorizer": {
                    "organization_id": str(organization_id),
                    "role": role,
                    "username": username,
                }
            }
        }

    return _event


@pytest.fixture
def bearer_token(jwt_secret):
    def _token(username="demo", organization_id=1, role="demo", hours=12):
        return create_token(username, organization_id, role, jwt_secret, hours=hours)

    return _token
