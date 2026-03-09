# WordPress Security Research — Workspace Guidelines

## Context
White-box pentesting workspace for WordPress core + plugins. We have full source code access.

## Tools Available
- **Semgrep** (v1.154.0): Primary PHP SAST scanner — `.venv\Scripts\semgrep.exe`
- **CodeQL** (v2.24.3): JS/Python deep analysis — `C:\codeql\codeql.exe` (no native PHP)
- **MCP Server** `semgrep-scan`: 6 tools — `semgrep_scan`, `semgrep_scan_rule`, `codeql_create_database`, `codeql_analyze`, `grep_vulnerability_pattern`, `list_wp_plugins`
- **Custom Semgrep Rules**: `.semgrep/rules/wordpress-security.yaml`
- **ripgrep**: Fast text search

## Core Principles

### Findings = Candidates, Not Confirmed Bugs
Every finding from automated tools or AI analysis is a **candidate** until manually verified. Never claim a vulnerability is confirmed without tracing the full data flow and testing it.

### Two Operating Modes
1. **Auto Mode** (`@auto-scan`): Automated broad scanning — Semgrep, CodeQL, pattern grep. Produces candidate lists in structured JSON.
2. **Manual Mode** (`@manual-audit`): Deep human-guided analysis — read specific code, trace data flows, analyze logic, construct exploit chains.
3. **Hybrid**: Use `/pentest` prompt to orchestrate both. Auto finds surface area, manual goes deep.

### Vulnerability Priority (High → Low)
1. Remote Code Execution (RCE)
2. PHP Object Injection / Deserialization
3. Arbitrary File Upload → RCE
4. Privilege Escalation (Subscriber → Admin)
5. SQL Injection
6. Local File Inclusion / Path Traversal
7. SSRF
8. Stored XSS
9. CSRF with impact

### WordPress-Specific Knowledge
- Entry points: `wp_ajax_*`, `wp_ajax_nopriv_*`, `register_rest_route`, `admin_post_*`, `admin_init`
- Auth checks: `current_user_can()`, `wp_verify_nonce()`, `check_ajax_referer()`
- Dangerous sinks: `eval`, `system`, `exec`, `shell_exec`, `passthru`, `popen`, `proc_open`, `include`, `require`, `unserialize`, `maybe_unserialize`, `move_uploaded_file`, `file_put_contents`
- Sources: `$_GET`, `$_POST`, `$_REQUEST`, `$_COOKIE`, `$_FILES`, REST params, AJAX params

## Output Language
Respond in **Bahasa Indonesia** unless the user writes in English.

## Output Format
Use structured JSON for findings (see `.github/prompts/` for templates). Always include: file, line, source, sink, data_flow, severity, and recommended_manual_test.
