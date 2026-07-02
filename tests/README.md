# Workshop tests

Two layers of testing for this repo, both runnable by anyone.

## 1. Mechanical smoke test (30 seconds, no models)

```bash
uv run --no-project --with ollama python tests/smoke.py
# no Python 3.14 installed? add: --python 3.12
```

Compiles every track, validates the podcast feed generator produces absolute
enclosure URLs (RSS apps require them), and checks LAN IP detection. Needs the
`ollama` package for imports only; nothing contacts a server.

## 2. Persona tests (agentic, ~30-60 min each)

The real test of a workshop is whether a specific kind of attendee gets through it.
`personas/` contains three attendee personas written as prompts for a coding agent
(Claude Code, OpenCode, etc.). Each instructs the agent to role-play the attendee AND
their helper agent, actually execute the activities on the host machine, and report
bugs plus a first-person friction/feelings log.

To run one: open a coding agent on a machine with Ollama, paste the persona file as
the task, and fill in the ENVIRONMENT FACTS section for that machine. Treat the repo
as read-only; fixes get reported, then applied by a human (or the orchestrating agent).

| Persona | Covers | Focus |
|---|---|---|
| `personas/sara_beginner.md` | Skill Steps 0-2, Activities A, C, E(★) | wording clarity, confidence, first-time friction |
| `personas/maya_builder.md` | Activity E ★★★ audio pipelines end to end | product payoff actually works |
| `personas/deen_speedrunner.md` | Activity B, ★★★★★ tier, --watch ambient mode | stretch tiers keep fast attendees busy |

Completed runs are written up in `persona_reports/` with date and machine. Reports
feed fixes; the feelings logs feed the slides and the skill.
