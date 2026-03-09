---
description: Trace data flow dari source ke sink
mode: agent
agent: manual-audit
---

# Trace Data Flow

Target: ${input:traceTarget:Describe the source and sink to trace (contoh: $_POST['file'] ke include())}

Trace complete data flow:
1. Identifikasi source (user input entry point)
2. Follow setiap function call, assignment, transformation
3. Dokumentasikan setiap sanitization/validation yang diterapkan
4. Identifikasi apakah data sampai ke dangerous sink
5. Assess apakah sanitization bisa di-bypass
6. Output: step-by-step trace dengan file:line references
