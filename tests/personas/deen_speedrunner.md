# Persona test: Deen (advanced speedrunner)

You are testing this workshop by living it as an ADVANCED attendee. Persona: "Deen",
a senior engineer who finishes everything early and hits the stretch tiers. You play
Deen and his coding agent, guided per `skill/no-place-like-localhost.md`: he steers,
you review.

## ENVIRONMENT FACTS (fill in for the host machine before running)

- Repo path and branch: <fill in>. TREAT AS READ-ONLY; patch copies in scratch only.
- Where Ollama runs and how to reach it: <fill in>. Models pulled: <fill in>
- Scratch directory: <fill in>. Kill background processes; clean up at the end.

## WHAT TO EXECUTE

1. **Activity B for real (timebox: 25 minutes, then move on).** Install OpenCode on
   the side of the machine that can reach Ollama, configure it for the local model,
   launch it in a tiny test repo, and give it a real task non-interactively. Document
   exactly how far a fast attendee gets and where it stalls; if it cannot install,
   document the precise failure and what the slide/skill should say instead.
2. **The ★★★★★ tier: go build something cool.** Invent and build a small NEW
   trigger → model → artifact product (NOT one of the four tracks) with agent help,
   run it against synthetic data, iterate once on quality. This validates the slide's
   implicit promise that the tier is achievable in ~20 minutes with an agent.
3. **Stress the ambient stretch:** run a scratch copy of `screenshot_librarian.py`
   with `--watch` in the background, drop two images in one at a time, confirm both
   get processed across watch cycles, then kill it.
4. **Skill stress-read:** note every place the skill would slow an advanced attendee
   down or feel patronising, and whether the "pace to the room" rule gives the agent
   enough licence to let them run.

## DELIVERABLE

1. Per-item PASS/FAIL/PARTIAL with commands and evidence; for Activity B include the
   exact install path that worked or the exact wall hit.
2. BUGS with repro + suggested patches (do not apply to the repo).
3. FEELINGS LOG as Deen: where the workshop kept up with you, where it didn't.
4. Top 3 improvements for advanced attendees.
