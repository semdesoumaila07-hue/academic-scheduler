path = r'C:\Eclipse\academic-scheduler\src\ui\app_window.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Trouver la ligne contenant "_set_active_btn"
insert_at = None
for i, line in enumerate(lines):
    if 'def _set_active_btn' in line:
        insert_at = i
        break

if insert_at is None:
    print("Ligne _set_active_btn non trouvee!")
else:
    timer_code = [
        '\n',
        '    def _reset_inactivity(self):\n',
        '        self._inactivity_minutes = 0\n',
        '        self._warning_shown = False\n',
        '\n',
        '    def _check_inactivity(self):\n',
        '        if self._user is None:\n',
        '            return\n',
        '        self._inactivity_minutes += 1\n',
        '        remaining = 5 - self._inactivity_minutes\n',
        '        if self._inactivity_minutes >= 3 and not self._warning_shown:\n',
        '            self._warning_shown = True\n',
        '            from PyQt5.QtWidgets import QMessageBox\n',
        '            msg = QMessageBox(self)\n',
        '            msg.setWindowTitle("Inactivite detectee")\n',
        '            msg.setText(f"Vous serez deconnecte dans {remaining} minute(s).\\nCliquez OK pour rester connecte.")\n',
        '            msg.setIcon(QMessageBox.Warning)\n',
        '            msg.exec_()\n',
        '            self._reset_inactivity()\n',
        '        elif self._inactivity_minutes >= 5:\n',
        '            self._inactivity_timer.stop()\n',
        '            from PyQt5.QtWidgets import QMessageBox\n',
        '            QMessageBox.information(self, "Session expiree", "Deconnecte automatiquement pour inactivite.")\n',
        '            self._logout()\n',
        '\n',
        '    def mousePressEvent(self, event):\n',
        '        self._reset_inactivity()\n',
        '        super().mousePressEvent(event)\n',
        '\n',
        '    def keyPressEvent(self, event):\n',
        '        self._reset_inactivity()\n',
        '        super().keyPressEvent(event)\n',
        '\n',
    ]
    lines = lines[:insert_at] + timer_code + lines[insert_at:]
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"OK methodes inserees avant la ligne {insert_at+1}")