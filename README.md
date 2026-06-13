# 📁 LAN File Server

A lightweight, zero-dependency HTTP file server that lets every device on your **local WiFi** browse and download files from your computer — right in the browser.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![No dependencies](https://img.shields.io/badge/Dependencies-none-brightgreen)

---

## ✨ Features

- 🌐 **Beautiful dark web UI** — works on any browser, mobile-friendly
- 📂 **Navigate folders** with breadcrumb navigation
- ⬇️ **One-click download** button for every file
- 🔒 **Directory traversal protection** — can't escape the served folder
- 🗂 **File type icons** — automatically matched by extension
- 📊 **Stats bar** — shows folder/file count and total size
- 🚫 **Zero dependencies** — uses only Python's standard library
- 🖥 **Cross-platform** — Windows, macOS, Linux

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Mikaeil297/lan-file-server.git
cd lan-file-server

# Serve the current directory on port 8080
python file_server.py

# Serve a specific folder
python file_server.py /path/to/folder

# Custom folder + custom port
python file_server.py /path/to/folder 9090
```

After running, you'll see output like:

```
╔══════════════════════════════════════════════╗
║          📁  LAN File Server  📡             ║
╠══════════════════════════════════════════════╣
║  📂 Serving : /home/user/Downloads           ║
║  🖥  Local  : http://localhost:8080          ║
║  📱 Network : http://192.168.1.42:8080       ║
╠══════════════════════════════════════════════╣
║  Open the Network URL on any device on the   ║
║  same WiFi to browse & download files.       ║
║  Press Ctrl+C to stop the server.            ║
╚══════════════════════════════════════════════╝
```

Open the **Network URL** on any phone, tablet, or computer connected to the same WiFi.

---

## 🖼 Screenshot

> Dark-themed file browser with folder/file icons, size, date, and download button.

---

## ⚙️ Requirements

- Python **3.8** or newer
- No external packages needed

---

## 🔒 Security Notes

- Only share files on **trusted local networks** (home/office WiFi).
- The server is **read-only** — visitors can browse and download, but cannot upload or delete.
- Hidden files (starting with `.`) are automatically excluded from the listing.
- Path traversal attacks are blocked.

---

## 📄 License

[MIT](LICENSE) © [Mikaeil297](https://github.com/Mikaeil297)
