

<p align="center">
  <img src="https://raw.githubusercontent.com/Phon3x/phon3x-cmdpad/main/Documents/assets/banner.png" alt="Phon3x-cmdpad banner" width="100%">
</p>

# ⚡ Phon3x-cmdpad

**Phonex-cmdpad** is a lightweight, keyboard-driven command launcher for developers who work in the terminal.

It allows you to **store, search, and instantly copy shell commands** using a fast, fuzzy-search driven interface - without unnecessary UI noise.

Designed for Linux (Wayland-safe) and Windows.

<div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
<img src="https://img.shields.io/badge/License-AGPL%203.0-red.svg" alt="AGPL 3.0 License">
<img src="https://img.shields.io/badge/Platform-Kali%20|%20Ubuntu-orange.svg" alt="Linux Platforms">
<img src="https://img.shields.io/badge/Fedora-294172?logo=fedora&logoColor=white" alt="Fedora">
<img src="https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white" alt="Windows">

</div>

---
## 🎯 Goals & Philosophy

- Speed over features  
- Keyboard-first workflow  
- Minimal UI, zero distraction  
- Local-only data (no cloud, no tracking)

---
## ✨ Features

- ⚡ Ultra-fast fuzzy search (RapidFuzz)
- 📋 Instant copy with **ENTER**
- 🖱️ Optional copy button
- 🧠 SQLite-backed command storage
- 🎯 Live results as you type
- 🪶 Lightweight & responsive
- 🐧 Linux-focused

---
## ❓ Why Phon3x-cmdpad?

🔹 Fast
🔹 Simple
🔹 Predictable
🔹 Terminal-oriented

---
## 🖥️ Preview

> Minimal, terminal-centric UI  
> _(Screenshots coming soon)_

---
## 📦 Installation

### Requirements

- Linux
- Python **3.10+**
- Qt (via PySide6)
### See [`INSTALL.md`](https://github.com/Phon3x/phon3x-cmdpad/blob/main/Documents/INSTALL.md).

---
## ⌨ Keyboard Shortcuts

| Key                                           | Action                |
| --------------------------------------------- | --------------------- |
| `Ctrl + Alt + C` or `(or any which you want)` | Toggle CmdPad         |
| `ESC`                                         | Hide                  |
| `↑ / ↓`                                       | Navigate results      |
| `Enter`                                       | Copy selected command |
| `Ctrl + N`                                    | Add new command       |
| `Ctrl + E`                                    | Edit selected         |
| `Delete`                                      | Delete selected       |

---
## 🧠 How It Works

- Commands are stored in a **local SQLite database**
- Search uses **fuzzy scoring**, not exact matching
- Results update in real time
- Copy logic is optimized for near-zero latency

❗**No cloud sync. | No telemetry. | No global hooks.**

---
## 🛠️ Tech Stack

- **Python**
- **PySide6 (Qt)**
- **SQLite**
- **RapidFuzz**
---
## ⭐ Support

If you find Phon3x-cmdpad useful, you can support the project by:

- ⭐ **Starring** the repository on GitHub  
- 🐛 **Reporting issues or bugs**  
- 💡 **Suggesting features or improvements**  
- 🔄 **Sharing** with the community  
- 📚 **Contributing** to the documentation

