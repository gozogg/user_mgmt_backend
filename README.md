# Job management API

React frontend talks to this SAM/Lambda API. After deploy, copy the `ApiUrl` output into `frontend/.env` as `VITE_API_URL`.

## Auth

Every route except `POST /login` requires `Authorization: Bearer <jwt>`. The JWT carries `org_id` and `role`. Lambdas use that org id and ignore any `organization_id` sent by the browser.

Default users (change these before sharing a live client account):

| Username | Password | Role | Org id (SAM param) |
|---|---|---|---|
| `demo` | `DemoJobs1!` | demo | `DemoOrgId` (default `1`) |
| `client` | `ClientJobs1!` | client | `ClientOrgId` (default `1`) |

Both default to organization `1` so the app works with your current data. For a recruiter-safe demo, create a second organization, seed fake clients/jobs, and deploy with `DemoOrgId` set to that id.

Change a password:

```bash
python scripts/hash_password.py 'your-new-password'
```

Then pass `DemoPasswordHash` or `ClientPasswordHash` (and `JwtSecret`) in `sam deploy --parameter-overrides`.

## Deploy

```bash
sam build
sam deploy
```
