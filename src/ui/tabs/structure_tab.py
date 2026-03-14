"""
Onglet Structure — VERSION SQLite
UC1 : Configurer la structure universitaire.
Toutes les opérations utilisent SQLAlchemy / db_manager.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QTabWidget,
    QDialog, QLineEdit, QComboBox, QMessageBox, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime

from src.database.db_manager import db_manager
from src.managers.structure_manager import StructureManager
from src.database.models import ProgramLevelEnum
from src.database.repositories import (
    UniversityRepository, UFRRepository, ProgramRepository, CohortRepository
)


class StructureTab(QWidget):
    """Onglet de gestion de la structure universitaire."""

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        # ✅ Connexion SQLite
        self.session = db_manager.get_session()
        self.structure_manager = StructureManager(self.session)
        self.data = {
            "universites": [],
            "ufrs": [],
            "programmes": [],
            "cohortes": []
        }
        self.load_data()
        self.init_ui()

    # ==========================================
    # CHARGEMENT DEPUIS SQLITE
    # ==========================================

    def load_data(self):
        """Charge toutes les données depuis SQLite."""
        try:
            univs = self.structure_manager.get_all_universities()
            self.data["universites"] = [
                {'id': u.id, 'nom': u.name, 'code': u.code,
                 'ville': u.city or '', 'adresse': u.address or ''}
                for u in univs
            ]
            ufrs = []
            for u in univs:
                ufrs += self.structure_manager.get_ufrs_by_university(u.id)
            self.data["ufrs"] = [
                {'id': u.id, 'nom': u.name, 'code': u.code,
                 'directeur': u.director or '', 'universite_id': u.university_id}
                for u in ufrs
            ]
            programmes = []
            for u in ufrs:
                programmes += self.structure_manager.get_programs_by_ufr(u.id)
            self.data["programmes"] = [
                {'id': p.id, 'nom': p.name, 'code': p.code,
                 'niveau': p.level.value if hasattr(p.level, 'value') else str(p.level),
                 'ufr_id': p.ufr_id, 'duree_annees': p.duration_years or 3}
                for p in programmes
            ]
            cohortes = []
            for p in programmes:
                cohortes += self.structure_manager.get_cohorts_by_program(p.id)
            self.data["cohortes"] = [
                {'id': c.id, 'nom': c.name,
                 'annee_academique': c.academic_year or '',
                 'semestre': {
                     1: 'Semestre 1', 2: 'Semestre 2', 3: 'Semestre 3',
                     4: 'Semestre 4', 5: 'Semestre 5', 6: 'Semestre 6',
                     7: 'M1', 8: 'M2', 9: 'M3', 10: 'M4',
                     11: 'Doctorat 1', 12: 'Doctorat 2', 13: 'Doctorat 3',
                 }.get(c.semester, str(c.semester) if c.semester else ''),
                 'date_debut': str(c.start_date) if c.start_date else '',
                 'date_fin': str(c.end_date) if c.end_date else '',
                 'effectif': c.student_count or 0,
                 'programme_id': c.program_id}
                for c in cohortes
            ]
        except Exception as e:
            print(f"Erreur chargement structure SQLite: {e}")

    def save_data(self):
        """Plus nécessaire — SQLAlchemy gère la persistance."""
        pass

    def get_existing_codes(self, key):
        return [item.get('code', '') for item in self.data.get(key, [])]

    # ==========================================
    # ACTIONS CRUD — SQLite
    # ==========================================

    def add_universite(self):
        dialog = UniversiteDialog(self, existing_codes=self.get_existing_codes("universites"))
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            try:
                res = self.structure_manager.create_university(
                    name=result['nom'], code=result['code'],
                    address=result.get('adresse', ''), city=result.get('ville', ''),
                    current_user=self.current_user
                )
                if res['success']:
                    self.load_data(); self.refresh_all_tabs(); self.update_statistics()
                    self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ Université '{result['nom']}' ajoutée !")
                else:
                    QMessageBox.warning(self, "Erreur", res.get('error', 'Erreur inconnue'))
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def add_ufr(self):
        if not self.data["universites"]:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord créer une université !"); return
        dialog = UFRDialog(self, self.data["universites"], existing_codes=self.get_existing_codes("ufrs"))
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            try:
                res = self.structure_manager.create_ufr(
                    name=result['nom'], code=result['code'],
                    director=result.get('directeur', ''), university_id=result['universite_id'],
                    current_user=self.current_user
                )
                if res['success']:
                    self.load_data(); self.refresh_all_tabs(); self.update_statistics()
                    self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ UFR '{result['nom']}' ajoutée !")
                else:
                    QMessageBox.warning(self, "Erreur", res.get('error', 'Erreur inconnue'))
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def add_programme(self):
        if not self.data["ufrs"]:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord créer une UFR !"); return
        dialog = ProgrammeDialog(self, self.data["ufrs"], existing_codes=self.get_existing_codes("programmes"))
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            try:
                niveau_map = {
                    'Licence 1': ProgramLevelEnum.LICENCE_1, 'Licence 2': ProgramLevelEnum.LICENCE_2,
                    'Licence 3': ProgramLevelEnum.LICENCE_3, 'Master 1': ProgramLevelEnum.MASTER_1,
                    'Master 2': ProgramLevelEnum.MASTER_2, 'Doctorat': ProgramLevelEnum.DOCTORAT,
                }
                niveau_enum = niveau_map.get(result.get('niveau'), ProgramLevelEnum.LICENCE_1)

                res = self.structure_manager.create_program(
                    name=result['nom'], code=result['code'], level=niveau_enum,
                    duration_years=result.get('duree_annees', 3), ufr_id=result['ufr_id'],
                    current_user=self.current_user
                )
                if res['success']:
                    self.load_data(); self.refresh_all_tabs(); self.update_statistics()
                    self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ Parcours '{result['nom']}' ajouté !")
                else:
                    QMessageBox.warning(self, "Erreur", res.get('error', 'Erreur inconnue'))
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def add_cohorte(self):
        if not self.data["programmes"]:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord créer un parcours !"); return
        dialog = CohorteDialog(self, self.data["programmes"])
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            try:
                def parse_date(s):
                    if not s: return None
                    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
                        try:
                            return datetime.strptime(s, fmt).date()
                        except ValueError: pass
                    return None
                sem_str = result.get('semestre', 'Semestre 1')
                sem_num = CohorteDialog.SEMESTRE_TO_INT.get(sem_str, 1)
                res = self.structure_manager.create_cohort(
                    name=result['nom'], academic_year=result.get('annee_academique', ''),
                    semester=sem_num, student_count=result.get('effectif', 0),
                    program_id=result['programme_id'],
                    start_date=parse_date(result.get('date_debut')),
                    end_date=parse_date(result.get('date_fin')),
                    current_user=self.current_user
                )
                if res['success']:
                    self.load_data(); self.refresh_all_tabs(); self.update_statistics()
                    self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ Classe '{result['nom']}' ajoutée !")
                else:
                    QMessageBox.warning(self, "Erreur", res.get('error', 'Erreur inconnue'))
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def edit_universite_by_index(self, index):
        if index < len(self.data['universites']):
            univ = self.data['universites'][index]
            dialog = UniversiteDialog(self, data=univ,
                existing_codes=[u['code'] for u in self.data["universites"] if u.get('id') != univ.get('id')])
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.get_data()
                try:
                    repo = UniversityRepository(self.session)
                    m = repo.get_by_id(univ['id'])
                    if m:
                        m.name = result['nom']; m.code = result['code']
                        m.city = result.get('ville', ''); m.address = result.get('adresse', '')
                        self.session.commit()
                    self.load_data(); self.refresh_all_tabs(); self.update_statistics()
                    self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ Université '{result['nom']}' modifiée !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def delete_universite_by_index(self, index):
        if index < len(self.data['universites']):
            univ = self.data['universites'][index]
            nb = len([u for u in self.data["ufrs"] if u.get("universite_id") == univ.get("id")])
            msg = f"Voulez-vous supprimer '{univ.get('nom')}' ?"
            if nb > 0: msg += f"\n\n⚠️ {nb} UFR associée(s) seront aussi supprimées."
            if QMessageBox.question(self, "Confirmation", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                try:
                    UniversityRepository(self.session).delete(univ['id'])
                    self.session.commit(); self.load_data(); self.refresh_all_tabs()
                    self.update_statistics(); self._notify_main_window()
                    QMessageBox.information(self, "Succès", "✅ Université supprimée !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def edit_ufr_by_index(self, index):
        if index < len(self.data["ufrs"]):
            ufr = self.data["ufrs"][index]
            dialog = UFRDialog(self, self.data["universites"], data=ufr,
                existing_codes=[u['code'] for u in self.data["ufrs"] if u.get('id') != ufr.get('id')])
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.get_data()
                try:
                    m = UFRRepository(self.session).get_by_id(ufr['id'])
                    if m:
                        m.name = result['nom']; m.code = result['code']
                        m.director = result.get('directeur', ''); m.university_id = result['universite_id']
                        self.session.commit()
                    self.load_data(); self.refresh_all_tabs(); self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ UFR '{result['nom']}' modifiée !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def delete_ufr_by_index(self, index):
        if index < len(self.data["ufrs"]):
            ufr = self.data["ufrs"][index]
            nb = len([p for p in self.data["programmes"] if p.get("ufr_id") == ufr.get("id")])
            msg = f"Voulez-vous supprimer '{ufr.get('nom')}' ?"
            if nb > 0: msg += f"\n\n⚠️ {nb} parcours associé(s) seront aussi supprimés."
            if QMessageBox.question(self, "Confirmation", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                try:
                    UFRRepository(self.session).delete(ufr['id'])
                    self.session.commit(); self.load_data(); self.refresh_all_tabs()
                    self.update_statistics(); self._notify_main_window()
                    QMessageBox.information(self, "Succès", "✅ UFR supprimée !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def edit_parcours_by_index(self, index):
        if index < len(self.data["programmes"]):
            prog = self.data["programmes"][index]
            dialog = ProgrammeDialog(self, self.data["ufrs"], data=prog,
                existing_codes=[p['code'] for p in self.data["programmes"] if p.get('id') != prog.get('id')])
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.get_data()
                try:
                    m = ProgramRepository(self.session).get_by_id(prog['id'])
                    if m:
                        m.name = result['nom']; m.code = result['code']; m.ufr_id = result['ufr_id']
                        self.session.commit()
                    self.load_data(); self.refresh_all_tabs(); self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ Parcours '{result['nom']}' modifié !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def delete_parcours_by_index(self, index):
        if index < len(self.data["programmes"]):
            prog = self.data["programmes"][index]
            nb = len([c for c in self.data["cohortes"] if c.get("programme_id") == prog.get("id")])
            msg = f"Voulez-vous supprimer '{prog.get('nom')}' ?"
            if nb > 0: msg += f"\n\n⚠️ {nb} classe(s) associée(s) seront aussi supprimées."
            if QMessageBox.question(self, "Confirmation", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                try:
                    ProgramRepository(self.session).delete(prog['id'])
                    self.session.commit(); self.load_data(); self.refresh_all_tabs()
                    self.update_statistics(); self._notify_main_window()
                    QMessageBox.information(self, "Succès", "✅ Parcours supprimé !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def edit_classe_by_index(self, index):
        if index < len(self.data["cohortes"]):
            cohorte = self.data["cohortes"][index]
            dialog = CohorteDialog(self, self.data["programmes"], data=cohorte)
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.get_data()
                try:
                    sem_str = result.get('semestre', 'Semestre 1')
                    sem_num = CohorteDialog.SEMESTRE_TO_INT.get(sem_str, 1)
                    m = CohortRepository(self.session).get_by_id(cohorte['id'])
                    if m:
                        m.name = result['nom']
                        m.academic_year = result.get('annee_academique', '')
                        m.student_count = result.get('effectif', 0)
                        m.program_id = result['programme_id']
                        m.semester = sem_num
                        self.session.commit()
                    self.load_data(); self.refresh_all_tabs(); self._notify_main_window()
                    QMessageBox.information(self, "Succès", f"✅ Classe '{result['nom']}' modifiée !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def delete_classe_by_index(self, index):
        if index < len(self.data["cohortes"]):
            cohorte = self.data["cohortes"][index]
            if QMessageBox.question(self, "Confirmation",
                f"Voulez-vous supprimer la classe '{cohorte.get('nom')}' ?\n\nCette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                try:
                    CohortRepository(self.session).delete(cohorte['id'])
                    self.session.commit(); self.load_data(); self.refresh_all_tabs()
                    self.update_statistics(); self._notify_main_window()
                    QMessageBox.information(self, "Succès", "✅ Classe supprimée !")
                except Exception as e:
                    self.session.rollback(); QMessageBox.critical(self, "Erreur", str(e))

    def _notify_main_window(self):
        """Notifie la fenêtre principale qu'une donnée a changé."""
        main_window = self.window()
        if hasattr(main_window, 'on_structure_changed'):
            main_window.on_structure_changed()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # EN-TÊTE
        title = QLabel("Structure Universitaire")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("Gestion des universités, UFR, parcours et classes")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(subtitle)

        # BARRE DE RECHERCHE
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Rechercher dans la structure...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
        """)
        self.search_box.setFixedHeight(45)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Toutes", "Universités", "UFR", "Parcours", "Classes"])
        self.filter_box.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background: white;
                min-width: 150px;
            }
        """)
        self.filter_box.setFixedHeight(45)

        search_layout.addWidget(self.search_box, 3)
        search_layout.addWidget(self.filter_box, 1)
        layout.addLayout(search_layout)

        # BOUTONS D'ACTION
        btn_layout = QHBoxLayout()

        btn_add_univ = QPushButton("➕ Nouvelle Université")
        btn_add_univ.setStyleSheet(self.get_button_style("#3498db"))
        btn_add_univ.setFixedHeight(40)
        btn_add_univ.clicked.connect(self.add_universite)

        btn_add_ufr = QPushButton("➕ Nouvelle UFR")
        btn_add_ufr.setStyleSheet(self.get_button_style("#27ae60"))
        btn_add_ufr.setFixedHeight(40)
        btn_add_ufr.clicked.connect(self.add_ufr)

        btn_add_prog = QPushButton("➕ Nouveau Parcours")
        btn_add_prog.setStyleSheet(self.get_button_style("#8e44ad"))
        btn_add_prog.setFixedHeight(40)
        btn_add_prog.clicked.connect(self.add_programme)

        btn_add_classe = QPushButton("➕ Nouvelle Classe")
        btn_add_classe.setStyleSheet(self.get_button_style("#e67e22"))
        btn_add_classe.setFixedHeight(40)
        btn_add_classe.clicked.connect(self.add_cohorte)

        btn_layout.addWidget(btn_add_univ)
        btn_layout.addWidget(btn_add_ufr)
        btn_layout.addWidget(btn_add_prog)
        btn_layout.addWidget(btn_add_classe)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ONGLETS
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #F5F5F5;
                color: #666;
                padding: 12px 30px;
                margin-right: 2px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1976D2;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #E3F2FD;
            }
        """)

        self.tab_universites = self.create_universites_tab()
        self.tab_ufr = self.create_ufr_tab()
        self.tab_parcours = self.create_parcours_tab()
        self.tab_classes = self.create_classes_tab()

        self.tab_widget.addTab(self.tab_universites, "🏛️  Universités")
        self.tab_widget.addTab(self.tab_ufr, "🎓  UFR")
        self.tab_widget.addTab(self.tab_parcours, "📚  Parcours")
        self.tab_widget.addTab(self.tab_classes, "👥  Classes")

        layout.addWidget(self.tab_widget)

        # STATISTIQUES EN BAS
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)

        self.stat1 = self.create_stat_box("Universités", "0", "#3498db")
        self.stat2 = self.create_stat_box("UFR", "0", "#27ae60")
        self.stat3 = self.create_stat_box("Parcours", "0", "#8e44ad")
        self.stat4 = self.create_stat_box("Classes", "0", "#e67e22")

        self.stats_layout.addWidget(self.stat1)
        self.stats_layout.addWidget(self.stat2)
        self.stats_layout.addWidget(self.stat3)
        self.stats_layout.addWidget(self.stat4)

        layout.addLayout(self.stats_layout)

        self.refresh_all_tabs()
        self.update_statistics()

    # ==========================================
    # ONGLET UNIVERSITÉS
    # ==========================================

    def create_universites_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        self.table_universites = QTableWidget()
        self.table_universites.setColumnCount(6)
        self.table_universites.setHorizontalHeaderLabels([
            "Nom", "Code", "Ville", "Adresse", "Nb UFR", "Actions"
        ])

        header = self.table_universites.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_universites.setColumnWidth(5, 120)
        self.table_universites.setStyleSheet(self.get_table_style())
        self.table_universites.setAlternatingRowColors(True)
        self.table_universites.verticalHeader().setVisible(False)
        self.table_universites.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_universites.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_universites.setRowHeight(0, 50)

        layout.addWidget(self.table_universites)
        return widget

    def refresh_universites_table(self):
        """✅ CORRIGÉ : Utilise l'index de ligne, pas le lambda."""
        self.table_universites.setRowCount(0)

        for i, univ in enumerate(self.data['universites']):
            row = self.table_universites.rowCount()
            self.table_universites.insertRow(row)
            self.table_universites.setRowHeight(row, 50)

            self.table_universites.setItem(row, 0, QTableWidgetItem(univ.get('nom', '')))
            self.table_universites.setItem(row, 1, QTableWidgetItem(univ.get('code', '')))
            self.table_universites.setItem(row, 2, QTableWidgetItem(univ.get('ville', '')))
            self.table_universites.setItem(row, 3, QTableWidgetItem(univ.get('adresse', 'N/A')))

            nb_ufr = len([u for u in self.data['ufrs']
                          if u.get('universite_id') == univ.get('id')])
            self.table_universites.setItem(row, 4, QTableWidgetItem(str(nb_ufr)))

            # ✅ FIX : Passer l'index i directement
            actions = self.create_action_buttons_univ(i)
            self.table_universites.setCellWidget(row, 5, actions)

    def create_action_buttons_univ(self, index):
        """✅ Boutons d'action pour Universités."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(35, 35)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet(self.get_action_btn_style("#E3F2FD"))
        # ✅ Capture correcte de l'index
        btn_edit.clicked.connect(lambda checked, idx=index: self.edit_universite_by_index(idx))

        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(35, 35)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet(self.get_action_btn_style("#FFEBEE"))
        # ✅ Capture correcte de l'index
        btn_delete.clicked.connect(lambda checked, idx=index: self.delete_universite_by_index(idx))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        return widget

    def create_ufr_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        self.table_ufr = self.create_table(
            ["Nom", "Code", "Université", "Directeur", "Parcours", "Actions"]
        )
        layout.addWidget(self.table_ufr)
        return widget

    def refresh_ufr_table(self):
        """✅ CORRIGÉ."""
        self.table_ufr.setRowCount(0)

        for i, ufr in enumerate(self.data["ufrs"]):
            row = self.table_ufr.rowCount()
            self.table_ufr.insertRow(row)
            self.table_ufr.setRowHeight(row, 50)

            self.table_ufr.setItem(row, 0, QTableWidgetItem(ufr.get('nom', 'N/A')))
            self.table_ufr.setItem(row, 1, QTableWidgetItem(ufr.get('code', 'N/A')))

            univ_nom = next(
                (u.get('nom', 'N/A') for u in self.data["universites"]
                 if u.get('id') == ufr.get('universite_id')),
                'N/A'
            )
            self.table_ufr.setItem(row, 2, QTableWidgetItem(univ_nom))
            self.table_ufr.setItem(row, 3, QTableWidgetItem(ufr.get('directeur', 'N/A')))

            nb_prog = len([
                p for p in self.data["programmes"]
                if p.get("ufr_id") == ufr.get("id")
            ])
            self.table_ufr.setItem(row, 4, QTableWidgetItem(f"{nb_prog} Parcours"))

            # ✅ FIX
            actions = self.create_action_buttons_ufr(i)
            self.table_ufr.setCellWidget(row, 5, actions)

    def create_action_buttons_ufr(self, index):
        """✅ Boutons d'action pour UFR."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(35, 35)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet(self.get_action_btn_style("#E3F2FD"))
        btn_edit.clicked.connect(lambda checked, idx=index: self.edit_ufr_by_index(idx))

        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(35, 35)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet(self.get_action_btn_style("#FFEBEE"))
        btn_delete.clicked.connect(lambda checked, idx=index: self.delete_ufr_by_index(idx))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        return widget

    def edit_ufr_by_index(self, index):
        """Éditer une UFR par index."""
        if index < len(self.data["ufrs"]):
            ufr = self.data["ufrs"][index]
            existing_codes = [
                u['code'] for u in self.data["ufrs"]
                if u.get('id') != ufr.get('id')
            ]
            dialog = UFRDialog(
                self, self.data["universites"],
                data=ufr, existing_codes=existing_codes
            )
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.get_data()
                self.data["ufrs"][index].update(result)
                self.save_data()
                self.refresh_all_tabs()
                QMessageBox.information(
                    self, "Succès",
                    f"✅ UFR '{result['nom']}' modifiée avec succès !"
                )

    def delete_ufr_by_index(self, index):
        """Supprimer une UFR par index."""
        if index < len(self.data["ufrs"]):
            ufr = self.data["ufrs"][index]
            nb_prog = len([
                p for p in self.data["programmes"]
                if p.get("ufr_id") == ufr.get("id")
            ])

            msg = f"Voulez-vous supprimer l'UFR '{ufr.get('nom')}' ?"
            if nb_prog > 0:
                msg += f"\n\n⚠️ {nb_prog} parcours associé(s) seront aussi supprimés."

            reply = QMessageBox.question(
                self, "Confirmation",
                msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                ufr_id = ufr.get("id")
                self.data["ufrs"].pop(index)
                self.data["programmes"] = [
                    p for p in self.data["programmes"]
                    if p.get("ufr_id") != ufr_id
                ]
                self.save_data()
                self.refresh_all_tabs()
                self.update_statistics()
                QMessageBox.information(self, "Succès", "✅ UFR supprimée !")

    # ==========================================
    # ONGLET PARCOURS
    # ==========================================

    def create_parcours_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        self.table_parcours = self.create_table(
            ["Nom", "Code", "Niveau", "UFR", "Classes", "Actions"]
        )
        layout.addWidget(self.table_parcours)
        return widget

    def refresh_parcours_table(self):
        """✅ CORRIGÉ."""
        self.table_parcours.setRowCount(0)

        for i, prog in enumerate(self.data["programmes"]):
            row = self.table_parcours.rowCount()
            self.table_parcours.insertRow(row)
            self.table_parcours.setRowHeight(row, 50)

            self.table_parcours.setItem(row, 0, QTableWidgetItem(prog.get('nom', 'N/A')))
            self.table_parcours.setItem(row, 1, QTableWidgetItem(prog.get('code', 'N/A')))
            self.table_parcours.setItem(row, 2, QTableWidgetItem(prog.get('niveau', 'N/A')))

            ufr_nom = next(
                (u.get('nom', 'N/A') for u in self.data["ufrs"]
                 if u.get('id') == prog.get('ufr_id')),
                'N/A'
            )
            self.table_parcours.setItem(row, 3, QTableWidgetItem(ufr_nom))

            nb_classes = len([
                c for c in self.data["cohortes"]
                if c.get("programme_id") == prog.get("id")
            ])
            self.table_parcours.setItem(row, 4, QTableWidgetItem(f"{nb_classes} Classes"))

            # ✅ FIX
            actions = self.create_action_buttons_parcours(i)
            self.table_parcours.setCellWidget(row, 5, actions)

    def create_action_buttons_parcours(self, index):
        """✅ Boutons d'action pour Parcours."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(35, 35)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet(self.get_action_btn_style("#E3F2FD"))
        btn_edit.clicked.connect(
            lambda checked, idx=index: self.edit_parcours_by_index(idx)
        )

        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(35, 35)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet(self.get_action_btn_style("#FFEBEE"))
        btn_delete.clicked.connect(
            lambda checked, idx=index: self.delete_parcours_by_index(idx)
        )

        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        return widget

    def edit_parcours_by_index(self, index):
        """Éditer un parcours par index."""
        if index < len(self.data["programmes"]):
            prog = self.data["programmes"][index]
            existing_codes = [
                p['code'] for p in self.data["programmes"]
                if p.get('id') != prog.get('id')
            ]
            dialog = ProgrammeDialog(
                self, self.data["ufrs"],
                data=prog, existing_codes=existing_codes
            )
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.get_data()
                self.data["programmes"][index].update(result)
                self.save_data()
                self.refresh_all_tabs()
                QMessageBox.information(
                    self, "Succès",
                    f"✅ Parcours '{result['nom']}' modifié avec succès !"
                )

    def delete_parcours_by_index(self, index):
        """Supprimer un parcours par index."""
        if index < len(self.data["programmes"]):
            prog = self.data["programmes"][index]
            nb_cohortes = len([
                c for c in self.data["cohortes"]
                if c.get("programme_id") == prog.get("id")
            ])

            msg = f"Voulez-vous supprimer le parcours '{prog.get('nom')}' ?"
            if nb_cohortes > 0:
                msg += f"\n\n⚠️ {nb_cohortes} classe(s) associée(s) seront aussi supprimées."

            reply = QMessageBox.question(
                self, "Confirmation",
                msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                prog_id = prog.get("id")
                self.data["programmes"].pop(index)
                self.data["cohortes"] = [
                    c for c in self.data["cohortes"]
                    if c.get("programme_id") != prog_id
                ]
                self.save_data()
                self.refresh_all_tabs()
                self.update_statistics()
                QMessageBox.information(self, "Succès", "✅ Parcours supprimé !")

    # ==========================================
    # ONGLET CLASSES
    # ==========================================

    def create_classes_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # ✅ Ajout des colonnes Date début et Date fin
        self.table_classes = QTableWidget()
        self.table_classes.setColumnCount(8)
        self.table_classes.setHorizontalHeaderLabels([
            "Nom", "Parcours", "Année", "Semestre",
            "Date début", "Date fin", "Effectif", "Actions"
        ])
        header = self.table_classes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table_classes.setColumnWidth(7, 120)
        self.table_classes.setStyleSheet(self.get_table_style())
        self.table_classes.setAlternatingRowColors(True)
        self.table_classes.verticalHeader().setVisible(False)
        self.table_classes.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_classes.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table_classes)
        return widget

    def refresh_classes_table(self):
        """✅ CORRIGÉ avec date_debut et date_fin."""
        self.table_classes.setRowCount(0)

        for i, cohorte in enumerate(self.data["cohortes"]):
            row = self.table_classes.rowCount()
            self.table_classes.insertRow(row)
            self.table_classes.setRowHeight(row, 50)

            # Nom
            self.table_classes.setItem(
                row, 0, QTableWidgetItem(cohorte.get('nom', 'N/A'))
            )

            # Parcours
            prog_nom = next(
                (
                    f"{p.get('nom', 'N/A')} ({p.get('niveau', '')})"
                    for p in self.data["programmes"]
                    if p.get('id') == cohorte.get('programme_id')
                ),
                'N/A'
            )
            self.table_classes.setItem(row, 1, QTableWidgetItem(prog_nom))

            # Année académique
            self.table_classes.setItem(
                row, 2,
                QTableWidgetItem(cohorte.get('annee_academique', 'N/A'))
            )

            # Semestre
            semestre_item = QTableWidgetItem(cohorte.get('semestre', 'N/A'))
            semestre_item.setForeground(QColor('#1976D2'))
            self.table_classes.setItem(row, 3, semestre_item)

            # ✅ Date début
            date_debut = cohorte.get('date_debut', '')
            date_debut_item = QTableWidgetItem(
                date_debut if date_debut else '—'
            )
            date_debut_item.setForeground(QColor('#27ae60'))
            self.table_classes.setItem(row, 4, date_debut_item)

            # ✅ Date fin
            date_fin = cohorte.get('date_fin', '')
            date_fin_item = QTableWidgetItem(date_fin if date_fin else '—')
            date_fin_item.setForeground(QColor('#e74c3c'))
            self.table_classes.setItem(row, 5, date_fin_item)

            # Effectif
            effectif_item = QTableWidgetItem(
                f"{cohorte.get('effectif', 0)} étudiants"
            )
            if cohorte.get('effectif', 0) > 50:
                effectif_item.setBackground(QColor('#FFF9C4'))
            self.table_classes.setItem(row, 6, effectif_item)

            # Actions
            actions = self.create_action_buttons_classes(i)
            self.table_classes.setCellWidget(row, 7, actions)

    def create_action_buttons_classes(self, index):
        """✅ Boutons d'action pour Classes."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(35, 35)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet(self.get_action_btn_style("#E3F2FD"))
        btn_edit.clicked.connect(
            lambda checked, idx=index: self.edit_classe_by_index(idx)
        )

        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(35, 35)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet(self.get_action_btn_style("#FFEBEE"))
        btn_delete.clicked.connect(
            lambda checked, idx=index: self.delete_classe_by_index(idx)
        )

        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        return widget

    def edit_classe_by_index(self, index):
        """Éditer une classe par index."""
        if index < len(self.data["cohortes"]):
            cohorte = self.data["cohortes"][index]
            dialog = CohorteDialog(self, self.data["programmes"], data=cohorte)
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.get_data()
                self.data["cohortes"][index].update(result)
                self.save_data()
                self.refresh_all_tabs()
                QMessageBox.information(
                    self, "Succès",
                    f"✅ Classe '{result['nom']}' modifiée avec succès !"
                )

    def delete_classe_by_index(self, index):
        """Supprimer une classe par index."""
        if index < len(self.data["cohortes"]):
            cohorte = self.data["cohortes"][index]
            reply = QMessageBox.question(
                self, "Confirmation",
                f"Voulez-vous supprimer la classe '{cohorte.get('nom')}' ?\n\n"
                "Cette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.data["cohortes"].pop(index)
                self.save_data()
                self.refresh_all_tabs()
                self.update_statistics()
                QMessageBox.information(self, "Succès", "✅ Classe supprimée !")

    # ==========================================
    # UTILITAIRES
    # ==========================================

    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet(self.get_table_style())
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            len(headers) - 1, QHeaderView.Fixed
        )
        table.setColumnWidth(len(headers) - 1, 120)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        return table

    def get_action_btn_style(self, hover_color):
        """Style des boutons d'action."""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    def get_table_style(self):
        return """
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #333;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """

    def create_stat_box(self, label, value, color):
        box = QWidget()
        box.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QVBoxLayout(box)
        value_label = QLabel(value)
        value_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: white;"
        )
        value_label.setAlignment(Qt.AlignCenter)
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 12px; color: white;")
        label_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        return box

    def update_stat_box(self, box, value):
        labels = box.findChildren(QLabel)
        if labels:
            labels[0].setText(value)

    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """

    def get_existing_codes(self, entity_type):
        return [item.get('code', '') for item in self.data.get(entity_type, [])]

    def refresh_all_tabs(self):
        self.refresh_universites_table()
        self.refresh_ufr_table()
        self.refresh_parcours_table()
        self.refresh_classes_table()
        self.tab_widget.setTabText(
            0, f"🏛️  Universités ({len(self.data['universites'])})"
        )
        self.tab_widget.setTabText(
            1, f"🎓  UFR ({len(self.data['ufrs'])})"
        )
        self.tab_widget.setTabText(
            2, f"📚  Parcours ({len(self.data['programmes'])})"
        )
        self.tab_widget.setTabText(
            3, f"👥  Classes ({len(self.data['cohortes'])})"
        )

    def update_statistics(self):
        self.update_stat_box(self.stat1, str(len(self.data["universites"])))
        self.update_stat_box(self.stat2, str(len(self.data["ufrs"])))
        self.update_stat_box(self.stat3, str(len(self.data["programmes"])))
        self.update_stat_box(self.stat4, str(len(self.data["cohortes"])))



class UniversiteDialog(QDialog):
    """Dialogue pour créer/modifier une université."""

    def __init__(self, parent=None, data=None, existing_codes=None):
        super().__init__(parent)
        self.data = data
        self.existing_codes = existing_codes or []
        self.setWindowTitle(
            "Nouvelle Université" if data is None else "Modifier Université"
        )
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel(
            "🏛️ " + (
                "Nouvelle Université" if self.data is None
                else "Modifier Université"
            )
        )
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Université Joseph KI-ZERBO")
        self.nom_input.setFixedHeight(40)
        form_layout.addRow("Nom *:", self.nom_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: UJK")
        self.code_input.setFixedHeight(40)
        form_layout.addRow("Code *:", self.code_input)

        self.ville_input = QLineEdit()
        self.ville_input.setPlaceholderText("Ex: Ouagadougou")
        self.ville_input.setFixedHeight(40)
        form_layout.addRow("Ville *:", self.ville_input)

        self.adresse_input = QLineEdit()
        self.adresse_input.setPlaceholderText("Ex: 03 BP 7021 Ouagadougou 03")
        self.adresse_input.setFixedHeight(40)
        form_layout.addRow("Adresse:", self.adresse_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(120, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #e0e0e0; color: #333;
                border: none; border-radius: 5px;
            }
            QPushButton:hover { background: #d0d0d0; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(150, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white;
                border: none; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        btn_save.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        if self.data:
            self.nom_input.setText(self.data.get('nom', ''))
            self.code_input.setText(self.data.get('code', ''))
            self.ville_input.setText(self.data.get('ville', ''))
            self.adresse_input.setText(self.data.get('adresse', ''))

    def validate_and_accept(self):
        nom = self.nom_input.text().strip()
        code = self.code_input.text().strip().upper()
        ville = self.ville_input.text().strip()

        if not nom or not code or not ville:
            QMessageBox.warning(
                self, "Champs requis",
                "Veuillez remplir tous les champs obligatoires (*)."
            )
            return

        if code in self.existing_codes:
            if not self.data or self.data.get('code') != code:
                QMessageBox.warning(
                    self, "Code existant",
                    f"Le code '{code}' est déjà utilisé."
                )
                return

        self.accept()

    def get_data(self):
        return {
            'nom': self.nom_input.text().strip(),
            'code': self.code_input.text().strip().upper(),
            'ville': self.ville_input.text().strip(),
            'adresse': self.adresse_input.text().strip()
        }


class UFRDialog(QDialog):
    def __init__(self, parent, universites, data=None, existing_codes=None):
        super().__init__(parent)
        self.parent_tab = parent
        self.universites = universites
        self.data = data or {}
        self.existing_codes = existing_codes or []
        self.edit_mode = data is not None
        self.setWindowTitle(
            "Modifier UFR" if self.edit_mode else "Nouvelle UFR"
        )
        self.setFixedSize(500, 450)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Modifier UFR" if self.edit_mode else "Nouvelle UFR")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(20)

        form = QFormLayout()
        form.setSpacing(15)

        self.univ_combo = QComboBox()
        self.univ_combo.addItems([u["nom"] for u in self.universites])
        self.univ_combo.setFixedHeight(40)
        if self.edit_mode and 'universite_id' in self.data:
            for i, u in enumerate(self.universites):
                if u.get('id') == self.data['universite_id']:
                    self.univ_combo.setCurrentIndex(i)
                    break
        form.addRow("Université *", self.univ_combo)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Sciences et Techniques")
        self.nom_input.setFixedHeight(40)
        if self.edit_mode:
            self.nom_input.setText(self.data.get('nom', ''))
        form.addRow("Nom *", self.nom_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: UFR-ST")
        self.code_input.setFixedHeight(40)
        if self.edit_mode:
            self.code_input.setText(self.data.get('code', ''))
        form.addRow("Code *", self.code_input)

        self.directeur_input = QLineEdit()
        self.directeur_input.setPlaceholderText("Nom du directeur")
        self.directeur_input.setFixedHeight(40)
        if self.edit_mode:
            self.directeur_input.setText(self.data.get('directeur', ''))
        form.addRow("Directeur", self.directeur_input)

        layout.addLayout(form)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #e0e0e0; color: #333;
                border: none; border-radius: 5px;
            }
            QPushButton:hover { background: #d0d0d0; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white;
                border: none; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def validate_and_accept(self):
        nom = self.nom_input.text().strip()
        code = self.code_input.text().strip().upper()

        if not nom or not code:
            QMessageBox.warning(
                self, "Champs obligatoires",
                "Le nom et le code sont obligatoires !"
            )
            return

        self.accept()

    def get_data(self):
        univ_nom = self.univ_combo.currentText()
        universite_id = next(
            (u.get('id') for u in self.universites if u['nom'] == univ_nom),
            None
        )
        result = {
            "nom": self.nom_input.text().strip(),
            "code": self.code_input.text().strip().upper(),
            "directeur": self.directeur_input.text().strip(),
            "universite_id": universite_id
        }
        if self.edit_mode and 'id' in self.data:
            result['id'] = self.data['id']
        return result


class ProgrammeDialog(QDialog):
    def __init__(self, parent, ufrs, data=None, existing_codes=None):
        super().__init__(parent)
        self.ufrs = ufrs
        self.data = data or {}
        self.existing_codes = existing_codes or []
        self.edit_mode = data is not None
        self.setWindowTitle(
            "Modifier Parcours" if self.edit_mode else "Nouveau Parcours"
        )
        self.setFixedSize(500, 500)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel(
            "Modifier Parcours" if self.edit_mode else "Nouveau Parcours"
        )
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(20)

        form = QFormLayout()
        form.setSpacing(15)

        self.ufr_combo = QComboBox()
        self.ufr_combo.addItems([u["nom"] for u in self.ufrs])
        self.ufr_combo.setFixedHeight(40)
        if self.edit_mode and 'ufr_id' in self.data:
            for i, u in enumerate(self.ufrs):
                if u.get('id') == self.data['ufr_id']:
                    self.ufr_combo.setCurrentIndex(i)
                    break
        form.addRow("UFR *", self.ufr_combo)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Informatique")
        self.nom_input.setFixedHeight(40)
        if self.edit_mode:
            self.nom_input.setText(self.data.get('nom', ''))
        form.addRow("Nom *", self.nom_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: INFO")
        self.code_input.setFixedHeight(40)
        if self.edit_mode:
            self.code_input.setText(self.data.get('code', ''))
        form.addRow("Code *", self.code_input)

        self.niveau_combo = QComboBox()
        self.niveau_combo.addItems([
            "Licence 1", "Licence 2", "Licence 3",
            "Master 1", "Master 2", "Doctorat"
        ])
        self.niveau_combo.setFixedHeight(40)
        if self.edit_mode:
            self.niveau_combo.setCurrentText(self.data.get('niveau', 'Licence 1'))
        form.addRow("Niveau *", self.niveau_combo)

        self.duree_input = QSpinBox()
        self.duree_input.setRange(1, 10)
        self.duree_input.setValue(
            self.data.get('duree_annees', 3) if self.edit_mode else 3
        )
        self.duree_input.setFixedHeight(40)
        form.addRow("Durée (années)", self.duree_input)

        layout.addLayout(form)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #e0e0e0; color: #333;
                border: none; border-radius: 5px;
            }
            QPushButton:hover { background: #d0d0d0; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white;
                border: none; border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def validate_and_accept(self):
        nom = self.nom_input.text().strip()
        code = self.code_input.text().strip().upper()

        if not nom or not code:
            QMessageBox.warning(
                self, "Champs obligatoires",
                "Le nom et le code sont obligatoires !"
            )
            return

        if code in self.existing_codes:
            QMessageBox.critical(
                self, "Code existant",
                f"Le code '{code}' est déjà utilisé."
            )
            return

        self.accept()

    def get_data(self):
        ufr_nom = self.ufr_combo.currentText()
        ufr_id = next(
            (u.get('id') for u in self.ufrs if u['nom'] == ufr_nom),
            None
        )
        result = {
            "nom": self.nom_input.text().strip(),
            "code": self.code_input.text().strip().upper(),
            "niveau": self.niveau_combo.currentText(),
            "ufr_id": ufr_id,
            "duree_annees": self.duree_input.value()
        }
        if self.edit_mode and 'id' in self.data:
            result['id'] = self.data['id']
        return result


class CohorteDialog(QDialog):
    """Dialogue pour créer/modifier une classe avec semestres dynamiques."""

    # Mapping niveau → semestres disponibles
    SEMESTRES_PAR_NIVEAU = {
        "Licence 1":  ["Semestre 1", "Semestre 2"],
        "Licence 2":  ["Semestre 3", "Semestre 4"],
        "Licence 3":  ["Semestre 5", "Semestre 6"],
        "Master 1":   ["M1",         "M2"],
        "Master 2":   ["M3",         "M4"],
        "Doctorat":   ["Doctorat 1", "Doctorat 2", "Doctorat 3"],
    }

    # Mapping semestre texte → entier pour la DB (sans contrainte 1-2)
    SEMESTRE_TO_INT = {
        "Semestre 1": 1,  "Semestre 2": 2,
        "Semestre 3": 3,  "Semestre 4": 4,
        "Semestre 5": 5,  "Semestre 6": 6,
        "M1": 7,          "M2": 8,
        "M3": 9,          "M4": 10,
        "Doctorat 1": 11, "Doctorat 2": 12, "Doctorat 3": 13,
    }
    INT_TO_SEMESTRE = {v: k for k, v in SEMESTRE_TO_INT.items()}

    def __init__(self, parent, programmes, data=None):
        super().__init__(parent)
        self.programmes = programmes
        self.data = data or {}
        self.edit_mode = data is not None
        self.setWindowTitle(
            "Modifier Classe" if self.edit_mode else "Nouvelle Classe"
        )
        self.setMinimumWidth(520)
        self.setMinimumHeight(600)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(5)

        # Titre
        title = QLabel(
            "✏️ Modifier Classe" if self.edit_mode else "➕ Nouvelle Classe"
        )
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(sep)
        layout.addSpacing(10)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight)

        # ── Parcours ──────────────────────────────
        self.prog_combo = QComboBox()
        prog_labels = [
            f"{p['nom']} ({p['niveau']})" for p in self.programmes
        ]
        self.prog_combo.addItems(prog_labels)
        self.prog_combo.setFixedHeight(40)
        self.prog_combo.setStyleSheet(self._combo_style())

        # Pré-sélection en mode édition
        if self.edit_mode and 'programme_id' in self.data:
            for i, p in enumerate(self.programmes):
                if p.get('id') == self.data['programme_id']:
                    self.prog_combo.setCurrentIndex(i)
                    break

        # Quand le parcours change → mettre à jour les semestres
        self.prog_combo.currentIndexChanged.connect(self._update_semestres)
        form.addRow("Parcours *", self.prog_combo)

        # ── Nom de la classe ──────────────────────
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: L3 INFO A")
        self.nom_input.setFixedHeight(40)
        self.nom_input.setStyleSheet(self._input_style())
        if self.edit_mode:
            self.nom_input.setText(self.data.get('nom', ''))
        form.addRow("Nom *", self.nom_input)

        # ── Année académique ──────────────────────
        self.annee_input = QLineEdit()
        self.annee_input.setPlaceholderText("Ex: 2025-2026")
        self.annee_input.setFixedHeight(40)
        self.annee_input.setStyleSheet(self._input_style())
        if self.edit_mode:
            self.annee_input.setText(self.data.get('annee_academique', ''))
        form.addRow("Année académique *", self.annee_input)

        # ── Semestre (dynamique) ──────────────────
        self.semestre_combo = QComboBox()
        self.semestre_combo.setFixedHeight(40)
        self.semestre_combo.setStyleSheet(self._combo_style())
        # Remplir selon le parcours sélectionné
        self._update_semestres()
        # Restaurer le semestre en mode édition
        if self.edit_mode and self.data.get('semestre'):
            idx = self.semestre_combo.findText(self.data['semestre'])
            if idx >= 0:
                self.semestre_combo.setCurrentIndex(idx)
        form.addRow("Semestre *", self.semestre_combo)

        # ── Date de début ────────────────────────
        self.date_debut_input = QLineEdit()
        self.date_debut_input.setPlaceholderText("Ex: 06/10/2025")
        self.date_debut_input.setFixedHeight(40)
        self.date_debut_input.setStyleSheet(self._input_style())
        if self.edit_mode:
            self.date_debut_input.setText(self.data.get('date_debut', ''))
        form.addRow("Date de début *", self.date_debut_input)

        # ── Date de fin ──────────────────────────
        self.date_fin_input = QLineEdit()
        self.date_fin_input.setPlaceholderText("Ex: 28/02/2026")
        self.date_fin_input.setFixedHeight(40)
        self.date_fin_input.setStyleSheet(self._input_style())
        if self.edit_mode:
            self.date_fin_input.setText(self.data.get('date_fin', ''))
        form.addRow("Date de fin *", self.date_fin_input)

        # ── Effectif ─────────────────────────────
        self.effectif_input = QSpinBox()
        self.effectif_input.setRange(1, 1000)
        self.effectif_input.setValue(
            self.data.get('effectif', 45) if self.edit_mode else 45
        )
        self.effectif_input.setFixedHeight(40)
        self.effectif_input.setStyleSheet(self._input_style())
        form.addRow("Effectif *", self.effectif_input)

        layout.addLayout(form)
        layout.addStretch()

        # ── Boutons ───────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 42)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #e0e0e0; color: #333;
                border: none; border-radius: 6px; font-size: 14px;
            }
            QPushButton:hover { background: #d0d0d0; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 42)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #4CAF50; color: white;
                border: none; border-radius: 6px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    # ── Mise à jour dynamique des semestres ───────
    def _update_semestres(self):
        """Met à jour la liste des semestres selon le niveau du parcours."""
        current_semestre = self.semestre_combo.currentText()
        self.semestre_combo.clear()

        # Récupérer le niveau du parcours sélectionné
        idx = self.prog_combo.currentIndex()
        niveau = ""
        if 0 <= idx < len(self.programmes):
            niveau = self.programmes[idx].get('niveau', '')

        # Charger les semestres correspondants
        semestres = self.SEMESTRES_PAR_NIVEAU.get(niveau, ["Semestre 1", "Semestre 2"])
        self.semestre_combo.addItems(semestres)

        # Restaurer la sélection précédente si possible
        restore_idx = self.semestre_combo.findText(current_semestre)
        if restore_idx >= 0:
            self.semestre_combo.setCurrentIndex(restore_idx)

    # ── Validation ────────────────────────────────
    def validate_and_accept(self):
        nom        = self.nom_input.text().strip()
        annee      = self.annee_input.text().strip()
        date_debut = self.date_debut_input.text().strip()
        date_fin   = self.date_fin_input.text().strip()

        if not nom or not annee or not date_debut or not date_fin:
            QMessageBox.warning(
                self, "Champs obligatoires",
                "Veuillez remplir tous les champs obligatoires (*) !"
            )
            return

        self.accept()

    # ── Données retournées ────────────────────────
    def get_data(self):
        prog_label = self.prog_combo.currentText()
        programme_id = next(
            (
                p.get('id') for p in self.programmes
                if f"{p['nom']} ({p['niveau']})" == prog_label
            ),
            None
        )
        result = {
            "nom":              self.nom_input.text().strip(),
            "annee_academique": self.annee_input.text().strip(),
            "semestre":         self.semestre_combo.currentText(),
            "date_debut":       self.date_debut_input.text().strip(),
            "date_fin":         self.date_fin_input.text().strip(),
            "programme_id":     programme_id,
            "effectif":         self.effectif_input.value()
        }
        if self.edit_mode and 'id' in self.data:
            result['id'] = self.data['id']
        return result

    # ── Styles ────────────────────────────────────
    def _input_style(self):
        return """
            QLineEdit, QSpinBox {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 13px;
                background: white;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #3498db;
            }
        """

    def _combo_style(self):
        return """
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 13px;
                background: white;
            }
            QComboBox:focus { border: 1px solid #3498db; }
            QComboBox::drop-down { border: none; }
        """

"""
Onglet de gestion des enseignants - VERSION CORRIGÉE
Toutes les fonctionnalités sont maintenant connectées
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QFileDialog
)
from PyQt5.QtCore import Qt

from datetime import datetime
import json
from src.data.data_manager import DataManager