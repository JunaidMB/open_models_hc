# Persona run: Sara (beginner) — 2026-07-02, pre-session overnight

Machine: Windows 11 + PowerShell (per the skill's routing), RTX 4080 16GB, qwen3:4b
and qwen2.5vl:3b. All bugs below were fixed on this branch the same night.

## Results

| Stage | Verdict | Notes |
|---|---|---|
| Steps 0-1 (detection, model choice) | PASS with friction | `ver` fails in PowerShell (fixed in skill); RAM-row vs VRAM-row confusion (skill now says VRAM wins); llmfit had no Windows install path (fixed) |
| Step 2 / Activity A | PASS after the night's worst bug | the skill's curl command fails in PowerShell (`curl` aliases Invoke-WebRequest) at the skill's self-declared key moment. Fixed: PowerShell variants added. Structured output exercise worked; schema call returned exact clean JSON |
| Activity C (ASR, whisper-tiny) | PASS | CPU transcription faster than the 4B chat model's cold start; a wall of transformers warnings looked like breakage (media_indexer now suppresses them) |
| Activity E (★ screenshot_librarian) | PARTIAL stock, PASS patched | see BUG 2 |

## Bugs found (all fixed on this branch)

1. **Skill's key-moment curl fails in PowerShell.** The skill routes Windows
   attendees to PowerShell, then hands them a bash-only command at its most
   important gate. Fixed: `curl.exe` and `Invoke-RestMethod` variants in the skill.
2. **screenshot_librarian silently filed unretryable duds.** Small VLMs often ignore
   the two-line NAME:/TAGS: text format; the regex missed, the file became
   `<date>--unnamed.png` with empty tags, exit 0, and the rename meant re-runs never
   retried it. Fixed: Ollama structured outputs (JSON schema) plus raise-on-empty so
   failures skip without renaming. The fix is Activity A's schema lesson applied to
   Activity E, which is now called out in a code comment.
3. **`ver` as the Windows OS check** fails in PowerShell (cmd builtin). Fixed.
4. **Python 3.14 pin surprises attendees** (`uv` refuses without it). Troubleshooting
   line added to the skill; relaxing the pin left as a repo-owner decision.

Also preempted in the skill now: qwen3's visible thinking on first reply (looks
broken to a beginner; it's a feature) and Windows console mojibake (`chcp 65001`).

## Feelings highlights (verbatim from the run)

- "minute ~10: mild panic then genuine laughter: my first ever local AI spent a full
  minute visibly agonizing over whether 'Hi, Sara!' is one sentence."
- "minute ~14: the low point. I pasted the workshop's own curl command and got red
  PowerShell vomit at THE moment the skill calls the thesis of the night."
- "minute ~18: the magic moment. The response JSON had choices[0].message.content,
  the exact shape I destructure at work. My laptop is impersonating OpenAI. I said
  'oh!' out loud."
- "minute ~40: fixing the librarian myself with the schema trick was the proudest I
  felt all night. Honestly a better lesson than if it had worked."
- "minute ~50: first workshop where the take-home isn't a certificate, it's a butler."
