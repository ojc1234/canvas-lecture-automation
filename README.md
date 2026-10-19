# canvas-lecture-automation

A Hermes agent **skill** for watching and completing Jeju National University Canvas (LearningX) online lectures through [BrowserSkill (`bsk`)](https://github.com/Tencent/browser-use) driving the user's own logged-in Chrome.

> This is procedural memory for an AI agent, not a standalone CLI tool. It encodes a status-first, real-playback workflow with the pitfalls discovered while automating a live course.

## What it does

- **Status-first**: reads the real completion state from the Canvas LTI tool page and reports only what Canvas itself says (`완료` / `출석` / `12분 57초(100%)`) — never "N lectures processed" from a loop.
- **Real playback**: watches lectures at 1x (the player is a cross-origin iframe, so JS speed/mute hacks silently do nothing; the site treats >2x as cheating).
- **Handles the resume dialog**: clicks "이전에 시청했던 …부터 이어서 보시겠습니까? → 예".
- **Survives session drops**: keeps the `bsk` session alive, re-navigates and resumes on `session not registered`.
- **Opens materials** (`down_XXXX`) to mark them complete, and extracts slide text for study notes.

## Files

| Path | Purpose |
|------|---------|
| `SKILL.md` | Main skill: rules + procedure + pitfalls |
| `references/sso-login-flow.md` | Portal SSO login steps (vault-based, no plaintext passwords) |
| `references/iframe-button-clicking.md` | Finding week/lecture buttons in the tool iframe |
| `references/quiz-automation.md` | Quiz UI flow |
| `references/material-text-extraction.md` | Pull `down_XXXX` slide text for quiz-study notes |
| `scripts/canvas_lecture_auto_enhanced.py` | Skeleton cron script (predates the real-playback findings — fix before use) |

## Key lessons encoded

- Top-level `return` in `bsk evaluate` throws `SyntaxError: Illegal return statement` — always wrap in `(function(){ … return x })()`.
- The lecture list lives inside `iframe[title="도구 내용"]` on `/external_tools/80`, not `/modules`.
- Snapshot refs (`@eN`) change after every navigation and after the resume dialog — snapshot right before each click.
- Keep each `bsk` call under ~5 min and ping the session every few minutes or it drops.

## License

MIT
