path = r'C:\Eclipse\academic-scheduler\src\ui\app_window.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

timer_methods = '''
    def _reset_inactivity(self):
        self._inactivity_minutes = 0
        self._warning_shown = False

    def _check_inactivity(self):
        if self._user is None:
            return
        self._inactivity_minutes += 1
        remaining = 5 - self._inactivity_minutes
        if self._inactivity_minutes >= 3 and not self._warning_shown:
            self._warning_shown = True
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Inactivite detectee")
            msg.setText(f"Vous serez deconnecte dans {remaining} minute(s).\\nCliquez OK pour rester connecte.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            self._reset_inactivity()
        elif self._inactivity_minutes >= 5:
            self._inactivity_timer.stop()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Session expiree", "Deconnecte automatiquement pour inactivite.")
            self._logout()

    def mousePressEvent(self, event):
        self._reset_inactivity()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        self._reset_inactivity()
        super().keyPressEvent(event)

'''

if '_check_inactivity' not in content:
    content = content.replace('    def center(self):', timer_methods + '    def center(self):')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK methodes timer ajoutees!")
else:
    print("-- deja present")