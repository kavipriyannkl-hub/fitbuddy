# 5. Project Development Phase

## Implementation
1. Create a virtual environment and install `requirements.txt`.
2. Copy `.env.example` to `.env` and configure Gemini/admin variables.
3. Run `uvicorn app.main:app --reload --no-access-log`.
4. Submit profile data through `/generate-workout` or `/api/workouts`.
5. Generate workout and independent nutrition tip; then save the profile and first plan.
6. Return a private result URL with saved content.
7. Submit feedback; use current profile and previous plan to generate a new version.
8. Log in to `/view-all-users` to compare histories.

## Verification
`python -m pytest -q` tests form/JSON workflows with a mocked AI service and an isolated database. Covered behavior: valid profile creation, feedback history, goal-based tips, validation failures, unknown token rejection, protected coach access, failure rollback and escaped output. AI provider tests cover missing credentials; live provider calls need a real configured key.

## Local versus hosted operation
Local SQLite survives process restarts in the working directory. Render's supplied free demo configuration has temporary storage. Durable hosting requires a persistent disk and corresponding SQLite URL; see README. Health checks confirm server availability, not Gemini key validity or plan quality.

## User acceptance testing
| Scenario | Procedure | Expected result | Current evidence |
| --- | --- | --- | --- |
| Create plan | Submit valid synthetic profile | Seven-day workout, tip and saved profile | Automated mocked-AI workflow passed |
| Revise plan | Submit feedback on existing private URL | New version with original retained | Automated history test passed |
| Request tip | Choose goal and submit standalone form | Goal-specific tip displayed | Automated mocked-AI form/API tests passed |
| Coach review | Try dashboard without/with admin login | Unauthorized rejected; coach sees all versions | Automated authorization/history tests passed |
| Validation | Submit negative weight or blank name | Request rejected without save | Automated validation tests passed |
| Provider failure | Simulate unavailable/empty provider response | Safe error; existing history preserved | Automated failure tests passed |
| Live content quality | Run all four scenarios with configured Gemini key | Relevant, complete, safe output | Pending real API access |

## Performance testing plan
Measure home/health/database retrieval separately from Gemini generation. Record machine, concurrency, p50/p95 latency, errors, model and quota. Exercise multiple concurrent requests against a temporary test database; verify history remains valid. AI calls have a 60-second timeout. Test provider timeout/quota failures and confirm no partial profiles/revisions. Local functional tests do not establish production latency, capacity or performance; live load results are intentionally pending. Do not load-test a hosted service without suitable service limits.
