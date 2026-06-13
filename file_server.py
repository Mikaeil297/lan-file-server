#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║          📁  LAN File Server  📡             ║
║  Share files over your local WiFi network.   ║
║  GitHub: https://github.com/Mikaeil297       ║
╚══════════════════════════════════════════════╝

Usage:
  python file_server.py                  # serve current directory on port 8080
  python file_server.py /path/to/folder  # serve a specific directory
  python file_server.py /path/to/folder 9090  # custom port
"""

import http.server
import os
import socket
import sys
import urllib.parse
import html
import mimetypes
from pathlib import Path
from datetime import datetime

# ─── Configuration ──────────────────────────────────────────
DEFAULT_PORT = 8080
DEFAULT_DIR  = "."   # Directory to serve (. = current directory)
# ────────────────────────────────────────────────────────────


def get_local_ip() -> str:
    """Detect the machine's local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def human_size(size_bytes: int) -> str:
    """Convert a byte count into a human-readable string (e.g. 3.2 MB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def file_icon(name: str, is_dir: bool) -> str:
    """Return an emoji icon that matches the file type."""
    if is_dir:
        return "📁"
    ext = Path(name).suffix.lower()
    icons = {
        ".pdf": "📄", ".doc": "📝", ".docx": "📝", ".txt": "📃", ".md": "📃",
        ".jpg": "🖼️", ".jpeg": "🖼️", ".png": "🖼️", ".gif": "🖼️",
        ".svg": "🖼️", ".webp": "🖼️", ".bmp": "🖼️",
        ".mp4": "🎬", ".mkv": "🎬", ".avi": "🎬", ".mov": "🎬", ".webm": "🎬",
        ".mp3": "🎵", ".wav": "🎵", ".flac": "🎵", ".aac": "🎵", ".ogg": "🎵",
        ".zip": "📦", ".rar": "📦", ".tar": "📦", ".gz": "📦", ".7z": "📦",
        ".py": "🐍", ".js": "📜", ".ts": "📜", ".html": "🌐",
        ".css": "🎨", ".json": "🔧", ".xml": "🔧", ".yaml": "🔧", ".yml": "🔧",
        ".xls": "📊", ".xlsx": "📊", ".csv": "📊",
        ".exe": "⚙️", ".apk": "📱", ".sh": "💻", ".bat": "💻",
        ".iso": "💿", ".dmg": "💿",
    }
    return icons.get(ext, "📎")


# ─── HTML Template ───────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📁 {title} — LAN File Server</title>
<style>
  :root {{
    --bg:      #0f1117;
    --surface: #1a1d27;
    --accent:  #6c63ff;
    --accent2: #a78bfa;
    --text:    #e2e8f0;
    --muted:   #94a3b8;
    --border:  #2d3154;
    --hover:   #2a2f4a;
    --radius:  12px;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }}

  /* ── Header ── */
  header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    position: sticky;
    top: 0;
    z-index: 10;
    backdrop-filter: blur(10px);
  }}

  .logo {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--accent2);
    letter-spacing: -0.3px;
    white-space: nowrap;
  }}

  .breadcrumb {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.83rem;
    color: var(--muted);
    flex-wrap: wrap;
  }}
  .breadcrumb a {{ color: var(--accent2); text-decoration: none; transition: color .2s; }}
  .breadcrumb a:hover {{ color: #fff; }}
  .breadcrumb sep {{ color: var(--border); user-select: none; }}

  /* ── Main ── */
  .container {{
    max-width: 960px;
    margin: 0 auto;
    padding: 28px 20px;
  }}

  /* ── Stats bar ── */
  .stats-bar {{
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }}
  .stat {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 0.78rem;
    color: var(--muted);
  }}
  .stat strong {{ color: var(--accent2); }}

  /* ── File list ── */
  .file-list {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }}

  .file-item {{
    display: flex;
    align-items: center;
    padding: 13px 20px;
    border-bottom: 1px solid var(--border);
    transition: background .14s;
    text-decoration: none;
    color: inherit;
    gap: 14px;
  }}
  .file-item:last-child {{ border-bottom: none; }}
  .file-item:hover {{ background: var(--hover); }}

  .file-icon {{ font-size: 1.35rem; width: 30px; text-align: center; flex-shrink: 0; }}

  .file-info {{ flex: 1; min-width: 0; }}
  .file-name {{
    font-weight: 500;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 1px;
  }}
  .file-meta {{ font-size: 0.73rem; color: var(--muted); }}

  .file-size {{
    font-size: 0.78rem;
    color: var(--muted);
    flex-shrink: 0;
    min-width: 56px;
    text-align: right;
  }}

  .download-btn {{
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 5px 13px;
    font-size: 0.73rem;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    flex-shrink: 0;
    transition: background .2s, transform .1s;
    letter-spacing: 0.2px;
  }}
  .download-btn:hover {{ background: var(--accent2); transform: scale(1.04); }}

  /* ── Empty state ── */
  .empty {{
    text-align: center;
    padding: 60px 20px;
    color: var(--muted);
  }}
  .empty .icon {{ font-size: 2.8rem; margin-bottom: 10px; }}

  /* ── Footer ── */
  footer {{
    text-align: center;
    padding: 22px;
    color: var(--muted);
    font-size: 0.76rem;
    border-top: 1px solid var(--border);
    margin-top: 40px;
  }}
  footer a {{ color: var(--accent2); text-decoration: none; }}
  footer a:hover {{ text-decoration: underline; }}

  /* ── Mobile ── */
  @media (max-width: 600px) {{
    header {{ padding: 12px 16px; flex-direction: column; align-items: flex-start; }}
    .file-item {{ padding: 11px 14px; gap: 10px; }}
    .download-btn {{ display: none; }}
    .file-size {{ display: none; }}
  }}
</style>
</head>
<body>

<header>
  <div class="logo">📁 LAN File Server</div>
  <div class="breadcrumb">{breadcrumb}</div>
</header>

<div class="container">
  <div class="stats-bar">
    <div class="stat">📂 Folders: <strong>{folder_count}</strong></div>
    <div class="stat">📎 Files: <strong>{file_count}</strong></div>
    <div class="stat">💾 Total size: <strong>{total_size}</strong></div>
  </div>

  <div class="file-list">
    {items}
  </div>
  {empty_msg}
</div>

<footer>
  LAN File Server &nbsp;•&nbsp; {time} &nbsp;•&nbsp;
  <a href="https://github.com/Mikaeil297" target="_blank">github.com/Mikaeil297</a>
</footer>

</body>
</html>"""


# ─── Request Handler ─────────────────────────────────────────

class FileHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):  # noqa: A002
        """Custom compact log line."""
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} → {args[0]}")

    def do_GET(self):
        # Decode URL and strip query string
        raw_path = urllib.parse.unquote(self.path).split("?")[0]
        full_path = os.path.normpath(os.path.join(SERVE_DIR, raw_path.lstrip("/")))

        # Security: prevent directory traversal
        abs_serve = os.path.abspath(SERVE_DIR)
        abs_full  = os.path.abspath(full_path)
        if not abs_full.startswith(abs_serve):
            self.send_error(403, "Access denied")
            return

        if os.path.isdir(abs_full):
            self._serve_directory(abs_full, raw_path)
        elif os.path.isfile(abs_full):
            self._serve_file(abs_full)
        else:
            self.send_error(404, "File not found")

    # ── Directory listing ────────────────────────────────────

    def _serve_directory(self, abs_path: str, url_path: str):
        try:
            names = sorted(
                os.listdir(abs_path),
                key=lambda x: (not os.path.isdir(os.path.join(abs_path, x)), x.lower())
            )
        except PermissionError:
            self.send_error(403, "Permission denied")
            return

        folder_count = file_count = total_bytes = 0
        items_html = ""

        # "Go up" link
        if url_path not in ("/", ""):
            parent = str(Path(url_path).parent)
            if not parent.endswith("/"):
                parent += "/"
            items_html += f"""
            <a class="file-item" href="{parent}">
              <div class="file-icon">⬆️</div>
              <div class="file-info">
                <div class="file-name">.. (parent folder)</div>
              </div>
            </a>"""

        for name in names:
            if name.startswith("."):
                continue  # skip hidden files

            full     = os.path.join(abs_path, name)
            is_dir   = os.path.isdir(full)
            icon     = file_icon(name, is_dir)
            safe_name = html.escape(name)

            try:
                stat  = os.stat(full)
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d  %H:%M")
                if is_dir:
                    size_str = "—"
                    folder_count += 1
                else:
                    sz = stat.st_size
                    total_bytes += sz
                    size_str = human_size(sz)
                    file_count += 1
            except OSError:
                mtime    = "—"
                size_str = "—"

            item_url = urllib.parse.quote(
                url_path.rstrip("/") + "/" + name + ("/" if is_dir else "")
            )

            dl_btn = (
                ""
                if is_dir
                else f'<a class="download-btn" href="{item_url}" download>⬇ Download</a>'
            )

            items_html += f"""
            <a class="file-item" href="{item_url}">
              <div class="file-icon">{icon}</div>
              <div class="file-info">
                <div class="file-name">{safe_name}</div>
                <div class="file-meta">{mtime}</div>
              </div>
              <div class="file-size">{size_str}</div>
              {dl_btn}
            </a>"""

        # Empty folder message
        empty_msg = ""
        if not items_html.strip():
            empty_msg = '<div class="empty"><div class="icon">📭</div><div>This folder is empty.</div></div>'
            items_html = ""

        # Breadcrumb
        parts = [p for p in url_path.strip("/").split("/") if p]
        bc    = '<a href="/">🏠 Home</a>'
        cum   = ""
        for part in parts:
            cum += "/" + part
            bc  += f' <sep>/</sep> <a href="{cum}/">{html.escape(part)}</a>'

        title = parts[-1] if parts else "Home"
        page  = HTML_TEMPLATE.format(
            title        = html.escape(title),
            breadcrumb   = bc,
            folder_count = folder_count,
            file_count   = file_count,
            total_size   = human_size(total_bytes),
            items        = items_html,
            empty_msg    = empty_msg,
            time         = datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        encoded = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    # ── File download ────────────────────────────────────────

    def _serve_file(self, abs_path: str):
        mime, _ = mimetypes.guess_type(abs_path)
        if not mime:
            mime = "application/octet-stream"

        try:
            size     = os.path.getsize(abs_path)
            filename = os.path.basename(abs_path)
            with open(abs_path, "rb") as f:
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(size))
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="{urllib.parse.quote(filename)}"',
                )
                self.end_headers()
                while chunk := f.read(65536):
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # user cancelled the download
        except OSError as e:
            self.send_error(500, str(e))


# ─── Entry Point ─────────────────────────────────────────────

def main():
    global SERVE_DIR, PORT

    args = sys.argv[1:]
    SERVE_DIR = os.path.abspath(args[0] if args else DEFAULT_DIR)
    PORT      = int(args[1]) if len(args) > 1 else DEFAULT_PORT

    if not os.path.isdir(SERVE_DIR):
        print(f"❌ Error: directory '{SERVE_DIR}' does not exist.")
        sys.exit(1)

    local_ip = get_local_ip()
    dir_display = SERVE_DIR if len(SERVE_DIR) <= 38 else "…" + SERVE_DIR[-37:]

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║          📁  LAN File Server  📡             ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  📂 Serving : {dir_display:<38} ║")
    print(f"║  🖥  Local  : http://localhost:{PORT:<5}              ║")
    print(f"║  📱 Network : http://{local_ip}:{PORT:<5}            ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  Open the Network URL on any device on the   ║")
    print("║  same WiFi to browse & download files.       ║")
    print("║  Press Ctrl+C to stop the server.            ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    server = http.server.HTTPServer(("0.0.0.0", PORT), FileHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
  
