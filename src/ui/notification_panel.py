# -*- coding: utf-8 -*-
"""
notification_panel.py — Panneau de notifications (cloche dans le header)
Chemin : src/ui/notification_panel.py
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor


TYPE_COLORS = {
    'success': ('#ECFDF5', '#10B981', '✅'),
    'danger':  ('#FEF2F2', '#EF4444', '❌'),
    'warning': ('#FFFBEB', '#F59E0B', '⚠️'),
    'info':    ('#EFF6FF', '#3B82F6', 'ℹ️'),
}


class NotificationItem(QFrame):
    def __init__(self, notif: dict, on_read=None, parent=None):
        super().__init__(parent)
        self.notif = notif
        self.on_read = on_read
        self._build()

    def _build(self):
        ntype = self.notif.get('type', 'info')
        bg, color, icon = TYPE_COLORS.get(ntype, TYPE_COLORS['info'])
        is_read = self.notif.get('is_read', 0)

        self.setStyleSheet(f"""
            QFrame {{
                background: {'#f9fafb' if is_read else bg};
                border-left: 4px solid {color if not is_read else '#e5e7eb'};
                border-radius: 6px;
                margin: 2px 4px;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)

        # Icone
        ico = QLabel(icon)
        ico.setStyleSheet("font-size:18px;")
        ico.setFixedWidth(24)
        lay.addWidget(ico)

        # Contenu
        content = QVBoxLayout()
        content.setSpacing(2)
        title = QLabel(self.notif.get('title', ''))
        title.setStyleSheet(f"font-weight:{'bold' if not is_read else 'normal'}; color:#1f2937; font-size:12px;")
        title.setWordWrap(True)
        msg = QLabel(self.notif.get('message', ''))
        msg.setStyleSheet("color:#6b7280; font-size:11px;")
        msg.setWordWrap(True)
        date = QLabel(str(self.notif.get('created_at', ''))[:16])
        date.setStyleSheet("color:#9ca3af; font-size:10px;")
        content.addWidget(title)
        content.addWidget(msg)
        content.addWidget(date)
        lay.addLayout(content, 1)

        # Bouton marquer lu
        if not is_read and self.on_read:
            btn = QPushButton("✓")
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("background:#e5e7eb; border-radius:12px; font-size:12px; color:#374151;")
            btn.setToolTip("Marquer comme lu")
            btn.clicked.connect(lambda: self.on_read(self.notif['id']))
            lay.addWidget(btn)


class NotificationPanel(QWidget):
    closed = pyqtSignal()

    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setFixedWidth(380)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)
        self._build()
        self.load()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background:#1F4E79; border-radius:12px 12px 0 0;")
        header.setFixedHeight(48)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 12, 0)
        title = QLabel("🔔 Notifications")
        title.setStyleSheet("color:white; font-weight:bold; font-size:13px;")
        hl.addWidget(title)
        hl.addStretch()
        btn_all = QPushButton("Tout lire")
        btn_all.setStyleSheet("background:#2E75B6; color:white; border-radius:6px; padding:3px 10px; font-size:11px;")
        btn_all.clicked.connect(self._mark_all)
        hl.addWidget(btn_all)
        lay.addWidget(header)

        # Liste scrollable
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setFixedHeight(400)
        self._container = QWidget()
        self._list_lay = QVBoxLayout(self._container)
        self._list_lay.setContentsMargins(4, 8, 4, 8)
        self._list_lay.setSpacing(4)
        self._list_lay.addStretch()
        self._scroll.setWidget(self._container)
        lay.addWidget(self._scroll)

        # Footer
        footer = QFrame()
        footer.setStyleSheet("background:#f9fafb; border-radius:0 0 12px 12px; border-top:1px solid #e5e7eb;")
        footer.setFixedHeight(36)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(12, 0, 12, 0)
        self._lbl_count = QLabel("")
        self._lbl_count.setStyleSheet("color:#6b7280; font-size:11px;")
        fl.addWidget(self._lbl_count)
        fl.addStretch()
        lay.addWidget(footer)

    def load(self):
        from src.services.notification_service import get_notifications, count_unread
        notifs = get_notifications(self.user_id)

        # Vider la liste
        while self._list_lay.count() > 1:
            item = self._list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not notifs:
            empty = QLabel("Aucune notification")
            empty.setStyleSheet("color:#9ca3af; font-size:12px; padding:20px;")
            empty.setAlignment(Qt.AlignCenter)
            self._list_lay.insertWidget(0, empty)
        else:
            for i, n in enumerate(notifs):
                item = NotificationItem(n, on_read=self._mark_one)
                self._list_lay.insertWidget(i, item)

        unread = count_unread(self.user_id)
        self._lbl_count.setText(f"{len(notifs)} notification(s) — {unread} non lue(s)")

    def _mark_one(self, notif_id):
        from src.services.notification_service import mark_as_read
        mark_as_read(notif_id)
        self.load()
        self.closed.emit()

    def _mark_all(self):
        from src.services.notification_service import mark_all_read
        mark_all_read(self.user_id)
        self.load()
        self.closed.emit()


class BellButton(QPushButton):
    """Bouton cloche avec badge rouge pour le header."""
    def __init__(self, user_id: int, parent=None):
        super().__init__("🔔", parent)
        self.user_id = user_id
        self._panel = None
        self.setFixedSize(40, 40)
        self.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 20px; border-radius: 20px;
            }
            QPushButton:hover { background: #f3f4f6; }
        """)
        self.clicked.connect(self._toggle_panel)

        # Badge
        self._badge = QLabel("0", self)
        self._badge.setFixedSize(18, 18)
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setStyleSheet("""
            QLabel {
                background: #EF4444; color: white;
                border-radius: 9px; font-size: 10px; font-weight: bold;
            }
        """)
        self._badge.move(22, 0)
        self._badge.setVisible(False)

        # Timer refresh badge toutes les 30s
        self._timer = QTimer(self)
        self._timer.setInterval(30000)
        self._timer.timeout.connect(self.refresh_badge)
        self._timer.start()
        self.refresh_badge()

    def refresh_badge(self):
        from src.services.notification_service import count_unread
        count = count_unread(self.user_id)
        if count > 0:
            self._badge.setText(str(count) if count < 100 else "99+")
            self._badge.setVisible(True)
        else:
            self._badge.setVisible(False)

    def _toggle_panel(self):
        if self._panel and self._panel.isVisible():
            self._panel.hide()
            return
        self._panel = NotificationPanel(self.user_id, parent=None)
        self._panel.closed.connect(self.refresh_badge)
        # Positionner sous la cloche
        pos = self.mapToGlobal(self.rect().bottomRight())
        self._panel.move(pos.x() - self._panel.width(), pos.y() + 4)
        self._panel.show()