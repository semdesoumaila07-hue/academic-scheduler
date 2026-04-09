"""
UC6 - Onglet d'Ordonnancement P-équitable (Pfair)

CORRECTIONS apportées :
1. Ui = volume / d_effective TOUJOURS (ne plus utiliser l'ancien charge_factor).
   Bug : charge_factor != 0 en base → utilisait l'ancienne valeur → ΣU faux.
2. Rotation des salles : chaque activité reçoit une salle différente à chaque
   créneau, en tournant dans la liste des salles disponibles.
3. Suppression TOTALE des anciens créneaux avant génération.
4. Remise à zéro de hours_done et charge_factor avant génération.
5. Créneaux 08h-12h et 14h-18h uniquement (Burkina Faso).
6. Bouton Aide (?) fonctionnel avec explication de l'algorithme.
"""
import json
from datetime import date, timedelta, datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox,
    QProgressBar, QDialog, QTabWidget, QTextEdit, QMessageBox,
    QDateEdit, QGroupBox, QFormLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QColor

from src.database.db_manager import db_manager
from src.database.repositories.cohort_repository import CohortRepository
from src.database.repositories.activity_repository import ActivityRepository
from src.database.repositories.teacher_repository import TeacherRepository


CRENEAUX_AUTORISES = [
    (8,  12),   # Matin       08h00 → 12h00
    (14, 18),   # Après-midi  14h00 → 18h00
]


# ══════════════════════════════════════════════════════════════════
# DIALOGUE D'AIDE — Explication de l'algorithme Pfair
# ══════════════════════════════════════════════════════════════════

class HelpDialog(QDialog):
    """Explication du fonctionnement de l'algorithme Pfair."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("❓ Aide — Ordonnancement P-équitable (Pfair)")
        self.setMinimumSize(700, 550)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("📖 Comment fonctionne l'ordonnancement Pfair ?")
        title.setStyleSheet("font-size:16px; font-weight:bold; color:#1a73e8;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")

        content = QWidget()
        clayout = QVBoxLayout(content)
        clayout.setSpacing(12)

        sections = [
            ("🎯 Principe général",
             "L'algorithme Pfair (Proportionate Fair) garantit que chaque activité "
             "reçoit des créneaux proportionnellement à son importance (volume horaire).\n\n"
             "Chaque activité τᵢ a un facteur de charge Uᵢ = Cᵢ / D_effectif où :\n"
             "  • Cᵢ = volume horaire total de l'activité\n"
             "  • D_effectif = nombre de jours ouvrables dans la période"),

            ("📊 Condition d'ordonnançabilité",
             "Le système est ordonnançable si et seulement si :\n\n"
             "  ΣU = Σ(Cᵢ / D_effectif) ≤ 1.0\n\n"
             "Si ΣU > 1.0, il y a trop d'heures à planifier pour le nombre "
             "de jours disponibles. Solutions :\n"
             "  • Augmenter la période (reculer la date de fin)\n"
             "  • Réduire le volume horaire de certaines activités"),

            ("⚡ Calcul de l'urgence α",
             "À chaque jour t, l'algorithme calcule pour chaque activité :\n\n"
             "  H_idéal(t) = Uᵢ × t   (heures théoriquement dues)\n"
             "  retard = H_idéal - H_réalisé\n"
             "  α = retard / Uᵢ\n\n"
             "  • α ≥ 1.0 → Activité CRITIQUE (retard important)\n"
             "  • 0.5 ≤ α < 1.0 → Activité URGENTE\n"
             "  • α < 0.5 → Activité OK (en avance ou à jour)"),

            ("🕐 Créneaux horaires (Burkina Faso)",
             "Les cours sont planifiés uniquement sur :\n"
             "  • Matin      : 08h00 → 12h00 (4 heures)\n"
             "  • Après-midi : 14h00 → 18h00 (4 heures)\n\n"
             "La pause déjeuner 12h-14h est automatiquement exclue.\n"
             "Maximum 2 activités par jour (une le matin, une l'après-midi)."),

            ("🏛️ Attribution des salles",
             "Les salles sont attribuées en rotation parmi les salles saisies.\n"
             "L'algorithme respecte :\n"
             "  1. Le type de salle selon le type d'activité (CM→AMPHI, TP→LABO)\n"
             "  2. La capacité ≥ effectif de la cohorte\n"
             "  3. La disponibilité (pas déjà occupée au même créneau)\n"
             "  4. Rotation pour répartir l'utilisation entre toutes les salles"),

            ("👨‍🏫 Contraintes enseignants",
             "L'algorithme respecte :\n"
             "  • Les congés approuvés : aucun cours durant un congé approuvé\n"
             "  • Les disponibilités horaires : si un enseignant déclare ses\n"
             "    disponibilités, seuls les créneaux couverts sont utilisés\n"
             "  • Si aucune disponibilité déclarée : enseignant disponible par défaut"),

            ("⚠️ Que faire si ΣU > 1 ?",
             "Exemple : MPCI 2022 avec 254h sur 214 jours\n"
             "  ΣU = 254 / (214 × 4h) = 0.297 → devrait être ordonnançable !\n\n"
             "Si l'application affiche ΣU > 1, vérifiez que :\n"
             "  1. Les volumes horaires des activités sont corrects\n"
             "  2. La période configurée est suffisamment longue\n"
             "  3. Le calendrier académique couvre bien la période"),
        ]

        for title_s, text_s in sections:
            t = QLabel(title_s)
            t.setStyleSheet(
                "font-size:13px; font-weight:bold; color:#1a73e8; "
                "background:#E8F0FE; padding:6px 10px; border-radius:4px;"
            )
            clayout.addWidget(t)
            b = QLabel(text_s)
            b.setWordWrap(True)
            b.setStyleSheet(
                "font-size:12px; color:#333; padding:8px 12px; "
                "background:#F9FAFB; border-radius:4px; line-height:1.5;"
            )
            clayout.addWidget(b)

        clayout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        btn = QPushButton("Fermer")
        btn.setFixedHeight(38)
        btn.setStyleSheet(
            "background:#1a73e8; color:white; border-radius:6px; "
            "font-weight:bold; padding:0 20px;"
        )
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)


# ══════════════════════════════════════════════════════════════════
# THREAD D'ORDONNANCEMENT PFAIR
# ══════════════════════════════════════════════════════════════════

class PfairSchedulerThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, cohort_id, start_date, end_date, available_rooms=None, parent=None):
        super().__init__(parent)
        self.cohort_id       = cohort_id
        self.start_date      = start_date
        self.end_date        = end_date
        self.available_rooms = available_rooms or []
        # Compteur de rotation pour les salles
        self._room_rotation_index = 0

    def run(self):
        try:
            session       = db_manager.get_session()
            activity_repo = ActivityRepository(session)
            cohort_repo   = CohortRepository(session)
            teacher_repo  = TeacherRepository(session)

            self.progress.emit(5, "Chargement de la cohorte...")
            cohort = cohort_repo.get_by_id(self.cohort_id)
            if not cohort:
                self.error.emit("Cohorte introuvable.")
                return

            self.progress.emit(10, "Suppression des anciens créneaux...")
            self._delete_all_cohort_slots(cohort.id)

            self.progress.emit(15, "Chargement des activités...")
            activities = activity_repo.get_by_cohort(self.cohort_id)
            if not activities:
                self.error.emit("Aucune activité trouvée pour cette cohorte.")
                return

            # ── Remise à zéro COMPLÈTE avant génération ──────────────────────
            for act in activities:
                act.hours_done    = 0.0
                act.charge_factor = 0.0
            session.commit()

            self.progress.emit(25, "Calcul des jours ouvrables...")
            d_effective = self._calc_effective_days(self.start_date, self.end_date)
            if d_effective <= 0:
                self.error.emit("Aucun jour ouvrable dans la période sélectionnée.")
                return

            self.progress.emit(35, "Vérification de l'ordonnançabilité (ΣU ≤ m)...")
            total_charge    = 0.0
            activities_data = []
            print(f"[DEBUG] {len(activities)} activité(s) trouvée(s) pour la cohorte")

            for act in activities:
                volume    = float(act.volume_hours or 0.0)
                remaining = volume

                print(f"[DEBUG] Activité [{act.id}] '{act.name}' | vol={volume}h | teacher_id={act.teacher_id}")

                if remaining > 0:
                    # ✅ FIX : Ui TOUJOURS recalculé depuis le volume et d_effective
                    # Ne JAMAIS utiliser l'ancien charge_factor en base
                    Ui = remaining / d_effective
                    total_charge += Ui
                    # Mettre à jour charge_factor en base pour cohérence
                    act.charge_factor = Ui
                    activities_data.append({
                        'activity'  : act,
                        'Ui'        : Ui,
                        'remaining' : remaining,
                        'hours_done': 0.0,
                        'volume'    : remaining,
                    })

            session.commit()
            print(f"[DEBUG] d_effective={d_effective} jours | total_charge={total_charge:.4f}")

            schedulable = total_charge <= 1.0

            self.progress.emit(50, "Exécution de l'algorithme Pfair...")
            scheduled_slots     = []
            conflicts           = []
            activities_snapshot = {}

            t            = 0
            current_date = self.start_date
            calendar_id  = self._get_calendar_id(self.start_date)

            while current_date <= self.end_date:
                if not self._is_workday(current_date, calendar_id):
                    current_date += timedelta(days=1)
                    continue

                t += 1
                progress_val = 50 + int((t / max(d_effective, 1)) * 40)
                self.progress.emit(
                    min(progress_val, 90),
                    f"Planification du {current_date.strftime('%d/%m/%Y')}..."
                )

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

                urgent.sort(key=lambda x: x[1], reverse=True)

                creneaux_du_jour = list(CRENEAUX_AUTORISES)

                for act, alpha, delay, Ui in urgent:
                    if not creneaux_du_jour:
                        break

                    teacher = teacher_repo.get_by_id(act.teacher_id) if act.teacher_id else None

                    # 1. Vérifier congé
                    if teacher and self._is_teacher_on_leave(teacher.id, current_date):
                        conflicts.append({
                            'date'    : current_date,
                            'activity': act.name,
                            'reason'  : f"Enseignant {teacher.full_name} en congé approuvé"
                        })
                        continue

                    # 2. Chercher un créneau compatible
                    creneau_choisi = None
                    for creneau in creneaux_du_jour:
                        start_h, end_h = creneau
                        if teacher and not self._is_teacher_available(
                            teacher.id, current_date, start_h, end_h
                        ):
                            continue
                        creneau_choisi = creneau
                        break

                    if creneau_choisi is None:
                        conflicts.append({
                            'date'    : current_date,
                            'activity': act.name,
                            'reason'  : (
                                f"Enseignant {teacher.full_name if teacher else '?'} "
                                f"non disponible ce jour"
                            )
                        })
                        continue

                    creneaux_du_jour.remove(creneau_choisi)
                    start_hour, end_hour = creneau_choisi
                    slot_duration = end_hour - start_hour

                    # 3. Sélection de salle avec rotation
                    room = self._select_room_with_rotation(
                        act, cohort, current_date, start_hour
                    )

                    act_type_str = act.type
                    if hasattr(act_type_str, 'value'):
                        act_type_str = act_type_str.value
                    elif hasattr(act_type_str, 'name'):
                        act_type_str = act_type_str.name
                    act_type_str = str(act_type_str or '').split('.')[-1]

                    slot_info = {
                        'date'         : current_date,
                        'start'        : f"{start_hour:02d}:00",
                        'end'          : f"{end_hour:02d}:00",
                        'activity'     : act.name,
                        'activity_code': act.code,
                        'activity_type': act_type_str,
                        'teacher'      : teacher.full_name if teacher else "Non assigné",
                        'cohort'       : cohort.name,
                        'room'         : room,
                        'alpha'        : round(alpha, 3),
                        'delay'        : round(delay, 2),
                        'cohort_id'    : self.cohort_id,
                        'activity_id'  : act.id,
                        'teacher_id'   : act.teacher_id,
                    }
                    scheduled_slots.append(slot_info)

                    for _item in activities_data:
                        if _item['activity'].id == act.id:
                            _item['hours_done'] += slot_duration
                            break

                    if act.code not in activities_snapshot:
                        urgence = ('critique' if alpha >= 1.0
                                   else ('urgente' if alpha >= 0.5 else 'ok'))
                        activities_snapshot[act.code] = {
                            'nom'             : act.name,
                            'code'            : act.code,
                            'type'            : act.type,
                            'volume_total'    : act.volume_hours,
                            'heures_realisees': h_done,
                            'alpha'           : round(alpha, 3),
                            'urgence'         : urgence,
                            'enseignant'      : teacher.full_name if teacher else "Non assigné",
                        }
                    else:
                        activities_snapshot[act.code]['heures_realisees'] = h_done

                current_date += timedelta(days=1)

            self.progress.emit(93, "Sauvegarde de l'emploi du temps...")
            self._save_schedules(scheduled_slots, cohort)
            self.progress.emit(100, "Ordonnancement terminé !")

            _cohort_size  = cohort.student_count or 0
            _slots_data   = []
            _cap_warnings = 0
            for _sl in scheduled_slots:
                _rn  = _sl.get('room', '')
                _rc  = self._get_room_capacity(_rn)
                _ovl = bool(_rc > 0 and _cohort_size > 0 and _rc < _cohort_size)
                if _ovl:
                    _cap_warnings += 1
                _slots_data.append({
                    'activity'     : _sl.get('activity', '?'),
                    'date'         : str(_sl.get('date', '')),
                    'start'        : _sl.get('start', ''),
                    'end'          : _sl.get('end', ''),
                    'room'         : _rn or '—',
                    'room_capacity': _rc,
                    'is_overload'  : _ovl,
                })

            avail_conflicts = sum(
                1 for c in conflicts if 'non disponible' in c.get('reason', '')
            )

            results = {
                'success'           : True,
                'cohort_name'       : cohort.name,
                'period'            : (
                    f"{self.start_date.strftime('%d/%m/%Y')} "
                    f"au {self.end_date.strftime('%d/%m/%Y')}"
                ),
                'total_activities'  : len(activities),
                'scheduled_slots'   : len(scheduled_slots),
                'total_hours'       : len(scheduled_slots) * 4,
                'total_charge'      : round(total_charge, 4),
                'effective_days'    : d_effective,
                'schedulable'       : schedulable,
                'conflicts'         : len(conflicts),
                'avail_conflicts'   : avail_conflicts,
                'activities'        : list(activities_snapshot.values()),
                'slots'             : scheduled_slots,
                'cohort_id'         : cohort.id,
                'cohort_size'       : _cohort_size,
                'slots_data'        : _slots_data,
                'capacity_warnings' : _cap_warnings,
                'conflicts_details' : conflicts,
            }
            self.finished.emit(results)

        except Exception as e:
            import traceback
            self.error.emit(f"Erreur : {str(e)}\n{traceback.format_exc()}")

    # ──────────────────────────────────────────────────────────────
    # Méthodes utilitaires
    # ──────────────────────────────────────────────────────────────

    def _delete_all_cohort_slots(self, cohort_id: int):
        """Supprime TOUS les créneaux d'une cohorte."""
        try:
            from src.database.models import ScheduleSlotModel
            session = db_manager.get_session()
            deleted = session.query(ScheduleSlotModel).filter(
                ScheduleSlotModel.cohort_id == cohort_id
            ).delete(synchronize_session=False)
            session.commit()
            print(f"[DEBUG] {deleted} anciens créneaux supprimés pour cohorte {cohort_id}")
        except Exception as e:
            print(f"[scheduling_tab] Erreur suppression: {e}")

    def _select_room_with_rotation(self, act, cohort, current_date: date, start_hour: int) -> str:
        """
        Sélectionne une salle disponible avec rotation entre les salles.

        La rotation garantit que toutes les salles sont utilisées équitablement
        plutôt que de toujours prendre la première salle de la liste.
        """
        if not self.available_rooms:
            return "Salle TBD"

        from sqlalchemy import text as sqlt
        session = db_manager.get_session()

        required_capacity = cohort.student_count or 0
        start_str = f"{start_hour:02d}:00"
        date_str  = str(current_date)

        # Salles occupées à ce créneau
        occupied_rows = session.execute(sqlt(
            "SELECT DISTINCT room FROM schedule_slots "
            "WHERE date = :d AND start_time LIKE :st AND room IS NOT NULL"
        ), {'d': date_str, 'st': f"{start_str}%"}).fetchall()
        occupied = {r[0] for r in occupied_rows}

        # Salles libres
        free_rooms = [r for r in self.available_rooms if r not in occupied]
        if not free_rooms:
            return "Salle TBD"

        # ✅ Rotation : réordonner la liste à partir de l'index de rotation
        n = len(free_rooms)
        idx = self._room_rotation_index % n
        rotated = free_rooms[idx:] + free_rooms[:idx]
        self._room_rotation_index += 1

        # Récupérer les infos des salles libres
        names_ph = ','.join([f':n{i}' for i in range(len(free_rooms))])
        params   = {f'n{i}': nm for i, nm in enumerate(free_rooms)}

        # Type préféré selon activité
        act_type_val = str(getattr(getattr(act, 'type', None), 'value', None) or '').lower()
        type_map = {
            'magistral': ['AMPHI', 'TD'],
            'dirige'   : ['TD', 'AMPHI'],
            'pratique' : ['TP', 'LABO', 'INFORMATIQUE'],
            'td'       : ['TD', 'AMPHI'],
            'tp'       : ['TP', 'LABO', 'INFORMATIQUE'],
            'cm'       : ['AMPHI', 'TD'],
        }
        preferred_types = next(
            (v for k, v in type_map.items() if k in act_type_val), None
        )

        # Récupérer toutes les salles libres avec leurs infos
        rows = session.execute(sqlt(
            f"SELECT name, room_type, capacity FROM rooms "
            f"WHERE is_active = 1 AND name IN ({names_ph}) "
            f"ORDER BY capacity ASC"
        ), params).fetchall()

        room_info = {r[0]: {'type': r[1], 'capacity': r[2] or 0} for r in rows}

        # Essai 1 : type préféré + capacité suffisante dans l'ordre de rotation
        if preferred_types:
            for ptype in preferred_types:
                for room_name in rotated:
                    info = room_info.get(room_name, {})
                    if (info.get('type') == ptype and
                            info.get('capacity', 0) >= required_capacity):
                        return room_name

        # Essai 2 : n'importe quel type + capacité suffisante (rotation)
        for room_name in rotated:
            info = room_info.get(room_name, {})
            if info.get('capacity', 0) >= required_capacity:
                return room_name

        # Essai 3 (fallback) : première salle libre dans la rotation
        return rotated[0] if rotated else "Salle TBD"

    def _get_calendar_id(self, reference_date: date):
        try:
            from src.database.models import AcademicCalendarModel
            session  = db_manager.get_session()
            calendar = session.query(AcademicCalendarModel).filter(
                AcademicCalendarModel.start_date <= reference_date,
                AcademicCalendarModel.end_date   >= reference_date,
            ).first()
            return calendar.id if calendar else None
        except Exception:
            return None

    def _calc_effective_days(self, start: date, end: date) -> int:
        try:
            from src.services.calendar_service import CalendarService
            session     = db_manager.get_session()
            cal_service = CalendarService(session)
            calendar_id = self._get_calendar_id(start)
            return cal_service.calculate_effective_days(start, end, calendar_id)
        except Exception:
            count = 0
            d = start
            while d <= end:
                if d.weekday() < 5:
                    count += 1
                d += timedelta(days=1)
            return count

    def _is_workday(self, check_date: date, calendar_id) -> bool:
        try:
            from src.services.calendar_service import CalendarService
            session = db_manager.get_session()
            return CalendarService(session).is_workday(check_date, calendar_id)
        except Exception:
            return check_date.weekday() < 5

    def _is_teacher_on_leave(self, teacher_id: int, check_date: date) -> bool:
        try:
            from src.database.models import LeaveRequestModel, LeaveStatusEnum
            from sqlalchemy import and_
            session = db_manager.get_session()
            leave = session.query(LeaveRequestModel).filter(
                and_(
                    LeaveRequestModel.teacher_id == teacher_id,
                    LeaveRequestModel.status     == LeaveStatusEnum.APPROVED,
                    LeaveRequestModel.start_date <= check_date,
                    LeaveRequestModel.end_date   >= check_date,
                )
            ).first()
            return leave is not None
        except Exception:
            return False

    def _is_teacher_available(self, teacher_id: int, check_date: date,
                               start_hour: int, end_hour: int) -> bool:
        try:
            from src.database.models import TeacherAvailabilityModel
            from datetime import time as dtime
            from sqlalchemy import and_
            session = db_manager.get_session()

            total_avail = session.query(TeacherAvailabilityModel).filter(
                TeacherAvailabilityModel.teacher_id == teacher_id
            ).count()
            if total_avail == 0:
                return True

            avail = session.query(TeacherAvailabilityModel).filter(
                and_(
                    TeacherAvailabilityModel.teacher_id  == teacher_id,
                    TeacherAvailabilityModel.day_of_week == check_date.weekday(),
                    TeacherAvailabilityModel.start_time  <= dtime(hour=start_hour),
                    TeacherAvailabilityModel.end_time    >= dtime(hour=end_hour),
                    TeacherAvailabilityModel.period_start <= check_date,
                    TeacherAvailabilityModel.period_end  >= check_date,
                )
            ).first()
            return avail is not None
        except Exception:
            return True

    def _get_room_capacity(self, room_name: str) -> int:
        if not room_name or room_name in ('—', 'Salle TBD', ''):
            return 0
        try:
            from sqlalchemy import text as sqlt
            session = db_manager.get_session()
            row = session.execute(
                sqlt('SELECT capacity FROM rooms WHERE name=:n'),
                {'n': room_name}
            ).fetchone()
            return int(row[0]) if row and row[0] else 0
        except Exception:
            return 0

    def _save_schedules(self, slots, cohort):
        nb_inserts = 0
        print(f"[DEBUG] Insertion de {len(slots)} créneau(x) dans schedule_slots")
        try:
            from datetime import time as dtime
            from src.database.models import ScheduleSlotModel
            session = db_manager.get_session()

            for s in slots:
                if not s.get('teacher_id') or not s.get('activity_id'):
                    continue
                try:
                    start_h, start_m = map(int, s['start'].split(':'))
                    end_h,   end_m   = map(int, s['end'].split(':'))
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
                        notes       = (
                            f"alpha={s.get('alpha', 0.0)} "
                            f"type={str(s.get('activity_type','') or '').split('.')[-1]}"
                        ),
                    )
                    session.add(slot)
                    nb_inserts += 1
                except Exception as e_slot:
                    print(f"[scheduling_tab] Erreur slot: {e_slot}")

            session.commit()
            print(f"[scheduling_tab] ✅ {nb_inserts} créneaux insérés")

        except Exception as e:
            print(f"[scheduling_tab] ❌ Erreur: {e}")
            import traceback; traceback.print_exc()

        try:
            data_dir = Path("data"); data_dir.mkdir(exist_ok=True)
            path = data_dir / "schedules.json"
            existing = {}
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            slots_json = []
            for s in slots:
                s2 = dict(s)
                if hasattr(s2.get('date'), 'isoformat'):
                    s2['date'] = s2['date'].isoformat()
                slots_json.append(s2)
            existing[cohort.name] = {
                'cohort_id'   : cohort.id,
                'cohort_name' : cohort.name,
                'generated_at': datetime.now().isoformat(),
                'nb_slots'    : nb_inserts,
                'slots'       : slots_json,
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"[scheduling_tab] JSON échoué: {e}")


# ══════════════════════════════════════════════════════════════════
# DIALOG RÉSULTATS
# ══════════════════════════════════════════════════════════════════

class ResultsDialog(QDialog):
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
        title.setStyleSheet("font-size:20px; font-weight:bold; color:#1a73e8;")
        layout.addWidget(title)

        subtitle = QLabel(f"Période : {self.results.get('period', '')}")
        subtitle.setStyleSheet("color:#666; font-size:13px;")
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._build_summary_tab(),    "📋 Résumé")
        tabs.addTab(self._build_activities_tab(), "📚 Activités")
        tabs.addTab(self._build_stats_tab(),      "📈 Statistiques")
        tabs.addTab(self._build_rooms_tab(),      "🏛️ Salles")
        layout.addWidget(tabs)

        btn = QPushButton("Fermer")
        btn.setFixedHeight(40)
        btn.setStyleSheet(
            "QPushButton {background:#1a73e8; color:white; border-radius:6px; font-size:14px;}"
            "QPushButton:hover {background:#1558b0;}"
        )
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)

    def _build_summary_tab(self):
        w = QWidget(); layout = QVBoxLayout(w); layout.setContentsMargins(15,15,15,15)
        r = self.results; schedulable = r.get('schedulable', False)
        status_lbl = QLabel(
            f"✅ ORDONNANÇABLE  (ΣU = {r.get('total_charge',0):.4f} ≤ 1)"
            if schedulable else
            f"⚠️ CHARGE ÉLEVÉE  (ΣU = {r.get('total_charge',0):.4f} > 1)"
        )
        status_lbl.setStyleSheet(
            f"font-size:14px; font-weight:bold; padding:10px; border-radius:6px;"
            f"color:{'#2e7d32' if schedulable else '#c62828'};"
            f"background-color:{'#e8f5e9' if schedulable else '#ffebee'};"
        )
        layout.addWidget(status_lbl)

        if not schedulable:
            fix_lbl = QLabel(
                f"💡 Pour rendre le système ordonnançable :\n"
                f"   • Allonger la période (reculer la date de fin)\n"
                f"   • Ou réduire le volume horaire de certaines activités\n"
                f"   • Volume total : {sum(a.get('volume_total',0) for a in r.get('activities',[])):.0f}h "
                f"sur {r.get('effective_days',0)} jours effectifs"
            )
            fix_lbl.setWordWrap(True)
            fix_lbl.setStyleSheet(
                "background:#FEF3C7; color:#92400E; padding:8px; border-radius:6px; font-size:12px;"
            )
            layout.addWidget(fix_lbl)

        avail_conflicts = r.get('avail_conflicts', 0)
        if avail_conflicts > 0:
            lbl = QLabel(f"ℹ️  {avail_conflicts} créneau(x) non planifié(s) : enseignant indisponible.")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("background:#EFF6FF; color:#1E40AF; padding:8px; border-radius:6px; font-size:12px;")
            layout.addWidget(lbl)

        form = QFormLayout(); form.setSpacing(8)
        for lbl, val in [
            ("🎓 Cohorte",            r.get('cohort_name','-')),
            ("📅 Période",            r.get('period','-')),
            ("📚 Activités",          str(r.get('total_activities',0))),
            ("🗓️ Créneaux planifiés", str(r.get('scheduled_slots',0))),
            ("⏱️ Heures planifiées",  f"{r.get('total_hours',0)} h"),
            ("📊 Charge totale ΣU",   f"{r.get('total_charge',0):.4f}"),
            ("📅 Jours effectifs",    str(r.get('effective_days',0))),
            ("⚠️ Conflits totaux",    str(r.get('conflicts',0))),
            ("📅 Indisponibilités",   str(avail_conflicts)),
            ("🏛️ Surcharges salle",   str(r.get('capacity_warnings',0))),
        ]:
            form.addRow(QLabel(f"<b>{lbl} :</b>"), QLabel(val))
        layout.addLayout(form); layout.addStretch()
        return w

    def _build_activities_tab(self):
        w = QWidget(); layout = QVBoxLayout(w)
        activities = self.results.get('activities', [])
        table = QTableWidget(len(activities), 7)
        table.setHorizontalHeaderLabels(["Activité","Code","Type","Vol. total (h)","Réalisé (h)","α","Urgence"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.setAlternatingRowColors(True); table.setEditTriggers(QTableWidget.NoEditTriggers)
        for row, act in enumerate(activities):
            table.setItem(row,0,QTableWidgetItem(act.get('nom','')))
            table.setItem(row,1,QTableWidgetItem(act.get('code','')))
            table.setItem(row,2,QTableWidgetItem(str(act.get('type','') or '').split('.')[-1]))
            table.setItem(row,3,QTableWidgetItem(str(act.get('volume_total',0))))
            table.setItem(row,4,QTableWidgetItem(f"{act.get('heures_realisees',0):.1f}"))
            table.setItem(row,5,QTableWidgetItem(f"{act.get('alpha',0):.3f}"))
            u = act.get('urgence','ok'); itm = QTableWidgetItem(u.upper())
            if u=='critique': itm.setBackground(QColor('#FFCDD2')); itm.setForeground(QColor('#C62828'))
            elif u=='urgente': itm.setBackground(QColor('#FFF9C4')); itm.setForeground(QColor('#F57F17'))
            else: itm.setBackground(QColor('#C8E6C9')); itm.setForeground(QColor('#2E7D32'))
            table.setItem(row,6,itm)
        layout.addWidget(table); return w

    def _build_rooms_tab(self):
        w = QWidget(); layout = QVBoxLayout(w); layout.setContentsMargins(12,12,12,12)
        r = self.results; cohort_size = r.get('cohort_size',0); cap_warns = r.get('capacity_warnings',0)
        layout.addWidget(QLabel(f"Effectif : {cohort_size} étudiants  |  Surcharges : {cap_warns}"))
        slots_data = r.get('slots_data',[])
        table = QTableWidget(len(slots_data),6)
        table.setHorizontalHeaderLabels(["Activité","Date","Horaire","Salle","Capacité","Effectif"])
        table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        for i in [1,2,3,4,5]: table.horizontalHeader().setSectionResizeMode(i,QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True); table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        for row, slot in enumerate(slots_data):
            room_cap = slot.get('room_capacity',0)
            is_ovl   = slot.get('is_overload',False) or (room_cap>0 and cohort_size>0 and room_cap<cohort_size)
            bg = QColor("#FEF3C7") if is_ovl else QColor("#FFFFFF")
            for col, val in enumerate([
                slot.get('activity','?'), str(slot.get('date','')),
                slot.get('start','') + " – " + slot.get('end',''),
                slot.get('room','—'), str(room_cap) if room_cap else "?",
                str(cohort_size) if cohort_size else "?"
            ]):
                item = QTableWidgetItem(val); item.setBackground(bg); item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row,col,item)
        layout.addWidget(table); return w

    def _build_stats_tab(self):
        w = QWidget(); layout = QVBoxLayout(w)
        acts = self.results.get('activities',[])
        total = len(acts)
        critiques = sum(1 for a in acts if a.get('urgence')=='critique')
        urgentes  = sum(1 for a in acts if a.get('urgence')=='urgente')
        ok = total - critiques - urgentes
        total_vol  = sum(a.get('volume_total',0) for a in acts)
        total_real = sum(a.get('heures_realisees',0) for a in acts)
        completion = (total_real/total_vol*100) if total_vol>0 else 0
        r = self.results
        text = QTextEdit(); text.setReadOnly(True)
        text.setStyleSheet("font-family:Consolas,monospace; font-size:13px;")
        text.setPlainText(f"""
STATISTIQUES D'ORDONNANCEMENT PFAIR
══════════════════════════════════════════

Cohorte  : {r.get('cohort_name','-')}
Période  : {r.get('period','-')}

CRÉNEAUX HORAIRES (Burkina Faso)
────────────────────────────────────
  Matin       : 08h00 → 12h00
  Après-midi  : 14h00 → 18h00
  Pause exclue: 12h00 → 14h00

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
  Charge totale ΣU   : {r.get('total_charge',0):.4f}
  Jours effectifs D  : {r.get('effective_days',0)}
  Créneaux planifiés : {r.get('scheduled_slots',0)}
  Heures planifiées  : {r.get('total_hours',0)} h
  Conflits           : {r.get('conflicts',0)}
  Indisponibilités   : {r.get('avail_conflicts',0)}
  Ordonnançable      : {'OUI ✅' if r.get('schedulable') else 'NON ⚠️'}

FORMULE PFAIR
────────────────────────────────────
  Uᵢ = Cᵢ / D_effectif
  ΣU = {r.get('total_charge',0):.4f} {'≤ 1 ✅' if r.get('schedulable') else '> 1 ⚠️'}
  α(τᵢ,t) = (Uᵢ×t - H_réalisé) / Uᵢ
""")
        layout.addWidget(text); return w


# ══════════════════════════════════════════════════════════════════
# ONGLET PRINCIPAL UC6
# ══════════════════════════════════════════════════════════════════

class SchedulingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._init_ui()
        self._load_cohorts()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ── En-tête avec bouton Aide ──────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("⚙️ Ordonnancement P-équitable (Pfair)")
        title.setStyleSheet("font-size:22px; font-weight:bold; color:#1a1a1a;")
        header.addWidget(title)
        header.addStretch()

        # ✅ Bouton Aide fonctionnel
        btn_help = QPushButton("❓ Aide")
        btn_help.setFixedHeight(36)
        btn_help.setFixedWidth(90)
        btn_help.setStyleSheet(
            "QPushButton {background:#E8F0FE; color:#1a73e8; border:1px solid #1a73e8; "
            "border-radius:6px; font-weight:bold; font-size:13px;}"
            "QPushButton:hover {background:#D2E3FC;}"
        )
        btn_help.clicked.connect(self._show_help)
        header.addWidget(btn_help)
        layout.addLayout(header)

        subtitle = QLabel("Formule : H_ideal(t) = Ui × t  |  α(τi, t) = (H_ideal − H_réalisé) / Ui")
        subtitle.setStyleSheet("color:#555; font-size:12px; font-style:italic;")
        layout.addWidget(subtitle)

        horaires_lbl = QLabel("🕐 Créneaux : 08h00–12h00 (matin)  |  14h00–18h00 (après-midi)")
        horaires_lbl.setStyleSheet(
            "background:#E8F5E9; color:#2E7D32; padding:6px 12px; "
            "border-radius:6px; font-size:12px; font-weight:bold;"
        )
        layout.addWidget(horaires_lbl)

        warn_lbl = QLabel(
            "ℹ️  À chaque lancement, les anciens créneaux sont supprimés et "
            "remplacés. Les heures réalisées sont remises à zéro."
        )
        warn_lbl.setWordWrap(True)
        warn_lbl.setStyleSheet(
            "background:#FEF3C7; color:#92400E; padding:6px 12px; border-radius:6px; font-size:11px;"
        )
        layout.addWidget(warn_lbl)

        config_group = QGroupBox("Configuration de l'ordonnancement")
        config_group.setStyleSheet("""
            QGroupBox {font-weight:bold; border:1px solid #ddd; border-radius:8px; padding-top:10px;}
            QGroupBox::title {padding:0 8px; color:#333;}
        """)
        form = QFormLayout(config_group); form.setSpacing(12)

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
        self.rooms_input.setPlaceholderText("Ex : AMPHI 500, AMPHI 750, AMPHI 1000, PSUT-EST")
        self.rooms_input.setFixedHeight(40)
        self.rooms_input.setStyleSheet(self._fstyle())
        form.addRow("Salles disponibles :", self.rooms_input)

        layout.addWidget(config_group)

        self.run_btn = QPushButton("🚀  Lancer l'ordonnancement")
        self.run_btn.setFixedHeight(48)
        self.run_btn.setStyleSheet("""
            QPushButton {background-color:#1a73e8; color:white; border-radius:8px;
                font-size:15px; font-weight:bold;}
            QPushButton:hover {background-color:#1558b0;}
            QPushButton:disabled {background-color:#aaa;}
        """)
        self.run_btn.clicked.connect(self._start_scheduling)
        layout.addWidget(self.run_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(22)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {border-radius:4px; background:#f0f0f0; text-align:center;}
            QProgressBar::chunk {background-color:#1a73e8; border-radius:4px;}
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color:#555; font-size:12px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _show_help(self):
        """✅ Bouton Aide — ouvre le dialogue d'explication."""
        HelpDialog(self).exec_()

    def _fstyle(self):
        return "border:1px solid #D1D5DB; border-radius:6px; padding:8px 12px; font-size:13px;"

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
                self.cohort_combo.addItem("⚠️ Aucune cohorte", userData=None)
        except Exception as e:
            self.cohort_combo.addItem(f"Erreur: {str(e)[:40]}", userData=None)

    def _start_scheduling(self):
        cohort_id = self.cohort_combo.currentData()
        if not cohort_id:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner une cohorte valide.")
            return

        sd    = self.start_date_edit.date()
        ed    = self.end_date_edit.date()
        start = date(sd.year(), sd.month(), sd.day())
        end   = date(ed.year(), ed.month(), ed.day())
        if end <= start:
            QMessageBox.warning(self, "Dates invalides",
                "La date de fin doit être postérieure à la date de début.")
            return

        reply = QMessageBox.question(
            self, "Confirmation",
            "⚠️ Cette action va supprimer TOUS les créneaux existants "
            "de cette cohorte et en générer de nouveaux.\n\nContinuer ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        rooms_txt = self.rooms_input.text().strip()
        rooms     = [r.strip() for r in rooms_txt.split(',') if r.strip()]

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