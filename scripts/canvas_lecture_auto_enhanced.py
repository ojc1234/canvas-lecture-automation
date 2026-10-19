#!/usr/bin/env python3
import os
import subprocess
import time
import json

BSK = os.environ.get("BSK_PATH", os.path.expanduser("~/bsk/bsk.exe"))

def bsk(cmd, session=None):
    if session:
        full = f"{BSK} {cmd} --session {session}"
    else:
        full = f"{BSK} {cmd}"
    try:
        result = subprocess.run(full, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"Exception running {full}: {e}")
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()

def main():
    print("Starting bsk session...")
    out = bsk("session start --quiet")
    if out is None:
        print("Failed to start session")
        return
    session_id = out.strip()
    print(f"Session ID: {session_id}")
    # Navigate to external tools page
    print("Navigating to external tools page...")
    nav = bsk(f"navigate --session {session_id} 'https://canvas.jejunu.ac.kr/courses/43379/external_tools/80'", session_id)
    if nav is None:
        print("Navigation failed")
        return
    time.sleep(3)
    # Process weeks 1 to 16
    for week in range(1, 17):
        print(f"\n=== Processing week {week} ===")
        # Expand week button
        js_expand = f"""
        var btns = Array.from(document.querySelectorAll('button'));
        var target = null;
        for (var i=0; i<btns.length; i++) {
            var txt = btns[i].textContent.trim();
            if (txt === ' {week}주차' || txt === ' {week}주차') {
                target = btns[i];
                break;
            }}
        if (target) {
            target.click();
            return true;
        } else {
            return false;
        }
        """
        js_expand_escaped = js_expand.replace("'", "\'")
        res = bsk(f"evaluate --session {session_id} '{js_expand_escaped}'", session_id)
        print(f"  Expand click result: {res}")
        time.sleep(2)
        # Get lecture links for this week
        js_lectures = f"""
        var links = Array.from(document.querySelectorAll('a'));
        var weekNum = {week};
        var lectureLinks = [];
        for (var i=0; i<links.length; i++) {
            var txt = links[i].textContent.trim();
            if (txt.includes('(' + String(weekNum).padStart(2, '0') + '_')) {
                lectureLinks.push({href: links[i].href, text: txt});
            }}
        return lectureLinks;
        """
        js_lectures_escaped = js_lectures.replace("'", "\'")
        lectures_json = bsk(f"evaluate --session {session_id} '{js_lectures_escaped}'", session_id)
        print(f"  Lectures raw: {lectures_json}")
        try:
            lectures = json.loads(lectures_json) if lectures_json else []
        except Exception as e:
            print(f"  Failed to parse lectures: {e}")
            lectures = []
        for lec in lectures:
            href = lec['href']
            text = lec['text']
            print(f"    Opening lecture: {text}")
            nav2 = bsk(f"navigate --session {session_id} '{href}'", session_id)
            if nav2 is None:
                print(f"      Navigation failed for {href}")
                continue
            time.sleep(3)
            # Set video playback rate and mute
            js_video = """
            var videos = document.querySelectorAll('video');
            if (videos.length > 0) {
                videos.forEach(function(v) {
                    v.playbackRate = 2.0;
                    v.muted = true;
                });
                return true;
            }
            return false;
            """
        js_video_escaped = js_video.replace("'", "\'")
        video_set = bsk(f"evaluate --session {session_id} '{js_video_escaped}'", session_id)
        print(f"      Video speed set: {video_set}")
        # Get video duration
        js_duration = """
        var v = document.querySelector('video');
        if (v) {
            return v.duration;
        }
        return 0;
        """
        js_duration_escaped = js_duration.replace("'", "\'")
        dur_str = bsk(f"evaluate --session {session_id} '{js_duration_escaped}'", session_id)
        try:
            duration = float(dur_str) if dur_str else 0
        except:
            duration = 0
        wait_time = max(duration / 2.0 + 5, 10)  # half speed plus buffer
        print(f"      Video duration: {duration}s, waiting {wait_time:.1f}s")
        time.sleep(wait_time)
        # Check attendance
        js_attendance = """
        var texts = Array.from(document.querySelectorAll('*')).map(el => el.textContent);
        var found = texts.some(function(t) {
            return t.includes('출석 인정') || t.includes('출석완료') || t.includes('출석 처리') || t.includes('출석 확인') || t.includes('✅');
        });
        return found;
        """
        js_attendance_escaped = js_attendance.replace("'", "\'")
        attended = bsk(f"evaluate --session {session_id} '{js_attendance_escaped}'", session_id)
        print(f"      Attendance found: {attended}")
        # Click next module item
        js_next = """
        var btns = Array.from(document.querySelectorAll('button'));
        var next = btns.find(b => b.textContent.includes('다음 모듈 항목'));
        if (next) { next.click(); return true; }
        return false;
        """
        js_next_escaped = js_next.replace("'", "\'")
        next_clicked = bsk(f"evaluate --session {session_id} '{js_next_escaped}'", session_id)
        print(f"      Next item clicked: {next_clicked}")
        time.sleep(2)
        print(f"  Finished week {week}")
    # Stop session
    print("Stopping session...")
    bsk(f"session stop {session_id}")
    print("Done.")

if __name__ == "__main__":
    main()
