"""
UC6 - Onglet d'Ordonnancement P-équitable (Pfair)
Connexion SQLite réelle pour cohortes, activités et créneaux.
"""
import json
import time
from datetime import date, timedelta, datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox,
    QProgressBar, QDialog, QTabWidget, QTextEdit, QMessageBox,
    QDateEdit, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QColor

from src.database.db_manager import db_manager
from src.database.repositories.cohort_repository import CohortRepository
from src.database.repositories.activity_repository import ActivityRepository
from src.database.repositories.teacher_repository import TeacherRepository


# ══════════════════════════════════════════════════════════════════
# THREAD D'ORDONNANCEMENT PFAIR
# ══════════════════════════════════════════════════════════════════

class PfairSchedulerThread(QThread):
    """Thread non bloquant pour l'algorithme d'ordonnancement P-équitable."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, cohort_id, start_date, end_date, available_rooms=None, parent=None):
        super().__init__(parent)
        self.cohort_id = cohort_id
        self.start_date = start_date
        self.end_date = end_date
        self.available_rooms = available_rooms or []

    def run(self):
        try:
            session = db_manager.get_session()
            activity_repo = ActivityRepository(session)
            cohort_repo = CohortRepository(session)
            teacher_repo = TeacherRepository(session)

            self.progress.emit(5, "Chargement de la cohorte...")
            cohort = cohort_repo.get_by_id(self.cohort_id)
            if not cohort:
                self.error.emit("Cohorte introuvable.")
                return

            self.progress.emit(15, "Chargement des activités...")
            activities = activity_repo.get_by_cohort(self.cohort_id)
            if not activities:
                self.error.emit("Aucune activité trouvée pour cette cohorte.")
                return

            # Calcul de D_effectif (jours ouvrables)
            self.progress.emit(25, "Calcul des jours ouvrables...")
            d_effective = self._calc_effective_days(self.start_date, self.end_date)
            if d_effective <= 0:
                self.error.emit("Aucun jour ouvrable dans la période sélectionnée.")
                return

            # Calcul de la charge totale U = Σ Ui où Ui = (Ci - hi) / D
            self.progress.emit(35, "Vérification de l'ordonnançabilité (ΣU ≤ m)...")
            total_charge = 0.0
            activities_data = []
            print(f"[DEBUG] {len(activities)} activité(s) trouvée(s) pour la cohorte")
            for act in activities:
                # heures déjà faites et volume total
                hours_done_db = float(act.hours_done or 0.0)
                volume        = float(act.volume_hours or 0.0)
                charge_factor = float(act.charge_factor or 0.0)
                remaining     = volume - hours_done_db  # heures RESTANTES à planifier

                print(f"[DEBUG] Activité [{act.id}] '{act.name}' | vol={volume}h | done={hours_done_db}h | remaining={remaining}h | charge_factor={charge_factor} | teacher_id={act.teacher_id}")

                if remaining > 0:
                    Ui = remaining / d_effective if charge_factor == 0 else charge_factor
                    total_charge += Ui
                    activities_data.append({
                        'activity':    act,
                        'Ui':          Ui,
                        'remaining':   remaining,
                        # ✅ FIX CRITIQUE : Pfair repart de 0 pour la période
                        # On planifie les 'remaining' heures, h_done_local commence à 0
                        'hours_done':  0.0,
                        'volume':      remaining,  # volume à planifier = restant
                    })
                else:
                    print(f"[DEBUG]   → IGNORÉE (remaining={remaining} <= 0)")
            print(f"[DEBUG] activities_data contient {len(activities_data)} activité(s) planifiable(s)")
            print(f"[DEBUG] d_effective={d_effective} jours | total_charge={total_charge:.4f}")

            schedulable = total_charge <= 1.0

            # Algorithme Pfair : α(τi, t) = (Ui×t - H_réalisé) / Ui
            self.progress.emit(50, "Exécution de l'algorithme Pfair...")
            scheduled_slots = []
            conflicts = []
            activities_snapshot = {}

            t = 0
            current_date = self.start_date

            while current_date <= self.end_date:
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue

                t += 1
                progress_val = 50 + int((t / max(d_effective, 1)) * 40)
                self.progress.emit(min(progress_val, 90), f"Planification du {current_date.strftime('%d/%m/%Y')}...")

                urgent = []
                for item in activities_data:
                    act    = item['activity']
                    Ui     = item['Ui']
                    volume = item['volume']
                    h_done = item['hours_done']
                    if Ui <= 0 or h_done >= volume:
                        continue
                    H_ideal = Ui * t
                    delay   = H_ideal - h_done
                    alpha   = delay / Ui
                    if alpha >= 0:
                        urgent.append((act, alpha, delay, Ui))

                # Trier par α décroissant
                urgent.sort(key=lambda x: x[1], reverse=True)

                start_hour = 8
                slot_duration = 4

                for act, alpha, delay, Ui in urgent:
                    if start_hour >= 17:
                        break
                    teacher = teacher_repo.get_by_id(act.teacher_id) if act.teacher_id else None
                    # AMELIORATION 1: Salle compatible + pas de conflit inter-cohortes
                    room = "Salle TBD"
                    act_type_val = str(getattr(getattr(act, 'type', None), 'value', None) or '').lower()
                    type_map = {
                        'magistral': ['AMPHI', 'TD'], 'dirige': ['TD', 'AMPHI'],
                        'pratique': ['TP', 'LABO', 'INFORMATIQUE'],
                        'td': ['TD', 'AMPHI'], 'tp': ['TP', 'LABO', 'INFORMATIQUE'],
                        'cm': ['AMPHI', 'TD'],
                    }
                    preferred = next((v for k,v in type_map.items() if k in act_type_val), None)
                    slot_start_str = f"{start_hour:02d}:00:00.000000"
                    current_date_str = str(current_date)
                    if self.available_rooms:
                        from src.database.db_manager import db_manager as _dm
                        from sqlalchemy import text as _t
                        _s = _dm.get_session()
                        # Salles occupees a ce creneau (toutes cohortes)
                        occupied = set(r[0] for r in _s.execute(_t(
                            "SELECT room FROM schedule_slots WHERE date=:d AND start_time=:st AND room IS NOT NULL"
                        ), {'d': current_date_str, 'st': slot_start_str}).fetchall())
                        free_rooms = [r for r in self.available_rooms if r not in occupied]
                        if free_rooms:
                            # Choisir salle compatible avec type activite
                            if preferred:
                                from src.database.db_manager import db_manager as _dm2
                                from sqlalchemy import text as _t2
                                _s2 = _dm2.get_session()
                                for ptype in preferred:
                                    names = tuple(free_rooms) if len(free_rooms)>1 else (free_rooms[0], free_rooms[0])
                                    placeholders = ','.join([f':n{i}' for i in range(len(free_rooms))])
                                    params = {'rt': ptype}
                                    for i,n in enumerate(free_rooms): params[f'n{i}'] = n
                                    rows = _s2.execute(_t2(
                                        f"SELECT name FROM rooms WHERE room_type=:rt AND is_active=1 AND name IN ({placeholders})"
                                    ), params).fetchall()
                                    if rows:
                                        room = rows[0][0]; break
                            if room == "Salle TBD" and free_rooms:
                                room = free_rooms[0]
                        else:
                            # Aucune salle libre -> conflit
                            conflicts.append({'date': current_date, 'activity': act.name,
                                'reason': f'Aucune salle libre a {start_hour}h'})
                            continue

                    # Convertir ActivityTypeEnum en string
                    act_type_str = act.type
                    if hasattr(act_type_str, 'value'):
                        act_type_str = act_type_str.value
                    elif hasattr(act_type_str, 'name'):
                        act_type_str = act_type_str.name
                    act_type_str = str(act_type_str or '').split('.')[-1]

                    slot_info = {
                        'date': current_date,  # objet date Python
                        'start': f"{start_hour:02d}:00",
                        'end': f"{start_hour + slot_duration:02d}:00",
                        'activity': act.name,
                        'activity_code': act.code,
                        'activity_type': act_type_str,
                        'teacher': teacher.full_name if teacher else "Non assigné",
                        'cohort': cohort.name,
                        'room': room,
                        'alpha': round(alpha, 3),
                        'delay': round(delay, 2),
                        'cohort_id': self.cohort_id,
                        'activity_id': act.id,
                        'teacher_id': act.teacher_id,  # ✅ nécessaire pour SQLite
                    }
                    scheduled_slots.append(slot_info)
                            # ✅ mise à jour de la copie locale via act_id
                    for _item in activities_data:
                        if _item['activity'].id == act.id:
                            _item['hours_done'] += slot_duration
                            break
                    start_hour += slot_duration

                    if act.code not in activities_snapshot:
                        urgence = 'critique' if alpha >= 1.0 else ('urgente' if alpha >= 0.5 else 'ok')
                        activities_snapshot[act.code] = {
                            'nom': act.name,
                            'code': act.code,
                            'type': act.type,
                            'volume_total': act.volume_hours,
                            'heures_realisees': h_done,
                            'alpha': round(alpha, 3),
                            'urgence': urgence,
                            'enseignant': teacher.full_name if teacher else "Non assigné",
                        }
                    else:
                        activities_snapshot[act.code]['heures_realisees'] = h_done

                current_date += timedelta(days=1)

            # Sauvegarder dans data/schedules.json
            self.progress.emit(93, "Sauvegarde de l'emploi du temps...")
            self._save_schedules(scheduled_slots, cohort)

            self.progress.emit(100, "Ordonnancement terminé !")

            results = {
                'success': True,
                'cohort_name': cohort.name,
                'period': f"{self.start_date.strftime('%d/%m/%Y')} au {self.end_date.strftime('%d/%m/%Y')}",
                'total_activities': len(activities),
                'scheduled_slots': len(scheduled_slots),
                'total_hours': len(scheduled_slots) * 2,
                'total_charge': round(total_charge, 4),
                'effective_days': d_effective,
                'schedulable': schedulable,
                'conflicts': len(conflicts),
                'activities': list(activities_snapshot.values()),
                'slots': scheduled_slots,
            }
            self.finished.emit(results)

        except Exception as e:
            import traceback
            self.error.emit(f"Erreur : {str(e)}\n{traceback.format_exc()}")

    def _calc_effective_days(self, start, end):
        count = 0
        d = start
        while d <= end:
            if d.weekday() < 5:
                count += 1
            d += timedelta(days=1)
        return count

    def _save_schedules(self, slots, cohort):
        """Sauvegarde les créneaux dans SQLite (schedule_slots) ET schedules.json."""
        # ─── 1. SAUVEGARDE SQLite ─────────────────────────────────────────────
        nb_inserts = 0
        print(f"[DEBUG] Tentative insertion de {len(slots)} créneau(x) dans schedule_slots")
        try:
            from datetime import time as dtime
            from src.database.models import ScheduleSlotModel

            session = db_manager.get_session()

            # Supprimer les anciens créneaux de cette cohorte pour cette période
            if slots:
                # Déterminer la plage de dates des nouveaux créneaux
                all_dates = [s['date'] for s in slots]
                min_date  = min(all_dates)
                max_date  = max(all_dates)
                session.query(ScheduleSlotModel).filter(
                    ScheduleSlotModel.cohort_id == cohort.id,
                    ScheduleSlotModel.date >= min_date,
                    ScheduleSlotModel.date <= max_date,
                ).delete(synchronize_session=False)

            for s in slots:
                # teacher_id est NOT NULL dans schedule_slots → skip si absent
                if not s.get('teacher_id'):
                    print(f"[scheduling_tab] Créneau ignoré (teacher_id manquant): {s.get('activity','?')} le {s.get('date')}")
                    continue
                if not s.get('activity_id'):
                    continue
                try:
                    start_h, start_m = map(int, s['start'].split(':'))
                    end_h,   end_m   = map(int, s['end'].split(':'))
                    # ✅ FIX : garantir que date est un objet Python date
                    raw_date = s['date']
                    if isinstance(raw_date, str):
                        from datetime import datetime as _dt
                        raw_date = _dt.fromisoformat(raw_date).date()
                    elif hasattr(raw_date, 'toPyDate'):
                        raw_date = raw_date.toPyDate()
                    slot = ScheduleSlotModel(
                        date        = raw_date,
                        start_time  = dtime(start_h, start_m),
                        end_time    = dtime(end_h,   end_m),
                        room        = s.get('room', 'Salle TBD'),
                        activity_id = s['activity_id'],
                        teacher_id  = s['teacher_id'],
                        cohort_id   = s.get('cohort_id', cohort.id),
                        delay_value = s.get('delay', 0.0),
                        notes       = f"alpha={s.get('alpha', 0.0)} type={str(s.get('activity_type','') or '').split('.')[-1]}",
                    )
                    session.add(slot)
                    nb_inserts += 1
                except Exception as e_slot:
                    print(f"[scheduling_tab] Erreur insertion slot {s.get('date')}: {e_slot}")

            session.commit()
            print(f"[scheduling_tab] ✅ {nb_inserts} créneaux insérés dans schedule_slots")

        except Exception as e:
            print(f"[scheduling_tab] ❌ Erreur sauvegarde SQLite: {e}")
            import traceback; traceback.print_exc()

        # ─── 2. SAUVEGARDE JSON (backup) ─────────────────────────────────────
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            path = data_dir / "schedules.json"
            existing = {}
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            # Convertir les dates en string pour le JSON
            slots_json = []
            for s in slots:
                s2 = dict(s)
                if hasattr(s2.get('date'), 'isoformat'):
                    s2['date'] = s2['date'].isoformat()
                slots_json.append(s2)
            existing[cohort.name] = {
                'cohort_id':    cohort.id,
                'cohort_name':  cohort.name,
                'generated_at': datetime.now().isoformat(),
                'nb_slots':     nb_inserts,
                'slots':        slots_json,
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"[scheduling_tab] Sauvegarde schedules.json échouée: {e}")


# ══════════════════════════════════════════════════════════════════
# DIALOG RÉSULTATS
# ══════════════════════════════════════════════════════════════════

class ResultsDialog(QDialog):
    """Fenêtre de résultats avec 3 onglets : Résumé, Activités, Statistiques."""

    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.results = results
        self.setWindowTitle("📊 Résultats de l'Ordonnancement Pfair")
        self.setMinimumSize(900, 600)
        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel(f"✅ Ordonnancement — {self.results.get('cohort_name', '')}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a73e8;")
        layout.addWidget(title)

        subtitle = QLabel(f"Période : {self.results.get('period', '')}")
        subtitle.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._build_summary_tab(), "📋 Résumé")
        tabs.addTab(self._build_activities_tab(), "📚 Activités")
        tabs.addTab(self._build_stats_tab(), "📈 Statistiques")
        layout.addWidget(tabs)

        btn = QPushButton("Fermer")
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton { background-color: #1a73e8; color: white;
                border-radius: 6px; font-size: 14px; }
            QPushButton:hover { background-color: #1558b0; }
        """)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)

    def _build_summary_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 15, 15, 15)

        r = self.results
        schedulable = r.get('schedulable', False)
        status_txt = (
            f"✅ ORDONNANÇABLE  (ΣU = {r.get('total_charge', 0):.4f} ≤ 1)"
            if schedulable
            else f"⚠️ CHARGE ÉLEVÉE  (ΣU = {r.get('total_charge', 0):.4f} > 1)"
        )
        status_lbl = QLabel(status_txt)
        status_lbl.setStyleSheet(
            f"font-size: 14px; font-weight: bold; padding: 10px; border-radius: 6px;"
            f"color: {'#2e7d32' if schedulable else '#c62828'};"
            f"background-color: {'#e8f5e9' if schedulable else '#ffebee'};"
        )
        layout.addWidget(status_lbl)

        form = QFormLayout()
        form.setSpacing(8)
        for lbl, val in [
            ("🎓 Cohorte", r.get('cohort_name', '-')),
            ("📅 Période", r.get('period', '-')),
            ("📚 Activités", str(r.get('total_activities', 0))),
            ("🗓️ Créneaux planifiés", str(r.get('scheduled_slots', 0))),
            ("⏱️ Heures planifiées", f"{r.get('total_hours', 0)} h"),
            ("📊 Charge totale ΣU", f"{r.get('total_charge', 0):.4f}"),
            ("📅 Jours effectifs", str(r.get('effective_days', 0))),
            ("⚠️ Conflits", str(r.get('conflicts', 0))),
        ]:
            form.addRow(QLabel(f"<b>{lbl} :</b>"), QLabel(val))

        layout.addLayout(form)
        layout.addStretch()
        return w

    def _build_activities_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        activities = self.results.get('activities', [])

        table = QTableWidget(len(activities), 7)
        table.setHorizontalHeaderLabels(
            ["Activité", "Code", "Type", "Vol. total (h)", "Réalisé (h)", "α", "Urgence"]
        )
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, act in enumerate(activities):
            table.setItem(row, 0, QTableWidgetItem(act.get('nom', '')))
            table.setItem(row, 1, QTableWidgetItem(act.get('code', '')))
            table.setItem(row, 2, QTableWidgetItem(str(act.get('type', '') or '').split('.')[-1]))
            table.setItem(row, 3, QTableWidgetItem(str(act.get('volume_total', 0))))
            table.setItem(row, 4, QTableWidgetItem(f"{act.get('heures_realisees', 0):.1f}"))
            table.setItem(row, 5, QTableWidgetItem(f"{act.get('alpha', 0):.3f}"))
            u = act.get('urgence', 'ok')
            itm = QTableWidgetItem(u.upper())
            if u == 'critique':
                itm.setBackground(QColor('#FFCDD2'))
                itm.setForeground(QColor('#C62828'))
            elif u == 'urgente':
                itm.setBackground(QColor('#FFF9C4'))
                itm.setForeground(QColor('#F57F17'))
            else:
                itm.setBackground(QColor('#C8E6C9'))
                itm.setForeground(QColor('#2E7D32'))
            table.setItem(row, 6, itm)

        layout.addWidget(table)
        return w

    def _build_stats_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        acts = self.results.get('activities', [])
        total = len(acts)
        critiques = sum(1 for a in acts if a.get('urgence') == 'critique')
        urgentes = sum(1 for a in acts if a.get('urgence') == 'urgente')
        ok = total - critiques - urgentes
        total_vol = sum(a.get('volume_total', 0) for a in acts)
        total_real = sum(a.get('heures_realisees', 0) for a in acts)
        completion = (total_real / total_vol * 100) if total_vol > 0 else 0
        alpha_moy = sum(a.get('alpha', 0) for a in acts) / max(total, 1)

        r = self.results
        text = QTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")
        text.setPlainText(f"""
STATISTIQUES D'ORDONNANCEMENT PFAIR
══════════════════════════════════════════

Cohorte  : {r.get('cohort_name', '-')}
Période  : {r.get('period', '-')}

ACTIVITÉS
────────────────────────────────────
  Total         : {total}
  🔴 Critiques  : {critiques}  (α ≥ 1.0)
  🟡 Urgentes   : {urgentes}  (0.5 ≤ α < 1.0)
  🟢 OK         : {ok}  (α < 0.5)

VOLUME HORAIRE
────────────────────────────────────
  Volume total     : {total_vol:.1f} h
  Heures réalisées : {total_real:.1f} h
  Taux completion  : {completion:.1f} %

ALGORITHME PFAIR
────────────────────────────────────
  Charge totale ΣU   : {r.get('total_charge', 0):.4f}
  Jours effectifs D  : {r.get('effective_days', 0)}
  α moyen            : {alpha_moy:.3f}
  Créneaux planifiés : {r.get('scheduled_slots', 0)}
  Heures planifiées  : {r.get('total_hours', 0)} h
  Conflits           : {r.get('conflicts', 0)}
  Ordonnançable      : {'OUI ✅' if r.get('schedulable') else 'NON ⚠️'}
""")
        layout.addWidget(text)
        return w


# ══════════════════════════════════════════════════════════════════
# ONGLET PRINCIPAL UC6
# ══════════════════════════════════════════════════════════════════

class SchedulingTab(QWidget):
    """UC6 — Ordonnancement P-équitable des activités académiques."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._init_ui()
        self._load_cohorts()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titre
        title = QLabel("⚙️ Ordonnancement P-équitable (Pfair)")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("Formule : H_ideal(t) = Ui × t  |  α(τi, t) = (H_ideal − H_réalisé) / Ui")
        subtitle.setStyleSheet("color: #555; font-size: 12px; font-style: italic;")
        layout.addWidget(subtitle)

        # Configuration
        config_group = QGroupBox("Configuration de l'ordonnancement")
        config_group.setStyleSheet("""
            QGroupBox { font-weight: bold; border: 1px solid #ddd;
                border-radius: 8px; padding-top: 10px; }
            QGroupBox::title { padding: 0 8px; color: #333; }
        """)
        form = QFormLayout(config_group)
        form.setSpacing(12)

        self.cohort_combo = QComboBox()
        self.cohort_combo.setFixedHeight(40)
        self.cohort_combo.setStyleSheet(self._fstyle())
        form.addRow("Cohorte * :", self.cohort_combo)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setFixedHeight(40)
        self.start_date_edit.setStyleSheet(self._fstyle())
        form.addRow("Date de début * :", self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.end_date_edit.setDate(QDate.currentDate().addMonths(6))
        self.end_date_edit.setFixedHeight(40)
        self.end_date_edit.setStyleSheet(self._fstyle())
        form.addRow("Date de fin * :", self.end_date_edit)

        self.rooms_input = QLineEdit()
        self.rooms_input.setPlaceholderText("Ex : A101, A102, B201  (séparées par des virgules)")
        self.rooms_input.setFixedHeight(40)
        self.rooms_input.setStyleSheet(self._fstyle())
        form.addRow("Salles disponibles :", self.rooms_input)

        layout.addWidget(config_group)

        # Bouton
        self.run_btn = QPushButton("🚀  Lancer l'ordonnancement")
        self.run_btn.setFixedHeight(48)
        self.run_btn.setStyleSheet("""
            QPushButton { background-color: #1a73e8; color: white;
                border-radius: 8px; font-size: 15px; font-weight: bold; }
            QPushButton:hover { background-color: #1558b0; }
            QPushButton:disabled { background-color: #aaa; }
        """)
        self.run_btn.clicked.connect(self._start_scheduling)
        layout.addWidget(self.run_btn)

        # Progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(22)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border-radius: 4px; background: #f0f0f0; text-align: center; }
            QProgressBar::chunk { background-color: #1a73e8; border-radius: 4px; }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #555; font-size: 12px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _fstyle(self):
        return ("border: 1px solid #D1D5DB; border-radius: 6px; "
                "padding: 8px 12px; font-size: 13px;")

    def _load_cohorts(self):
        try:
            session = db_manager.get_session()
            cohorts = CohortRepository(session).get_all()
            self.cohort_combo.clear()
            if cohorts:
                for c in cohorts:
                    self.cohort_combo.addItem(
                        f"{c.name}  ({c.academic_year}, S{c.semester})",
                        userData=c.id
                    )
            else:
                self.cohort_combo.addItem("⚠️ Aucune cohorte — créez-en via Structure", userData=None)
        except Exception as e:
            self.cohort_combo.addItem(f"Erreur: {str(e)[:40]}", userData=None)

    def _start_scheduling(self):
        cohort_id = self.cohort_combo.currentData()
        if not cohort_id:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une cohorte valide.")
            return

        sd = self.start_date_edit.date()
        ed = self.end_date_edit.date()
        start = date(sd.year(), sd.month(), sd.day())
        end = date(ed.year(), ed.month(), ed.day())
        if end <= start:
            QMessageBox.warning(self, "Dates invalides", "La date de fin doit être postérieure à la date de début.")
            return

        rooms_txt = self.rooms_input.text().strip()
        rooms = [r.strip() for r in rooms_txt.split(',') if r.strip()]

        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)

        self._thread = PfairSchedulerThread(cohort_id, start, end, rooms)
        self._thread.progress.connect(self._on_progress)
        self._thread.finished.connect(self._on_finished)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def _on_finished(self, results):
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        ResultsDialog(results, self).exec_()

    def _on_error(self, message):
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        QMessageBox.critical(self, "Erreur d'ordonnancement", message)

    def refresh_data(self):
        self._load_cohorts()