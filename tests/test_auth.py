import pytest

from auth.authorizer import lambda_handler as authorize
from auth.passwords import hash_password, verify_password
from auth.tokens import decode_token
from org import parse_organization_id, require_client_role, require_organization


def test_password_round_trip():
    stored = hash_password("DemoJobs1!")
    assert verify_password("DemoJobs1!", stored)
    assert not verify_password("wrong-password", stored)


def test_password_rejects_malformed_hash():
    assert verify_password("secret", "not-a-hash") is False
    assert verify_password("", "ab:cd") is False


def test_token_includes_org_and_role(jwt_secret):
    from auth.tokens import create_token

    token = create_token("demo", 2, "demo", jwt_secret)
    payload = decode_token(token, jwt_secret)
    assert payload["sub"] == "demo"
    assert payload["org_id"] == 2
    assert payload["role"] == "demo"


def test_authorizer_allows_valid_bearer_token(jwt_secret, bearer_token):
    token = bearer_token(username="client", organization_id=2, role="client")
    policy = authorize(
        {
            "authorizationToken": f"Bearer {token}",
            "methodArn": "arn:aws:execute-api:us-east-2:123:abc/Prod/GET/jobs",
        },
        None,
    )
    assert policy["policyDocument"]["Statement"][0]["Effect"] == "Allow"
    assert policy["context"]["organization_id"] == "2"
    assert policy["context"]["role"] == "client"
    assert policy["policyDocument"]["Statement"][0]["Resource"].endswith("/*/*")


def test_authorizer_rejects_invalid_token(jwt_secret):
    with pytest.raises(Exception, match="Unauthorized"):
        authorize(
            {
                "authorizationToken": "Bearer nope",
                "methodArn": "arn:aws:execute-api:us-east-2:123:abc/Prod/GET/jobs",
            },
            None,
        )


def test_org_id_comes_from_authorizer_not_query_string(auth_event):
    event = auth_event(organization_id=7)
    event["queryStringParameters"] = {"organization_id": "99"}
    org_id, err = parse_organization_id(event, {"organization_id": 99})
    assert err is None
    assert org_id == 7


def test_missing_authorizer_is_unauthorized():
    org_id, err = parse_organization_id({"queryStringParameters": {"organization_id": "1"}})
    assert org_id is None
    assert err["statusCode"] == 401


def test_require_organization_uses_token_org(monkeypatch, auth_event):
    import org as org_module

    monkeypatch.setattr(org_module, "fetch_all", lambda *_args, **_kwargs: [{"id": 2}])
    org_id, err = require_organization(auth_event(organization_id=2))
    assert err is None
    assert org_id == 2


def test_require_organization_404_when_org_missing(monkeypatch, auth_event):
    import org as org_module

    monkeypatch.setattr(org_module, "fetch_all", lambda *_args, **_kwargs: [])
    org_id, err = require_organization(auth_event(organization_id=99))
    assert org_id is None
    assert err["statusCode"] == 404


def test_demo_role_cannot_create_organizations(auth_event):
    err = require_client_role(auth_event(role="demo"))
    assert err["statusCode"] == 403
    assert require_client_role(auth_event(role="client")) is None
