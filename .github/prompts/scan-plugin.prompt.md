---
description: Quick auto scan pada WordPress plugin menggunakan Semgrep dan pattern grep
mode: agent
agent: auto-scan
---

# Scan Plugin

Target: ${input:scanTarget:Plugin path (contoh: wp-content/plugins/contact-form-7)}

Jalankan automated security scan:
1. Semgrep dengan custom rules + p/php + p/security-audit
2. Pattern grep untuk dangerous sinks dan missing auth
3. Compile findings dalam structured JSON
4. Rangkum: total per severity, top risks, recommended deep-dive
