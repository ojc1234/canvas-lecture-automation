# Extracting lecture material (down_XXXX) text for study notes

The `down_XXXX` items are not file downloads — they are a slide viewer rendered as
HTML text at `https://common.jejunu.ac.kr/em/<content_id>`. You can pull the full
text (summaries + lecture scripts + key takeaways) to build quiz-study notes
WITHOUT any PDF tooling.

## 1. Find the content_id
From a material item page (`/modules/items/<id>`), the inner player iframe `src`
contains the id:
```bash
$B evaluate --session $S "(function(){var r=[];function w(win){try{win.document.querySelectorAll('iframe').forEach(function(f){r.push(f.src);w(f.contentWindow)})}catch(e){}}w(window);return r.join('\n')})()"
# => https://common.jejunu.ac.kr/em/6ac3b9146d4a0?TargetUrl=...content_type=pdf...
```

## 2. Navigate straight to the viewer and dump text
Navigating directly (with `?pr=1&mxpr=2.00&lg=ko`) renders the slides as text.
Scroll in steps so every slide's text is laid out, then read `innerText`:
```bash
for c in <id1> <id2> <id3>; do
  $B navigate "https://common.jejunu.ac.kr/em/$c?pr=1&mxpr=2.00&lg=ko" --session $S >/dev/null; sleep 8
  $B evaluate --session $S "(function(){return new Promise(function(res){var y=0;var iv=setInterval(function(){y+=1500;window.scrollTo(0,y);document.querySelectorAll('*').forEach(function(e){if(e.scrollHeight>e.clientHeight+50)e.scrollTop=y});if(y>60000){clearInterval(iv);res(document.body.innerText)}},150)})})()" > material_$c.txt
done
```
The viewer shows `page N / N` at the top; each slide block is
`SUMMARY` / `LECTURE SCRIPT` / `KEY TAKEAWAY`. The scroll-and-dump above usually
captures the later slides reliably; the very first slides sometimes need a
second pass (scroll back to top, re-dump) if they're missing.

## 3. Turn into study notes
Summarise `material_*.txt` into a `.md` cheat-sheet grouped by session, keeping
the KEY TAKEAWAY lines verbatim — those map almost 1:1 to quiz questions.

## Reading quiz questions (study only, never submit)
A quiz's questions and options ARE readable from the attempt page snapshot:
navigate to the quiz `/modules/items/<id>`, click `link "퀴즈 응시"`, then
`snapshot` — each option is a `radio "<text>"`. Use this ONLY to help the user
study or to show them the options. Do NOT click answers or submit; that is a
graded, attempt-limited assessment the user must complete themselves.
