# 1. Ideation Phase

## Problem statement
People pursuing weight loss, muscle gain or general wellness often lack an actionable weekly routine matched to their experience, time and available equipment. Generic plans are difficult to adapt when preferences change. Coaches need a way to review a user's original plan and subsequent revisions.

## Brainstorming and prioritization
| Idea | Value | Priority |
| --- | --- | --- |
| Personalized seven-day schedule | Gives users a concrete starting point | Must have |
| Feedback-based revisions | Adapts the plan without losing its history | Must have |
| Goal-based nutrition/recovery tip | Complements training | Must have |
| Coach review dashboard | Supports oversight across users | Must have |
| Wearable integration and progress charts | Requires external data not in the reference | Future scope |

Selected solution: FitBuddy, a FastAPI web application using Google Gemini and SQLite. Four core scenarios match the project guide: generate a plan, revise it from feedback, request a tip and review all users as a coach.

## Empathy map
This is a design hypothesis, not a claim of conducted user research.

| Dimension | Beginner fitness user |
| --- | --- |
| Says | “I need a routine I can follow at home.” |
| Thinks | “Will this fit my goal and available time?” |
| Does | Selects a goal and equipment; tries the weekly plan; requests changes |
| Feels | Uncertain about where to start; motivated by clear daily actions |
| Pain | Generic advice, unrealistic intensity, no easy way to adapt |
| Gain | A structured week, recovery guidance and saved revisions |

Coach empathy: needs clear profile information and original/revised plans in one protected view. This version records feedback and plan history; it does not measure completed workouts or physical progress.
