# Iframe Button Clicking Technique

## Purpose
Click buttons inside iframes when direct DOM access is blocked by cross-origin restrictions.

## When to Use
- Need to interact with elements inside iframes (especially cross-origin iframes)
- Direct CSS/XPath selectors fail due to iframe boundaries
- BrowserSkill snapshot shows iframe elements but click coordinates are unreliable

## Procedure

1. **Extract identifier** from the target (e.g., lecture number '01' from item '01_01')
2. **Create JavaScript search function**:
   ```javascript
   (function() {
       const targetText = 'LECTURE_NUMBER_OR_TEXT';
       const frames = document.querySelectorAll('iframe');
       for (let i = 0; i < frames.length; i++) {
           try {
               const doc = frames[i].contentDocument || frames[i].contentWindow.document;
               if (!doc) continue;
               const buttons = doc.querySelectorAll('button, [role="button"]');
               for (let btn of buttons) {
                   if (btn.textContent.trim() === targetText) {
                       btn.click();
                       return 'found and clicked in iframe ' + i;
                   }
               }
           } catch (e) {
               // Ignore cross-origin access errors
               continue;
           }
       }
       // Fallback to main document
       const mainButtons = document.querySelectorAll('button, [role="button"]');
       for (let btn of mainButtons) {
           if (btn.textContent.trim() === targetText) {
               btn.click();
               return 'found and clicked in main document';
           }
       }
       return 'not found: ' + targetText;
   })()
   ```
3. **Execute via BrowserSkill**: `bsk evaluate --session <id> '<JS_CODE>'` (note: use `evaluate`, not `js` which doesn't exist)
4. **Check result**: Look for 'found and clicked' in the output
5. **Wait for content to load**: Typically 2000-3000ms after click

## Why This Works
- JavaScript execution context can access iframe content documents (when same-origin or when allowed)
- Text matching is more reliable than positional selectors that may change
- Fallback to main document handles cases where iframe isn't actually used
- Avoids coordinate-based clicking which is fragile with responsive layouts

## Pitfalls

- **Cross-origin restrictions**: Some iframes block contentDocument access entirely; in those cases, you must interact with the iframe as a whole (e.g., click the iframe element itself)
- **Dynamic content**: Iframe content may load asynchronously; wait for iframe to be present before executing search
- **Multiple matches**: If multiple buttons have same text, only the first will be clicked; consider adding additional context (parent element checks)
- **Performance**: Searching all iframes can be slow on pages with many iframes; limit to relevant iframes when possible

## Example: Canvas Lecture Button Clicking

For Canvas lecture items named like '01_01', '01_02':
- Extract '01' as the lecture number
- Search for button with text exactly '01'
- Clicking this button navigates to the lecture video player
- After click, video element can be controlled via JavaScript in the same context

## Related Techniques

- **Coordinate clicking as fallback**: When JavaScript search fails, use snapshot to find element and click via ref
- **Element dispatch events**: Instead of btn.click(), sometimes dispatching a MouseEvent works better
- **URL navigation**: Some iframe buttons actually change the page URL; after click, check for URL change to confirm success
