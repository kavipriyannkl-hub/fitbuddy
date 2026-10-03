# 6. Project Documentation

## Abstract
FitBuddy generates personalized seven-day fitness plans with Google Gemini, accepts user feedback for revisions, supplies goal-based nutrition/recovery tips and saves profiles and complete plan histories. A FastAPI backend renders Jinja2 pages and exposes JSON APIs. SQLite/SQLAlchemy provide persistence, and an authenticated coach dashboard supports review.

## Objectives and scope
Implement the four guide scenarios: personalized plan generation, feedback-driven revision, independent tip generation and coach review. Required profile fields are name, age, weight, goal and intensity. Experience, equipment and duration offer additional customization. Fitness output is general guidance; the app does not diagnose conditions, track exercise completion or measure physical progress.

## System workflow
Profile → validation → Gemini workout and tip → successful save → private result link. Feedback → ownership token lookup → Gemini revision using current profile/prior plan → new saved version. Coach login → profile list → original/revised plan review.

## Installation, operation and API
See README for commands, environment variables, complete route table, security model, persistence limitations and deployment steps. Detailed requirements, data flow, architecture, schema and implementation are in phases 2–5.

## Reference alignment
| Reference scenario | Implementation |
| --- | --- |
| 1. Personalized weekly workout | Profile form and `/generate-workout` |
| 2. Feedback-based revision | `/submit-feedback` and version history |
| 3. Goal-based nutrition/recovery tip | `/nutrition-tip` and separate AI tip function |
| 4. Coach review | Authenticated `/view-all-users` |

## Results and limitations
Automated local tests verify application behavior with controlled AI responses. They do not establish real model quality, successful hosted deployment or user outcomes. Live API verification, real screenshots and demonstration recording should be added after configuring a key. Plan format is requested in the prompt; generated fitness text still needs human review. Hosted SQLite durability depends on persistent storage.

## Future work
Optional user accounts, workout completion tracking, structured response validation, retention/deletion controls and rate limiting can extend this reference implementation.

## References
- [FitBuddy project guide](https://docs.google.com/document/d/1aycIF0DK3Iexn0A0oHgHJM_JP77zSt8w/edit)
- [Seven-phase template folder](https://drive.google.com/drive/folders/1laeXjLiMaqP8hnwvammmyUfAwH95jW0O)
- [Google Gemini model documentation](https://ai.google.dev/gemini-api/docs/models)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy documentation](https://docs.sqlalchemy.org/)
