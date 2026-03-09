source code
   ↓
ripgrep scan
   ↓
AI audit (JSON prompt)
   ↓
candidate vulnerabilities
   ↓
manual code review
   ↓
Burp Suite testing

Chain 1
AJAX endpoint
↓
file upload
↓
include
↓
RCE

Chain 1
AJAX endpoint
↓
file upload
↓
include
↓
RCE

Chain 2
unserialize
↓
magic method
↓
system()
↓
RCE

kamu hanya finding candidates, bukan langsung di anggap bug
