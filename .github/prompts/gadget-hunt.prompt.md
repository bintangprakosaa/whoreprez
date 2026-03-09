---
description: Hunt PHP Object Injection dan POP gadget chains
mode: agent
agent: auto-scan
---

# Gadget Chain Hunt

Target: ${input:gadgetTarget:Plugin atau directory path (contoh: wp-content/plugins/target-plugin)}

Cari PHP Object Injection vulnerabilities dan POP gadget chains:
1. Scan untuk `unserialize()` dan `maybe_unserialize()` pada user input
2. Enumerate semua class dengan magic methods: `__destruct`, `__wakeup`, `__toString`, `__call`, `__invoke`
3. Trace property access di dalam magic methods
4. Identifikasi apakah attacker-controlled properties bisa reach dangerous sinks
5. Construct possible POP gadget chains
6. Output structured report dengan chain paths
