"""
MCP Server for Security Scanning (Semgrep + CodeQL)
Provides tools for white-box penetration testing via VS Code Copilot.
"""
import subprocess
import json
import os
import tempfile
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("security-scanner")

WORKSPACE = Path(r"C:\laragon\www")
SEMGREP = WORKSPACE / ".venv" / "Scripts" / "semgrep.exe"
CODEQL = Path(r"C:\codeql\codeql.exe")
CUSTOM_RULES = WORKSPACE / ".semgrep" / "rules"

ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
    "CODEQL_ALLOW_INSTALLATION_ANYWHERE": "true",
}


@mcp.tool()
def semgrep_scan(
    target: str,
    config: str = "auto",
    severity: str = "",
    max_findings: int = 50,
) -> str:
    """
    Run Semgrep security scan on a file or directory.
    
    Args:
        target: File or directory path to scan (relative to workspace or absolute)
        config: Semgrep config - 'auto', 'p/php', 'p/owasp-top-ten', 'p/security-audit', 'custom', or a specific rule ID
        severity: Filter by severity: 'ERROR', 'WARNING', 'INFO' (empty = all)
        max_findings: Maximum number of findings to return
    """
    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = WORKSPACE / target

    if not target_path.exists():
        return f"Error: Target not found: {target_path}"

    configs = []
    if config == "custom":
        configs = ["--config", str(CUSTOM_RULES)]
    elif config == "auto":
        configs = ["--config", "auto"]
    elif config == "full":
        configs = [
            "--config", "p/php",
            "--config", "p/owasp-top-ten",
            "--config", "p/security-audit",
            "--config", str(CUSTOM_RULES),
        ]
    else:
        configs = ["--config", config]

    cmd = [
        str(SEMGREP), "scan",
        "--json",
        "--include", "*.php",
        "--max-target-bytes", "2000000",
        *configs,
        str(target_path),
    ]

    if severity:
        cmd.extend(["--severity", severity])

    result = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=120)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return f"Semgrep error:\n{result.stderr[:1000]}"

    results = data.get("results", [])
    if not results:
        return f"No findings in {target_path}"

    output_lines = [f"## Semgrep Findings: {len(results)} total (showing max {max_findings})\n"]

    for i, r in enumerate(results[:max_findings]):
        extra = r.get("extra", {})
        meta = extra.get("metadata", {})
        output_lines.append(f"### [{i+1}] {r.get('check_id', 'unknown')}")
        output_lines.append(f"- **Severity:** {extra.get('severity', '?')}")
        output_lines.append(f"- **File:** {r.get('path', '?')}:{r.get('start', {}).get('line', '?')}")
        if meta.get("cwe"):
            output_lines.append(f"- **CWE:** {meta['cwe']}")
        if meta.get("owasp"):
            output_lines.append(f"- **OWASP:** {meta['owasp']}")
        output_lines.append(f"- **Message:** {extra.get('message', '').strip()[:300]}")
        lines_info = extra.get("lines", "")
        if lines_info:
            output_lines.append(f"- **Code:** ```{lines_info.strip()[:200]}```")
        output_lines.append("")

    return "\n".join(output_lines)


@mcp.tool()
def semgrep_scan_rule(target: str, pattern: str, language: str = "php") -> str:
    """
    Run a custom Semgrep pattern against a target. Good for quick ad-hoc checks.
    
    Args:
        target: File or directory to scan
        pattern: Semgrep pattern (e.g., 'eval($_GET[...])', '$wpdb->query("..." . $X . "...")')
        language: Programming language (default: php)
    """
    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = WORKSPACE / target

    cmd = [
        str(SEMGREP), "scan",
        "--json",
        "--pattern", pattern,
        "--lang", language,
        str(target_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=60)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return f"Error: {result.stderr[:500]}"

    results = data.get("results", [])
    if not results:
        return f"No matches for pattern `{pattern}` in {target_path}"

    output = [f"Found {len(results)} matches for `{pattern}`:\n"]
    for r in results[:30]:
        line = r.get("start", {}).get("line", "?")
        path = r.get("path", "?")
        code = r.get("extra", {}).get("lines", "").strip()[:200]
        output.append(f"- **{path}:{line}** — `{code}`")

    return "\n".join(output)


@mcp.tool()
def codeql_create_database(
    source_root: str,
    language: str = "javascript",
    db_name: str = "wp-codeql-db",
) -> str:
    """
    Create a CodeQL database from source code.
    Note: PHP is not natively supported. Use 'javascript' for JS/TS analysis.
    
    Args:
        source_root: Root directory of source code
        language: Language to analyze (javascript, python, ruby, etc.)
        db_name: Name for the database
    """
    if not CODEQL.exists():
        return "Error: CodeQL CLI not found at C:\\codeql\\codeql.exe"

    source_path = Path(source_root)
    if not source_path.is_absolute():
        source_path = WORKSPACE / source_root

    db_path = WORKSPACE / "pentest-results" / db_name
    db_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(CODEQL), "database", "create",
        str(db_path),
        f"--language={language}",
        f"--source-root={source_path}",
        "--overwrite",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=300)

    if result.returncode != 0:
        return f"Error creating CodeQL database:\n{result.stderr[:1000]}"

    return f"CodeQL database created at {db_path}\nLanguage: {language}\nReady for analysis."


@mcp.tool()
def codeql_analyze(
    db_name: str = "wp-codeql-db",
    query_suite: str = "codeql/javascript-queries:codeql-suites/javascript-security-extended.qls",
) -> str:
    """
    Run CodeQL security analysis on a previously created database.
    
    Args:
        db_name: Name of the CodeQL database (created with codeql_create_database)
        query_suite: Query suite to run (e.g., 'codeql/javascript-queries:codeql-suites/javascript-security-extended.qls')
    """
    if not CODEQL.exists():
        return "Error: CodeQL CLI not found"

    db_path = WORKSPACE / "pentest-results" / db_name
    if not db_path.exists():
        return f"Error: Database not found at {db_path}. Run codeql_create_database first."

    results_dir = WORKSPACE / "pentest-results"
    sarif_file = results_dir / f"{db_name}-results.sarif"

    cmd = [
        str(CODEQL), "database", "analyze",
        str(db_path),
        query_suite,
        "--format=sarif-latest",
        f"--output={sarif_file}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=600)

    if result.returncode != 0:
        return f"Error running CodeQL analysis:\n{result.stderr[:1000]}"

    with open(sarif_file, "r", encoding="utf-8") as f:
        sarif = json.load(f)

    findings = []
    for run in sarif.get("runs", []):
        for res in run.get("results", []):
            loc = res.get("locations", [{}])[0].get("physicalLocation", {})
            findings.append({
                "rule": res.get("ruleId", "unknown"),
                "level": res.get("level", "?"),
                "message": res.get("message", {}).get("text", ""),
                "file": loc.get("artifactLocation", {}).get("uri", "?"),
                "line": loc.get("region", {}).get("startLine", "?"),
            })

    if not findings:
        return "No security findings from CodeQL analysis."

    output = [f"## CodeQL Findings: {len(findings)}\n"]
    for i, f in enumerate(findings[:50]):
        output.append(f"### [{i+1}] {f['rule']}")
        output.append(f"- **Level:** {f['level']}")
        output.append(f"- **File:** {f['file']}:{f['line']}")
        output.append(f"- **Message:** {f['message'][:300]}")
        output.append("")

    return "\n".join(output)


@mcp.tool()
def grep_vulnerability_pattern(
    pattern: str,
    target: str = ".",
    file_type: str = "*.php",
) -> str:
    """
    Search for dangerous code patterns using regex grep. Useful for finding
    sinks, sources, and suspicious code quickly.
    
    Args:
        pattern: Regex pattern to search for (e.g., 'eval\\s*\\(', 'shell_exec', '\\$_GET.*query')
        target: Directory to search (relative to workspace)
        file_type: File glob pattern (default: *.php)
    """
    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = WORKSPACE / target

    cmd = [
        "findstr", "/S", "/I", "/N", "/R",
        pattern,
        str(target_path / file_type),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if not result.stdout.strip():
        return f"No matches for `{pattern}` in {target_path}/{file_type}"

    lines = result.stdout.strip().split("\n")
    output = [f"Found {len(lines)} matches for `{pattern}`:\n"]
    for line in lines[:50]:
        output.append(f"- {line.strip()[:200]}")

    if len(lines) > 50:
        output.append(f"\n... and {len(lines) - 50} more matches")

    return "\n".join(output)


@mcp.tool()
def list_wp_plugins(target: str = ".") -> str:
    """
    List all WordPress plugins and their versions for vulnerability research.
    
    Args:
        target: WordPress root directory
    """
    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = WORKSPACE / target

    plugins_dir = target_path / "wp-content" / "plugins"
    if not plugins_dir.exists():
        return f"No plugins directory found at {plugins_dir}"

    plugins = []
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        version = "unknown"
        main_file = None

        for php_file in plugin_dir.glob("*.php"):
            try:
                content = php_file.read_text(encoding="utf-8", errors="ignore")[:3000]
                if "Plugin Name:" in content:
                    main_file = php_file.name
                    for line in content.split("\n"):
                        if "Version:" in line:
                            version = line.split("Version:")[-1].strip().rstrip("*/ ")
                            break
                    break
            except Exception:
                continue

        plugins.append({
            "name": plugin_dir.name,
            "version": version,
            "main_file": main_file or "?",
        })

    if not plugins:
        return "No plugins found."

    output = [f"## WordPress Plugins ({len(plugins)})\n"]
    output.append("| Plugin | Version | Main File |")
    output.append("|--------|---------|-----------|")
    for p in plugins:
        output.append(f"| {p['name']} | {p['version']} | {p['main_file']} |")

    return "\n".join(output)


if __name__ == "__main__":
    mcp.run()
