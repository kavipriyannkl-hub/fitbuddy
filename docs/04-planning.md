# 4. Project Planning Phase

## Milestones
| Reference milestone | Work package | Deliverable |
| --- | --- | --- |
| 1. Model selection and architecture | Select configurable workout/tip models; define data and modules; set up environment | AI configuration, schema, requirements |
| 2. Core functionality | Workout generation, independent tip and feedback revisions | `app/ai.py`, persistence helpers |
| 3. Routes development | Input validation, routing, persistence and coach access | `app/routes.py`, documented JSON APIs |
| 4. Frontend development | Separate responsive input, result, tip and admin pages | Jinja2 templates and CSS |
| 5. Deployment | Environment setup, startup, tests and hosting instructions | Render configuration and README |

## Dependencies
Model access and API key → real AI verification. Schema → save/history. Saved original plan → feedback update. Admin credentials → coach verification. Persistent hosting disk → durable remote history.

## Risks and mitigation
| Risk | Mitigation |
| --- | --- |
| API quota, timeout or unavailable model | Configurable model names, finite timeout, clear retry message |
| Provider failure during create/revise | Commit only after all required generation succeeds |
| Unauthorized profile access | Private token URLs and authenticated coach view |
| Lost hosted SQLite data | Persistent-disk setup instructions and backups |
| Inappropriate AI output | Safety prompt and visible guidance; human review remains necessary |

## Submission planning
Team name, member assignments, institution-specific dates, screenshots and recorded demonstration remain for the actual submitter to complete. No fabricated research, live results or completed milestones are claimed. Seven phase documents are editable Markdown equivalents; they are not edited copies of the shared Word templates.
