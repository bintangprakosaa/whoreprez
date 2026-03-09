# WordPress Security Research Lab

White-box pentesting lab untuk riset keamanan WordPress plugins. Menggabungkan automated SAST scanning (Semgrep, CodeQL) dengan AI-assisted manual audit menggunakan VS Code Copilot agents.

> **DISCLAIMER**: Repository ini hanya untuk tujuan pendidikan dan pengujian keamanan di lingkungan lab yang diotorisasi. Jangan gunakan pada sistem yang bukan milik Anda.

---

## Arsitektur

```
Source Code (WordPress + Plugins)
        ↓
┌───────────────────────────────────┐
│   Phase 1: Automated Scanning     │
│   Semgrep · CodeQL · Pattern Grep │
│          @auto-scan               │
└───────────────┬───────────────────┘
                ↓
┌───────────────────────────────────┐
│   Phase 2: AI-Assisted Audit      │
│   Data Flow Trace · Logic Review  │
│          @manual-audit            │
└───────────────┬───────────────────┘
                ↓
┌───────────────────────────────────┐
│   Phase 3: Candidate Report       │
│   Structured JSON · Exploit Chains│
│          @pentest                 │
└───────────────┬───────────────────┘
                ↓
        Manual Verification
        (Burp Suite / PoC)
```

## CVE Lab

| CVE ID | Plugin | Vulnerability | Severity |
|--------|--------|---------------|----------|
| CVE-2026-1357 | WPvivid Backup | Remote Code Execution | Critical |
| CVE-2026-1492 | WP File Upload (User Registration) | Privilege Escalation → Admin | Critical |
| CVE-2026-2599 | Contact Form Entries | Unauthenticated PHP Object Injection | High |
| CVE-2026-3459 | Drag & Drop Multiple File Upload – CF7 | Unauthenticated Arbitrary File Upload → RCE | High |

Setiap folder di `lab-cve/` berisi:
- `exploit.py` — PoC exploit (single & mass mode)
- `scanner.py` — Vulnerability scanner
- `riset.md` / `README.md` — Dokumentasi teknis & analisis
- Plugin source code (`.zip`) untuk analisis lokal

---

## Prasyarat

| Tool | Versi | Keterangan |
|------|-------|------------|
| [Python](https://www.python.org/) | 3.10+ | Runtime utama |
| [Laragon](https://laragon.org/) | Latest | Local WordPress server (Nginx + PHP 8.3 + MySQL) |
| [VS Code](https://code.visualstudio.com/) | Latest | Editor dengan GitHub Copilot |
| [Semgrep](https://semgrep.dev/) | 1.154.0+ | PHP SAST scanner |
| [CodeQL](https://codeql.github.com/) | 2.24.3+ | JS/Python deep analysis (opsional) |
| [Burp Suite](https://portswigger.net/burp) | Community/Pro | Manual testing & verification |

### VS Code Extensions
- **GitHub Copilot** + **Copilot Chat**
- **Semgrep** (`semgrep.semgrep`)
- **CodeQL** (`github.vscode-codeql`)

---

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/<username>/wp-security-lab.git
cd wp-security-lab
```

### 2. Setup Python Environment

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install semgrep mcp requests
```

### 3. Install CodeQL (Opsional)

Download dari [GitHub CodeQL releases](https://github.com/github/codeql-cli-binaries/releases), extract ke `C:\codeql\`, dan tambahkan ke PATH.

### 4. Setup WordPress Lokal

```bash
# Menggunakan Laragon — start Nginx + PHP + MySQL
# Import WordPress ke webroot
# Install plugin target yang ingin dianalisis
```

### 5. Verifikasi Tools

```powershell
.\.venv\Scripts\semgrep.exe --version    # Semgrep 1.154.0
codeql version --format=terse            # 2.24.3
```

---

## Struktur Workspace

```
.
├── .github/
│   ├── copilot-instructions.md    # Workspace-wide Copilot guidelines
│   ├── agents/
│   │   ├── auto-scan.agent.md     # Automated scanner agent
│   │   ├── manual-audit.agent.md  # Manual audit agent
│   │   └── pentest.agent.md       # Hybrid orchestrator agent
│   ├── prompts/
│   │   ├── pentest.prompt.md      # /pentest — full hybrid scan
│   │   ├── scan-plugin.prompt.md  # /scan-plugin — quick auto scan
│   │   ├── audit-function.prompt.md # /audit-function — deep audit
│   │   ├── trace-flow.prompt.md   # /trace-flow — data flow trace
│   │   └── gadget-hunt.prompt.md  # /gadget-hunt — object injection
│   └── instructions/
│       └── php-security.instructions.md  # Auto-context untuk file PHP
│
├── .semgrep/
│   └── rules/
│       └── wordpress-security.yaml  # 20 custom WordPress security rules
│
├── .vscode/
│   ├── settings.json              # Semgrep + CodeQL config
│   └── mcp.json                   # MCP server config
│
├── lab-cve/
│   ├── cve-2026-1357/             # WPvivid RCE
│   ├── CVE-2026-1492/             # WP File Upload Priv Esc
│   ├── CVE-2026-2599/             # Contact Form Entries ObjInj
│   └── CVE-2026-3459/             # DnD File Upload RCE
│
├── mcp-semgrep-server.py          # MCP server (6 security tools)
├── pentest-scan.py                # CLI orchestration script
├── prompt/                        # Reference prompt templates (JSON)
│   ├── mode auto/                 # Auto scanning prompts
│   ├── manual mode/               # Manual audit prompts
│   └── strategi.md                # Methodology flowchart
│
├── wp-admin/                      # WordPress core
├── wp-content/                    # Plugins & themes (analysis target)
└── wp-includes/                   # WordPress core includes
```

---

## Penggunaan

### Copilot Agents

Invoke agent dengan mengetik `@nama-agent` di Copilot Chat:

| Agent | Fungsi |
|-------|--------|
| `@auto-scan` | Automated scanning — Semgrep + pattern grep → JSON candidates |
| `@manual-audit` | Deep manual audit — trace data flow, exploit chains |
| `@pentest` | Hybrid — auto scan + manual audit (5 phase) |

**Contoh:**
```
@pentest scan plugin flavor di wp-content/plugins/flavor
@manual-audit trace $_POST['template'] ke include() di file loader.php
@auto-scan scan semua plugin
```

### Slash Commands

Ketik `/command` di Copilot Chat:

| Command | Fungsi |
|---------|--------|
| `/pentest` | Full hybrid pentest pada plugin |
| `/scan-plugin` | Quick automated scan |
| `/audit-function` | Deep audit function/endpoint |
| `/trace-flow` | Trace data flow source → sink |
| `/gadget-hunt` | PHP Object Injection & POP chain |

### MCP Server Tools

6 tools tersedia via MCP server (otomatis dipakai oleh agents):

| Tool | Fungsi |
|------|--------|
| `semgrep_scan` | Scan dengan Semgrep configs |
| `semgrep_scan_rule` | Ad-hoc pattern scan |
| `codeql_create_database` | Buat CodeQL database |
| `codeql_analyze` | Jalankan CodeQL analysis |
| `grep_vulnerability_pattern` | Regex pattern search |
| `list_wp_plugins` | Enumerate WordPress plugins |

### CLI Script

```powershell
# Quick scan
python pentest-scan.py wp-content/plugins/target-plugin --quick

# Full scan (Semgrep + CodeQL)
python pentest-scan.py wp-content/plugins/target-plugin --full
```

### Custom Semgrep Rules

20 rules di `.semgrep/rules/wordpress-security.yaml` mencakup:
- SQL Injection (wpdb tanpa prepare)
- XSS (echo user input tanpa escaping)
- CSRF (missing nonce verification)
- Unauthorized AJAX handlers
- Nopriv AJAX (unauthenticated endpoints)
- File inclusion (LFI/RFI)
- File upload tanpa validation
- Command injection
- Deserialization (unserialize user input)
- SSRF, hardcoded credentials, phpinfo exposure

```powershell
# Jalankan custom rules saja
$env:PYTHONUTF8="1"
.\.venv\Scripts\semgrep.exe --config .semgrep/rules/ wp-content/plugins/target/
```

---

## Alur Kerja Riset CVE

```
1. Identifikasi plugin target
   └─ Cek changelog, Wordfence advisories, WPScan DB

2. Download & install plugin rentan di lab lokal
   └─ Laragon (WordPress + Nginx + PHP)

3. Auto scan
   └─ /scan-plugin → Semgrep + pattern grep

4. Manual audit
   └─ /audit-function → trace data flow

5. Construct exploit chain
   └─ @pentest find chains

6. Develop PoC
   └─ exploit.py + scanner.py

7. Verify
   └─ Burp Suite / curl / browser

8. Dokumentasi
   └─ riset.md + README.md di lab-cve/CVE-XXXX-XXXX/
```

---

## Output Format

Semua findings menggunakan structured JSON:

```json
{
  "vulnerability_type": "Remote Code Execution",
  "severity": "Critical",
  "file_path": "includes/ajax-handler.php",
  "line_number": 142,
  "source": "$_POST['template']",
  "sink": "include()",
  "data_flow": "$_POST['template'] -> $template -> include($template)",
  "exploit_chain": "LFI -> file inclusion -> RCE",
  "recommended_manual_test": "POST request dengan template=../../../../etc/passwd"
}
```

> **Penting**: Semua findings = **candidates**, bukan confirmed bugs. Verifikasi manual tetap wajib.

---

## Prioritas Vulnerability

| # | Tipe | Impact |
|---|------|--------|
| 1 | Remote Code Execution (RCE) | Server compromise |
| 2 | PHP Object Injection / Deserialization | RCE via gadget chain |
| 3 | Arbitrary File Upload → RCE | Webshell upload |
| 4 | Privilege Escalation (Subscriber → Admin) | Account takeover |
| 5 | SQL Injection | Data breach |
| 6 | Local File Inclusion / Path Traversal | File read/RCE |
| 7 | SSRF | Internal network access |
| 8 | Stored XSS | Session hijacking |
| 9 | CSRF with impact | Unauthorized actions |

---

## Responsible Disclosure

Semua CVE yang ditemukan di lab ini telah dilaporkan secara bertanggung jawab melalui:
- [Wordfence Bug Bounty Program](https://www.wordfence.com/threat-intel/vulnerabilities/)
- [WPScan Vulnerability Database](https://wpscan.com/)
- Plugin developer secara langsung

Timeline disclosure mengikuti standar 90 hari.

---

## License

Kode exploit dan scanner di repository ini dilisensikan untuk **penggunaan edukasi dan riset keamanan saja**. Penggunaan untuk menyerang sistem tanpa izin adalah ilegal dan melanggar hukum yang berlaku.
