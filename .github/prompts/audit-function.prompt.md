---
description: Deep manual audit pada function atau endpoint WordPress
mode: agent
agent: manual-audit
---

# Audit Function / Endpoint

Target: ${input:auditTarget:Function name, file path, atau endpoint (contoh: wp_ajax_upload_handler)}

Lakukan deep manual audit:
1. Baca semua kode yang relevan secara mendalam
2. Trace complete data flow dari source ke sink
3. Identifikasi semua security checks (present dan missing)
4. Cek capability verification, nonce validation, input sanitization
5. Construct exploit scenario dan PoC steps
6. Assess severity dan exploitability
7. Berikan rekomendasi fix
