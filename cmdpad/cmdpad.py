#!/home/phon3x/.pyenv/versions/3.12.12/envs/cmdpad/bin/python

import sys
import os
import sqlite3
from rapidfuzz import fuzz

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QFrame, QLabel, QPushButton, QHBoxLayout,
    QDialog, QFormLayout, QTextEdit, QMessageBox,
    QSystemTrayIcon, QMenu
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

APP_NAME = "Phon3x-cmdpad"
SERVER_NAME = "phon3x_cmdpad_single_instance"
FUZZY_THRESHOLD = 60
MAX_RESULTS = 2

# =========================================================
# DB - SETUP
# =========================================================

if sys.platform == "win32":
    base_dir = Path(os.getenv("APPDATA")) / APP_NAME
else:
    base_dir = Path.home() / ".local" / "share" / APP_NAME

base_dir.mkdir(parents=True, exist_ok=True)
DB_PATH = base_dir / "phon3x-cmdpad.db"

# =========================================================
# DB - Functions
# =========================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tags TEXT NOT NULL,
            description TEXT,
            command TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def fetch_commands():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, tags, description, command FROM commands"
    ).fetchall()
    conn.close()
    return rows

def insert_command(tags, desc, cmd):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO commands (tags, description, command) VALUES (?, ?, ?)",
        (tags, desc, cmd)
    )
    conn.commit()
    conn.close()

def update_command(cid, tags, desc, cmd):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE commands SET tags=?, description=?, command=? WHERE id=?",
        (tags, desc, cmd, cid)
    )
    conn.commit()
    conn.close()

def delete_command(cid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM commands WHERE id=?", (cid,))
    conn.commit()
    conn.close()

# =========================================================
# FUZZY
# =========================================================

def fuzzy_score(query, tags, desc, cmd):
    q = query.lower()
    return max(
        fuzz.partial_ratio(q, tags.lower()),
        fuzz.partial_ratio(q, desc.lower()),
        fuzz.partial_ratio(q, cmd.lower()),
    )

# =========================================================
# THEME
# =========================================================

DARK_STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: Inter, Arial, sans-serif;
    font-size: 13px;
}

QLineEdit {
    background-color: #252526;
    border: 1px solid #333;
    padding: 8px;
    border-radius: 6px;
}

QFrame#ResultCard {
    background-color: #252526;
    border-radius: 8px;
}

QFrame#ResultCard[selected="true"] {
    border: 1px solid #3a96dd;
}

QFrame#ResultCard:hover {
    background-color: #2a2d2e;
}

QFrame#Actions {
    opacity: 0.0;
}

QFrame#ResultCard:hover QFrame#Actions {
    opacity: 1.0;
}

QPushButton {
    background: transparent;
    border: none;
    color: #9da0a6;
    padding: 6px 12px;
}

QPushButton:hover {
    color: #3a96dd;
}
"""

# =========================================================
# DIALOG
# =========================================================

class CommandDialog(QDialog):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)

        self.tags = QLineEdit()
        self.desc = QLineEdit()
        self.cmd = QTextEdit()
        self.cmd.setFont(QFont("Monospace", 11))

        if data:
            self.tags.setText(data["tags"])
            self.desc.setText(data["desc"])
            self.cmd.setText(data["cmd"])

        form = QFormLayout(self)
        form.addRow("Tags", self.tags)
        form.addRow("Description", self.desc)
        form.addRow("Command", self.cmd)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        save = QPushButton("Save")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        form.addRow(btns)

    def values(self):
        return {
            "tags": self.tags.text().strip(),
            "desc": self.desc.text().strip(),
            "cmd": self.cmd.toPlainText().strip()
        }

# =========================================================
# CARD
# =========================================================

class ResultCard(QFrame):
    def __init__(self, cid, tags, desc, cmd, on_copy, on_edit, on_delete):
        super().__init__()
        self.cid = cid
        self.cmd = cmd
        self.setObjectName("ResultCard")
        self.setProperty("selected", False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)

        title = QLabel(f" {tags} ")
        title.setStyleSheet("""
            font-weight: 600;
            background-color: #2d2d30;
            border-radius: 4px;
            padding: 2px 6px;
        """)

        desc_lbl = QLabel(f" {desc} ")
        desc_lbl.setStyleSheet("""
            color: #9da0a6;
            background-color: #2a2a2a;
            border-radius: 4px;
            padding: 2px 6px;
        """)

        actions = QFrame()
        actions.setObjectName("Actions")
        act = QHBoxLayout(actions)
        act.setContentsMargins(0, 0, 0, 0)

        copy_btn = QPushButton("Copy")
        edit_btn = QPushButton("Edit")
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("color: #e06c75;")

        copy_btn.clicked.connect(lambda: on_copy(cmd))
        edit_btn.clicked.connect(lambda: on_edit(self))
        del_btn.clicked.connect(lambda: on_delete(self))

        act.addWidget(copy_btn)
        act.addWidget(edit_btn)
        act.addWidget(del_btn)

        top.addWidget(title)
        top.addWidget(desc_lbl, 1)
        top.addWidget(actions)

        cmd_lbl = QLabel(cmd)
        cmd_lbl.setFont(QFont("Monospace", 11))
        cmd_lbl.setStyleSheet("color: #b5cea8; padding-left: 18px;")
        cmd_lbl.setWordWrap(True)

        layout.addLayout(top)
        layout.addWidget(cmd_lbl)

    def set_selected(self, value: bool):
        self.setProperty("selected", value)
        self.style().unpolish(self)
        self.style().polish(self)

# =========================================================
# MAIN WINDOW
# =========================================================

class CmdPad(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.server.newConnection.connect(self.on_new_connection)

        self.cards = []
        self.selected_index = -1

        self.setWindowTitle("cmdPAD")
        self.setFixedWidth(640)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setStyleSheet(DARK_STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search command…")
        self.search.textChanged.connect(self.on_search)

        add_btn = QPushButton("＋ Add")
        add_btn.clicked.connect(self.add_cmd)

        bar.addWidget(self.search, 1)
        bar.addWidget(add_btn)
        outer.addLayout(bar)

        self.results = QVBoxLayout()
        self.results.setSpacing(8)
        outer.addLayout(self.results)

        self.adjust_height(0)
        self.setup_tray()

    # ---------- IPC ----------

    def on_new_connection(self):
        sock = self.server.nextPendingConnection()
        sock.readyRead.connect(lambda s=sock: self.on_socket_read(s))

    def on_socket_read(self, sock):
        sock.readAll()
        sock.disconnectFromServer()
        self.toggle()

    # ---------- Tray (Windows only) ----------

    def setup_tray(self):
        if sys.platform != "win32":
            return
        tray = QSystemTrayIcon(QIcon(), self)
        menu = QMenu()
        menu.addAction("Show / Hide", self.toggle)
        menu.addAction("Quit", QApplication.quit)
        tray.setContextMenu(menu)
        tray.setToolTip("CmdPad")
        tray.show()
        self.tray = tray

    # ---------- Toggle ----------

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            self.search.setFocus()

    # ---------- Helpers ----------

    def clear_results(self):
        self.cards.clear()
        self.selected_index = -1
        while self.results.count():
            item = self.results.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def adjust_height(self, count):
        base = 120
        per = 105
        self.setFixedHeight(min(base + count * per, 440))

    def update_selection(self):
        for i, c in enumerate(self.cards):
            c.set_selected(i == self.selected_index)

    # ---------- Search ----------

    def on_search(self, text):
        query = text.strip()
        self.clear_results()

        if not query:
            self.adjust_height(0)
            return

        scored = []
        for cid, tags, desc, cmd in fetch_commands():
            s = fuzzy_score(query, tags, desc, cmd)
            if s >= FUZZY_THRESHOLD:
                scored.append((s, cid, tags, desc, cmd))

        scored.sort(key=lambda x: x[0], reverse=True)

        for _, cid, tags, desc, cmd in scored[:MAX_RESULTS]:
            card = ResultCard(cid, tags, desc, cmd,
                              self.copy_command,
                              self.edit_card,
                              self.delete_card)
            self.cards.append(card)
            self.results.addWidget(card)

        if self.cards:
            self.selected_index = 0
            self.update_selection()

        self.adjust_height(len(self.cards))

    # ---------- Keyboard ----------

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hide()
            return

        if e.key() == Qt.Key_Down and self.cards:
            self.selected_index = min(self.selected_index + 1, len(self.cards) - 1)
            self.update_selection()
            return

        if e.key() == Qt.Key_Up and self.cards:
            self.selected_index = max(self.selected_index - 1, 0)
            self.update_selection()
            return

        if e.key() == Qt.Key_Return and self.cards:
            QApplication.clipboard().setText(self.cards[self.selected_index].cmd)
            self.hide()
            return

        if e.key() == Qt.Key_E and e.modifiers() & Qt.ControlModifier:
            if self.cards:
                self.edit_card(self.cards[self.selected_index])
            return

        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace) and self.cards:
            self.delete_card(self.cards[self.selected_index])
            return

        if e.key() == Qt.Key_N and e.modifiers() & Qt.ControlModifier:
            self.add_cmd()
            return

    # ---------- Actions ----------

    def add_cmd(self):
        d = CommandDialog(self, "Add Command")
        if d.exec():
            v = d.values()
            if v["cmd"]:
                insert_command(v["tags"], v["desc"], v["cmd"])
                self.on_search(self.search.text())

    def edit_card(self, card):
        row = next(r for r in fetch_commands() if r[0] == card.cid)
        d = CommandDialog(self, "Edit Command", {
            "tags": row[1], "desc": row[2], "cmd": row[3]
        })
        if d.exec():
            v = d.values()
            update_command(card.cid, v["tags"], v["desc"], v["cmd"])
            self.on_search(self.search.text())

    def delete_card(self, card):
        if QMessageBox.question(self, "Delete", "Delete this command?") != QMessageBox.Yes:
            return
        delete_command(card.cid)
        self.on_search(self.search.text())

    def copy_command(self, text: str):
        QApplication.clipboard().setText(text)
        self.hide()

# =========================================================
# ENTRY
# =========================================================

def main():
    init_db()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    sock = QLocalSocket()
    sock.connectToServer(SERVER_NAME)
    if sock.waitForConnected(100):
        sock.write(b"toggle")
        sock.flush()
        return 0

    QLocalServer.removeServer(SERVER_NAME)
    server = QLocalServer()
    server.listen(SERVER_NAME)

    w = CmdPad(server)
    w.show()

    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
