# Quiz Automation Reference

## Quiz Flow

1. Navigate to quiz from "할 일" to-do list or module navigation
2. Click "퀴즈 응시" button (@e30 in quiz page)
3. For each question:
   - Find radio buttons in "답변 선택 그룹" legend
   - Click correct radio (refs like @e31, @e32, etc.)
4. Click "퀴즈 제출" button (@e48)
5. Verify score in "시도 이력" table (row shows "시도 1" | "1분 이내" | "3 / 3")
6. Click "다음 모듈 항목" to proceed

## Question Patterns Observed

### Multiple Choice (Radio Buttons)
- Each question has a "Legend "답변 선택 그룹"" with radio options
- Radio refs have `value` attributes (e.g., `="1204"`)
- Use `snapshot` to find current refs before clicking
- Correct answers are marked `[checked] ="on"` in result snapshot

### Answer Selection Strategy
- **Preferred**: Use domain knowledge to select correct answer
- **Fallback**: If unknown, select first option (or use educated guess)
- **Verification**: After submit, check "시도 이력" for score

## BrowserSkill Commands for Quiz

```bash
# Start quiz
./bsk/bsk.exe click --session <id> --ref e30  # 퀴즈 응시

# Wait for quiz to load
./bsk/bsk.exe wait-ms 5000

# Answer questions (refs change per page load - snapshot first)
./bsk/bsk.exe click --session <id> --ref e33  # Example answer
./bsk/bsk.exe click --session <id> --ref e39
./bsk/bsk.exe click --session <id> --ref e46

# Submit
./bsk/bsk.exe click --session <id> --ref e48  # 퀴즈 제출

# Wait for result
./bsk/bsk.exe wait-ms 3000

# Verify score
./bsk/bsk.exe snapshot --session <id>
# Look for: "시도 이력 1분 이내 3 / 3"

# Next module item
./bsk/bsk.exe click --session <id> --ref e47  # 다음 모듈 항목
```

## Pitfalls

- **Ref volatility**: Quiz element refs (eN) change on every page load — MUST `snapshot` immediately before each `click`
- **Score verification**: Always verify score in "시도 이력" table; if < max, consider re-taking (if allowed)
- **Session continuity**: Quiz submission navigates to result page; "다음 모듈 항목" button appears there
- **Time limits**: Some quizzes may have time limits; watch for "시간 제한" in quiz header
- **Storage state**: Quiz answers persist after submission; re-entering quiz shows previous attempt

## Quiz Types Encountered

| Week | Quiz | Questions | Notes |
|------|------|-----------|-------|
| 1주차 | 01_01 | 3 | OECD DeSeCo, 4th Industrial Revolution, WEF Future of Jobs |
| 1주차 | 01_02 | 3 | Human vs AI creativity, KIPO AI inventor, Hyper-connectivity |
| 1주차 | 01_03 | 3 | IP virtuous cycle, Patent definition, New IP rights |
| 2주차 | 02_01 | 3 | Invention examples, Invention features, Invention vs Discovery |
| 2주차 | 02_02 | 3 | Patent Act definition, Creativity requirement, Utility Model |
| 2주차 | 02_03 | 3 | Novelty objective criteria, Inventor definition, Patent vs Utility Model scope |
| 3주차 | 03_01 | 3 | First-to-File, Patent definition, Patent duration |
| 3주차 | 03_02 | 3 | Patent vs Utility Model, Design Right examples, Design focus |
| 3주차 | 03_03 | 3 | Novelty objective criteria, Inventor subjective requirements, Trademark duration |
| 4주차 | 04_01 | 3 | Cloud Bread case, Internet source usage, AI copyright challenge |
| 4주차 | 04_02 | 3 | Two Golden Rules (Originality+Expression), Unprotected works, Michael Kenna case |
| 4주차 | 04_03 | 3 | Copyright ownership, Moral rights, Fair use boundaries |

## Integration with Main Loop

In the main automation loop, after processing lecture items:
```python
if item_type == 'quiz':
    click_quiz_link()
    click_quiz_attempt()
    for question in questions:
        select_answer(question)
    click_submit()
    verify_score()
    click_next_module_item()
```