# Lecture video download + transcript (any Jeju Canvas course)

Use when the user wants a lecture's MP4 saved and/or its script (대본) organised. Works for any course id, not just 43379.

## 1. Find the content_id (user's Chrome via bsk)
Navigate to `/courses/<cid>/modules/items/<item>`, then read the player iframe nested inside `iframe[title="도구 내용"]`:
```bash
$B evaluate --session $S "(function(){var o=[document.title];document.querySelectorAll('iframe').forEach(function(f){try{f.contentDocument.querySelectorAll('iframe').forEach(function(g){o.push(g.src)})}catch(e){}});return o.join('\n')})()"
```
The src is `https://common.jejunu.ac.kr/em/<content_id>?startat=..&endat=<seconds>...`. `endat` = duration. `document.title` = lecture title (use for filenames/summary headers).

## 2. Resolve the real MP4
Navigate the bsk tab to `https://common.jejunu.ac.kr/em/<content_id>` (same-origin), then sync-XHR
`/viewer/ssplayer/uniplayer_support/content.php?content_id=<id>` → XML with `<media_uri>`:
`https://jeju-cms-object.cdn.gov-ntruss.com/contents4/<owner>/<id>/contents/media_files/mobile/ssmovie.mp4` (also gives title, author, duration).
The `<video>` elements on the em page only show `preloader.mp4` — don't trust them.

## 3. Download
The CDN URL needs no cookies: `curl -s -o NN_lecture.mp4 -H "Referer: https://common.jejunu.ac.kr/" <media_uri>` (~7 MB/min of video). Save to `E:\lectures\<cid>\` (C: is low on space; ASCII filenames). Run downloads sequentially — Hermes terminal rejects `&` backgrounding in foreground calls.

## 4. Transcript
- Check `contents/media_script_list.xml` first; it usually 404s (no captions), so plan on Whisper.
- faster-whisper lives in the Hermes venv: `C:/Users/ojc12/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe` (bare `python`/`python3` lack it).
- Extract 16 kHz mono wav with the Hermes ffmpeg (`.../hermes/tools/ffmpeg-*/bin/ffmpeg.exe`), then `WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())`, `language="ko"`, `vad_filter=True`, and an `initial_prompt` with the course's domain terms (improves legal/technical vocabulary).
- If you try CUDA, the error only appears at the first encode (inside the segment loop), not at model load — so a try/except around `WhisperModel(...)` does NOT catch a missing cuBLAS; probe with a short transcribe before committing to GPU.
- Write `[HH:MM:SS] text` lines and flush per segment so progress can be checked with `tail`.
- CPU medium runs ≈ 1× real time. Launch with `terminal(background=true, notify=true)`, report ETA, and end the turn instead of polling.

## 5. Deliver
Summarise per 차시 in Korean: 사례 사실관계 → 쟁점 → 법리/판례 → 결론 (adapt headings for non-law courses). Keep the full transcript as a file; don't paste it into chat.
