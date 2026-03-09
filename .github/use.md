# Panduan Penggunaan Workspace Pentesting

## Agents

Invoke agent dengan mengetik `@nama-agent` di chat Copilot.

### `@auto-scan`
Scanner otomatis. Jalankan Semgrep, CodeQL, dan pattern grep untuk menghasilkan daftar candidate vulnerability dalam format JSON.

```
@auto-scan scan wp-content/plugins/contact-form-7
```

### `@manual-audit`
Audit manual mendalam. Baca kode, trace data flow, analisis logic flaw, dan construct exploit chain.

```
@manual-audit audit function handle_file_upload di wp-content/plugins/target/includes/upload.php
@manual-audit cek apakah ada privilege escalation di plugin flavor
```

### `@pentest`
Orchestrator hybrid — gabungan auto scan + manual audit dalam 5 phase (recon → scan → AI audit → candidates → deep review).

```
@pentest full pentest pada wp-content/plugins/flavor
@pentest find chains di plugin flavor
@pentest gadget hunt di wp-content/plugins/flavor
```

---

## Slash Commands (Prompts)

Ketik `/nama-prompt` di chat lalu tekan Enter. Akan muncul input field untuk target.

### `/pentest`
Full hybrid pentest pada satu plugin. Menjalankan auto scan + manual audit + chain analysis + report.

> **Agent**: `@pentest`
> **Input**: path plugin (misal `wp-content/plugins/flavor`)

### `/scan-plugin`
Quick automated scan saja — Semgrep + pattern grep → JSON findings.

> **Agent**: `@auto-scan`
> **Input**: path plugin

### `/audit-function`
Deep manual audit pada function atau endpoint tertentu. Trace data flow, cek auth, construct PoC.

> **Agent**: `@manual-audit`
> **Input**: nama function, file path, atau endpoint (misal `wp_ajax_upload_handler`)

### `/trace-flow`
Trace data flow dari source ke sink secara step-by-step.

> **Agent**: `@manual-audit`
> **Input**: deskripsi source dan sink (misal `$_POST['file'] ke include()`)

### `/gadget-hunt`
Cari PHP Object Injection dan POP gadget chains.

> **Agent**: `@auto-scan`
> **Input**: path plugin atau directory

---

## Contoh Alur Kerja

### 1. Pentest Plugin Baru (Full)
```
/pentest
→ input: wp-content/plugins/flavor
→ tunggu report JSON
→ review candidates severity Critical/High
→ test di Burp Suite
```

### 2. Quick Scan → Deep Dive
```
/scan-plugin
→ input: wp-content/plugins/flavor
→ lihat findings
→ /audit-function
→ input: function mencurigakan dari hasil scan
```

### 3. Investigasi Spesifik
```
@manual-audit cek apakah $_POST['template'] di file includes/loader.php bisa reach include()
```

### 4. Object Injection Hunt
```
/gadget-hunt
→ input: wp-content/plugins/flavor
→ jika ditemukan unserialize, lanjut:
@manual-audit trace POP chain dari class CacheHandler::__destruct ke file_put_contents
```

---

## Output

Semua findings menggunakan format JSON:

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

## Catatan Penting

- **Semua findings = candidates**, bukan confirmed bugs. Verifikasi manual tetap wajib.
- Response default dalam **Bahasa Indonesia**.
- PHP instructions otomatis aktif saat membuka file `*.php` — memberikan konteks security pattern WordPress.
