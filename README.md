# Job management API

React frontend talks to this SAM/Lambda API. After deploy, copy the `ApiUrl` output into `frontend/.env` as `VITE_API_URL`.

## Auth

Every route except `POST /login` requires `Authorization: Bearer <jwt>`. The JWT carries `org_id` and `role`. Lambdas use that org id and ignore any `organization_id` sent by the browser.


| Username | Password |
|---|---|
| `demo` | `DemoJobs1!` |


Change a password:

```bash
python scripts/hash_password.py 'your-new-password'
```

Then pass `DemoPasswordHash` or `ClientPasswordHash` (and `JwtSecret`) in `sam deploy --parameter-overrides`.

## Tests

Unit tests cover the scheduler, recurring dates, passwords/JWTs, and org scoping from the authorizer. They do not need RDS.

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

GitHub Actions runs the same command on every push and pull request (`.github/workflows/test.yml`).

## Deploy

```bash
sam build
sam deploy
```
