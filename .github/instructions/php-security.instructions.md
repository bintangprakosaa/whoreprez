---
applyTo: "**/*.php"
---

# PHP Security Analysis Context

Saat menganalisis file PHP di workspace ini, perhatikan pola keamanan berikut:

## WordPress Entry Points (Potential Attack Surface)
- `add_action('wp_ajax_*')` — AJAX handler (authenticated)
- `add_action('wp_ajax_nopriv_*')` — AJAX handler (unauthenticated — HIGH RISK)
- `register_rest_route()` — REST API endpoint, cek `permission_callback`
- `add_action('admin_post_*')` — Admin POST handler
- `add_action('admin_init', ...)` — Runs on every admin page load

## Security Checks yang Harus Ada
- `current_user_can()` — capability check (WAJIB di setiap endpoint)
- `wp_verify_nonce()` / `check_ajax_referer()` — CSRF protection
- `sanitize_text_field()`, `absint()`, `esc_html()` — input sanitization
- `$wpdb->prepare()` — parameterized queries (WAJIB untuk semua DB queries)

## Dangerous Sinks (Trace balik ke source!)
- **Code Exec**: `eval()`, `assert()`, `system()`, `exec()`, `shell_exec()`, `passthru()`, `popen()`, `proc_open()`
- **File Include**: `include()`, `require()`, `include_once()`, `require_once()` with dynamic input
- **Deserialization**: `unserialize()`, `maybe_unserialize()` on user input
- **File Ops**: `move_uploaded_file()`, `file_put_contents()`, `fopen()`, `copy()`, `rename()`, `unlink()`
- **Config Mod**: `update_option()`, `update_user_meta()`, `wp_update_user()`
- **SQL**: `$wpdb->query()`, `$wpdb->get_results()` tanpa `$wpdb->prepare()`

## Red Flags
- `is_admin()` dipakai sebagai auth check (ini cek halaman, bukan role!)
- `permission_callback => '__return_true'` di REST route
- `extract($_POST)` atau `extract($_GET)` — variable injection
- `$$variable` — variable variables dari user input
- Serialized data dari user input ke `unserialize()`
- File path construction dari user input tanpa `basename()`/`realpath()`

## Magic Methods (Object Injection Context)
Jika class punya magic methods, cek apakah bisa menjadi gadget:
- `__destruct()` — called saat object destroyed
- `__wakeup()` — called saat unserialize
- `__toString()` — called saat object di-cast ke string
- `__call()` — called saat method tidak exist
- `__invoke()` — called saat object dipanggil sebagai function
