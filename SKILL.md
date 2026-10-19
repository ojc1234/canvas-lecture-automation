---
name: canvas-lecture-automation
description: "Use when watching/completing Jeju Canvas (LearningX) lectures via bsk. Status-first, real playback, verify 100%."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [canvas, lms, browser-automation, browserskill, cron, lecture-watching]
    related_skills: [browserskill-user-chrome, computer-use]
---

# Canvas (Jeju LearningX) Lecture Completion via BrowserSkill

Drives the user's logged-in Chrome with `bsk` (path `$HOME/bsk/bsk.exe` from git-bash). Load `browserskill-user-chrome` too for generic bsk usage.

## Always-on rules

- **Report only what Canvas itself says.** "Processed N lectures" from a script loop is NOT completion. Before telling the user anything is done, re-read the status (step 1) and quote it per item (`완료`/`출석`/`12분 57초(100%)`). Scan script logs for `false`, empty values, and `invalid` before summarising; if a summary was wrong, correct it up front in the next reply.
- **Only process what is open and incomplete.** Weeks marked `예정` aren't open yet; `마감됨` + `완료` items are already done. Don't loop over all 16 weeks re-watching.
- Reply in Korean, short status table: done / remaining / deadline.

## Procedure

### 1. Read real status (do this first and last)
`/courses/43379/modules` redirects to the course home; the list lives in the LTI tool page `https://canvas.jejunu.ac.kr/courses/43379/external_tools/80`, inside `iframe[title="도구 내용"]` (same-origin, readable).
```bash
B=$HOME/bsk/bsk.exe; S=$($B session start --quiet | tr -d '\r\n')
$B navigate "https://canvas.jejunu.ac.kr/courses/43379/external_tools/80" --session $S >/dev/null; sleep 4
# expand every week, then dump text
$B evaluate --session $S "(function(){var d=document.querySelector('iframe[title=\"도구 내용\"]').contentDocument;Array.from(d.querySelectorAll('button')).forEach(function(b){if(/주차/.test(b.textContent)&&b.getAttribute('aria-expanded')!=='true')b.click();});return 1})()"; sleep 4
$B evaluate --session $S "(function(){return document.querySelector('iframe[title=\"도구 내용\"]').contentDocument.body.innerText})()" > status.txt
```
Each week shows `x/9`. Each item ends with `완료` or `-`, plus `D-n`/`마감됨`/`예정`. Item hrefs are `a` tags in the same iframe (`/modules/items/<id>`).

### 2. Materials (`down_XXXX`)
Just `navigate` to each `/modules/items/<id>` and wait ~4 s. Opening the item marks it `완료`.

### 3. Lectures: real playback at 1x
The player is a cross-origin iframe (`common.jejunu.ac.kr`). JS `video.playbackRate`/`muted` cannot reach it, so a script that "sets 2x" silently does nothing. Watch at real time. The site states that only up to 2x counts and anything faster is treated as cheating.
1. `navigate` to the lecture item and wait ~6 s.
2. Scroll the inner frames so the player is visible: `evaluate "(function(){document.querySelectorAll('iframe').forEach(function(f){try{f.contentWindow.scrollBy(0,400)}catch(e){}});return 1})()"`.
3. `snapshot`, find `button "재생"`, `click @eN`. The snapshot DOES expose refs inside the cross-origin player. Use refs, not `--image-x/y` (those are only for Canvas-region captures).
4. If there is earlier progress, a **"이전에 시청했던 MM:SS부터 이어서 보시겠습니까?" dialog blocks playback**. Snapshot again, click `button "예"`. Take a screenshot to confirm the video frame is advancing.
5. Wait out the remaining time (`재생 시간` minus recorded progress).
6. Click `학습 상태 확인`, then snapshot. Success = `12분 57초(100%)` + `완료` + `출석`. Progress is saved incrementally, so a resume only needs the remainder.

The player has its own `음소거` and `x 1.0` speed buttons (visible in the snapshot while playing). Use those refs for mute/speed, not JS.

### 4. Quizzes
See `references/quiz-automation.md` for the quiz UI flow.

### 5. Re-run step 1 and report.

## Pitfalls

- **Keep each bsk call under ~5 min, and keep the session alive with a cheap call (snapshot/screenshot) at least every few minutes.** Long `sleep`s let the session drop (`session not registered or already stopped`), and a terminal call that times out leaves no session. On drop: `session start` again, re-navigate, resume (dialog → 예). Hermes terminal foreground caps around 400 s, so chain waits as `sleep 280; snapshot` calls.
- Re-navigating away mid-play triggers a `beforeunload` that bsk auto-accepts. Progress up to that point is kept.
- Top-level `return` in `bsk evaluate` → `SyntaxError: Illegal return statement`. Always wrap: `(function(){ ... return x; })()`.
- `bsk wait-ms <ms>` takes no `--session` flag. Max is 300000.
- Shell-quoting JS inside bash: keep the outer double quotes and use `\"` for attribute selectors (`iframe[title=\"도구 내용\"]`).
- Week buttons contain icon glyphs. Match with a regex like `/^\D*7주차/` so `7` doesn't hit `17주차`.
- Refs (`@eN`) change after every navigation and after the dialog closes. Snapshot right before each click.
- Login: SSO via the 제주대 portal. See `references/sso-login-flow.md`. Never type the password yourself; use the browser vault.
- Python `subprocess` → bsk: pass `encoding='utf-8', errors='replace'`.

## Cron (weekly)
A Hermes cronjob can run the status check + materials + lecture playback each Monday 9 AM. It must report from Canvas status. `scripts/canvas_lecture_auto_enhanced.py` predates these findings (it relies on JS video control). Treat it as a skeleton and fix it before relying on it.

## References
- `references/sso-login-flow.md` — portal SSO steps
- `references/iframe-button-clicking.md` — finding week/lecture buttons in the tool iframe
- `references/quiz-automation.md` — quiz UI flow
- `references/material-text-extraction.md` — pull down_XXXX slide text for quiz-study notes
