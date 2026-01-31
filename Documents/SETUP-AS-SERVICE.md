# Phon3x-cmdpad – Run as User Service (Linux)

This guide explains how to run cmdpad automatically on login using a **systemd user service**.

This allows cmdpad to:
- start on user login
- run in background
- work without any terminal
- be available instantly via global shortcut

---

## Why use a systemd user service?

- No terminal windows
- Clean startup/shutdown
- Wayland-safe
- Standard Linux solution
- Runs as your user (no root)

---

## 1. Create systemd user directory

```bash
mkdir -p ~/.config/systemd/user
```

## 2. Create CmdPad service file

```bash
nano ~/.config/systemd/user/cmdpad.service
```

Paste the following content:

```bash
[Unit]
Description=Phon3x-cmdpad Launcher
After=graphical-session.target

[Service]
Type=simple
ExecStart=/home/YOUR-USERNAME/.local/bin/cmdpad
Restart=on-failure
Environment=QT_QPA_PLATFORM=wayland

[Install]
WantedBy=default.target
```
⚠ Replace YOUR-USERNAME with your actual username.

## 3. Reload systemd user services

```bash
systemctl --user daemon-reload
```

## 4. Enable cmdpad on login

```bash
systemctl --user enable cmdpad
```

## 5. Start cmdpad immediately (optional)

```bash
systemctl --user start cmdpad
```

## 6. Verify status

```bash
systemctl --user status cmdpad
```

## 7. Usage

- cmdpad runs in background
- Press your global shortcut (Ctrl + Alt + C) [which you setup before]
- cmdpad window appears
- Press ESC to hide

## Stop / Disable

To stop:
```bash
systemctl --user stop cmdpad
```

To disable autostart:
```bash
systemctl --user disable cmdpad
```
