---
name: canvas-lecture-automation
description: "Use when watching/downloading Jeju Canvas lectures via bsk. Real playback, verify 100%."
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

Drives the user's logged-in Chrome with `bsk` (path `/c/Users/ojc12/bsk/bsk.exe` from git-bash). Load `browserskill-user-chrome` too for generic bsk usage.

The user's private repo `ojc1234/canvas-lecture-automation` is a published copy of this skill. When the user points at it, just follow this skill; there's no need to clone it. If you do clone it, use `gh repo clone`.

## Always-on rules

- **Report only what Canvas itself says.** "Processed N lectures" from a script loop is NOT completion. Before telling the user anything is done, re-read the status (step 1) and quote it per item (`완료`/`출석`/`12분 57초(100%)`). Scan script logs for `false`, empty values, and `invalid` before summarising; if a summary was wrong, correct it up front in the next reply.
- **Never blind-answer graded quizzes** (e.g. always picking option 1). It costs points and uses up attempts. By default (cron) list the remaining quizzes with deadlines. When the user explicitly asks you to do the quizzes ("퀴즈도"), take them yourself: pull that week's material PDFs first (see `references/material-text-extraction.md`, section 0), answer from the material, check that all 3 radios show `[checked]` before submitting, and confirm `3 / 3` in 시도 이력.
- **Only process what is open and incomplete.** Weeks marked `예정` aren't open yet; `마감됨` + `완료` items are already done. Don't loop over all 16 weeks re-watching.
- Reply in Korean, short status table: done / remaining / deadline.
- **Act, don't offer.** When the user asks for this (or "automate everything"), do every safe step yourself — status read, materials, playback, cron setup/repair — and report the result. Don't end with "원하시면 제가 …할게요" for things you could just do; the user pushes back on that. The only hand-back is graded quizzes.

## Procedure

### 1. Read real status (do this first and last)
`/courses/43379/modules` redirects to the course home; the list lives in the LTI tool page `https://canvas.jejunu.ac.kr/courses/43379/external_tools/80`, inside `iframe[title="도구 내용"]` (same-origin, readable).
```bash
B=/c/Users/ojc12/bsk/bsk.exe; S=$($B session start --quiet | tr -d '\r\n')
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
List them (`07_01 퀴즈 … 3 문제 3 점, D-1`) for the user. See `references/quiz-automation.md` for the UI flow, used only when the user supplies the answers.

### 5. Re-run step 1 and report.

## Pitfalls

- **bsk >= 0.4.1 (cooperate mode):** every `evaluate`/`click`/`navigate` on the shared tab fails with `shared page control or observation changed` unless it carries a fresh sync. Run `J=$($B cooperate sync --session $S --json)`, take `context_id` and `observation_id`, and pass `--context $C --observation $O`. Re-sync after every navigation/DOM change. The sync JSON already contains a full snapshot (week counters `x/9`, item `완료`/`예정`), so it doubles as the step-1 status read.
- **Keep each bsk call under ~5 min, and keep the session alive with a cheap call (snapshot/screenshot) at least every few minutes.** Long `sleep`s let the session drop (`session not registered or already stopped`), and a terminal call that times out leaves no session. On drop: `session start` again, re-navigate, resume (dialog → 예). Hermes terminal foreground caps around 400 s, so chain waits as `sleep 280; snapshot` calls.
- Re-navigating away mid-play triggers a `beforeunload` that bsk auto-accepts. Progress up to that point is kept.
- Top-level `return` in `bsk evaluate` → `SyntaxError: Illegal return statement`. Always wrap: `(function(){ ... return x; })()`.
- `bsk wait-ms <ms>` takes no `--session` flag. Max is 300000.
- Shell-quoting JS inside bash: keep the outer double quotes and use `\"` for attribute selectors (`iframe[title=\"도구 내용\"]`).
- Week buttons contain icon glyphs. Match with a regex like `/^\D*7주차/` so `7` doesn't hit `17주차`.
- Refs (`@eN`) change after every navigation and after the dialog closes. Snapshot right before each click.
- Login: SSO via the 제주대 portal. See `references/sso-login-flow.md`. Never type the password yourself; use the browser vault.
- Python `subprocess` → bsk: pass `encoding='utf-8', errors='replace'`.

## Cron (daily)
Weeks open on irregular weekdays (Tue/Wed/Thu…), so schedule **`every day at 9am`**, not weekly — a Monday-only job misses most of each week's window.
- `cronjob_manage list` first and **update/resume the existing job** (named `canvas_auto_attendance_daily`) instead of creating a duplicate.
- Job config: `skills: [canvas-lecture-automation, browserskill-user-chrome]`, `enabled_toolsets: [terminal, file]`, `deliver: origin`. Prompt (Korean, self-contained): steps 1–5 above, "only open + incomplete items", 1x real playback via snapshot refs, quizzes solved from the week's material PDF (submit only when every answer is grounded, verify `3 / 3`, never re-take), on login page report "재로그인 필요" without typing a password, and a one-line "처리할 항목 없음" when idle. The user opted into cron quiz-solving; before that, cron only listed quizzes.
- Requires the PC on, Chrome logged in, BrowserSkill connected at fire time — say so in the report to the user.
- `scripts/canvas_lecture_auto_enhanced.py` predates these findings (it relies on JS video control). Don't use it as the cron payload; the skill-driven agent prompt is the working path.

## References
- `references/sso-login-flow.md` — portal SSO steps
- `references/iframe-button-clicking.md` — finding week/lecture buttons in the tool iframe
- `references/quiz-automation.md` — quiz UI flow (only with user-provided answers)
- `references/material-text-extraction.md` — pull down_XXXX slide text for quiz-study notes
- `references/video-download-transcribe.md` — download lecture mp4 + Whisper GPU transcript + notes
- `references/video-download-transcript.md` — resolve a lecture's MP4 (content.php → CDN), download, Whisper transcript, per-차시 summary
