# Jeju Canvas SSO Login Flow

## Overview
Canvas at Jeju National University uses a multi-step SSO redirect chain:
```
canvas.jejunu.ac.kr → jnuclass.jejunu.ac.kr (SSO) → portal.jejunu.ac.kr/login.htm (credentials) → jnuclass.jejunu.ac.kr (main) → canvas.jejunu.ac.kr (course)
```

## Procedure

1. **Navigate to Canvas course URL**
   ```bash
   bsk navigate --session <id> "https://canvas.jejunu.ac.kr/courses/43379/modules"
   ```
   This redirects through the SSO chain automatically.

2. **Check for login page** (after redirect)
   ```bash
   bsk snapshot --session <id>
   ```
   Look for "로그인 - 제주대학교 포털" or "통합 로그인" in the snapshot.

3. **Fill credentials on portal login page**
   ```bash
   # Username field (ref changes per load - always snapshot first)
   bsk fill --session <id> --ref e1 --value "STUDENT_ID_HERE"
   # Password field
   bsk fill --session <id> --ref e2 --value "PASSWORD_HERE"
   # Login button
   bsk click --session <id> --ref e3
   ```

4. **Wait for redirect and verify**
   ```bash
   bsk wait-ms 10000
   bsk snapshot --session <id>
   ```
   Verify we're on JNUclass main page (not login page).

5. **Navigate to course**
   ```bash
   bsk navigate --session <id> "https://canvas.jejunu.ac.kr/courses/43379/modules"
   bsk wait-ms 5000
   bsk snapshot --session <id>
   ```
   Verify "나의 강의" or course dashboard appears.

## Pitfalls

- **Credential mismatch**: If login fails, snapshot shows "사용자 인증에 실패하였습니다. (invalid input)" with a "뒤로 돌아가기" button (ref e1)
- **Session cookie persistence**: BrowserSkill uses the connected Chrome profile; if Chrome is already logged in, steps 2-4 may be skipped
- **Redirect timing**: Sometimes need longer wait (15s) after login click before snapshot
- **Origin mismatch for vault**: Browser vault only fills on exact origin match; portal.jejunu.ac.kr must match exactly

## Browser Vault Integration

```bash
# Check for saved credentials
browser_vault_list
# Fill on portal login page (must be on portal.jejunu.ac.kr origin)
browser_vault_fill --handle vault_XXXXXX
```

Never type passwords in chat or scripts.