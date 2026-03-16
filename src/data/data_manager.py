"""
DataManager conforme à la conception - stockage JSON/CSV.

Conforme au document de conception :
- structure.json : hiérarchie université -> UFR -> parcours -> classes
- activities.csv : activités académiques
- teachers.csv : enseignants
- leaves.json : demandes de congé
- calendar_YYYY_YYYY.json : calendrier académique
"""
import json
import csv
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from types import SimpleNamespace


def _json_serial(obj):
    """Sérialisation JSON pour datetime et date."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} non sérialisable")


def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).date() if "T" in str(s) else datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class DataManager:
    """
    Gestionnaire de données conforme à la conception.
    API unifiée pour charger/sauvegarder en JSON et CSV.
    """

    def __init__(self, data_dir: Path = None):
        self._data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._structure_file = self._data_dir / "structure.json"
        self._activities_file = self._data_dir / "activities.csv"
        self._teachers_file = self._data_dir / "teachers.csv"
        self._leaves_file = self._data_dir / "leaves.json"
        self._schedules_dir = self._data_dir / "schedules"
        try:
            self._schedules_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            self._schedules_dir = self._data_dir

        self._structure: Dict = {}
        self._activities: List[Dict] = []
        self._teachers: List[Dict] = []
        self._leaves: List[Dict] = []
        self._next_ids: Dict[str, int] = {}

    def load_all(self) -> None:
        """Charge toutes les données depuis les fichiers."""
        self._load_structure()
        self._load_activities()
        self._load_teachers()
        self._load_leaves()

    def save_all(self) -> None:
        """Sauvegarde toutes les données vers les fichiers."""
        self._save_structure()
        self._save_activities()
        self._save_teachers()
        self._save_leaves()

    # --- Structure (structure.json) ---

    def _load_structure(self) -> None:
        if self._structure_file.exists():
            with open(self._structure_file, "r", encoding="utf-8") as f:
                self._structure = json.load(f)
        else:
            self._structure = {"universités": []}

    def _save_structure(self) -> None:
        with open(self._structure_file, "w", encoding="utf-8") as f:
            json.dump(self._structure, f, ensure_ascii=False, indent=2, default=_json_serial)

    def get_universities(self) -> List[SimpleNamespace]:
        """Retourne la liste des universités (structure imbriquée)."""
        result = []
        for u in self._structure.get("universités", []):
            ufrs = []
            for uf in u.get("ufrs", []):
                parcours = []
                for p in uf.get("parcours", []):
                    classes = [SimpleNamespace(
                        id=c.get("id"), nom=c.get("nom"), année_académique=c.get("année_académique"),
                        semestre=c.get("semestre", 1), effectif=c.get("effectif", 0),
                        date_début=c.get("date_début"), date_fin=c.get("date_fin")
                    ) for c in p.get("classes", [])]
                    parcours.append(SimpleNamespace(
                        id=p.get("id"), nom=p.get("nom"), code=p.get("code"),
                        niveau=p.get("niveau"), durée_années=p.get("durée_années", 1), classes=classes
                    ))
                ufrs.append(SimpleNamespace(
                    id=uf.get("id"), nom=uf.get("nom"), code=uf.get("code"),
                    directeur=uf.get("directeur", ""), parcours=parcours
                ))
            result.append(SimpleNamespace(
                id=u.get("id"),
                name=u.get("nom", ""),
                code=u.get("code", ""),
                address=u.get("adresse", ""),
                city=u.get("ville", ""),
                country=u.get("pays", "Burkina Faso"),
                ufrs=ufrs
            ))
        return result

    def add_university(self, nom: str, code: str, adresse: str, ville: str, pays: str = "Burkina Faso") -> Dict:
        uid = self._next_id("university")
        uid = f"univ_{uid}"
        u = {
            "id": uid,
            "nom": nom,
            "code": code,
            "adresse": adresse,
            "ville": ville,
            "pays": pays,
            "ufrs": []
        }
        self._structure.setdefault("universités", []).append(u)
        self._save_structure()
        return {"id": uid, "success": True}  # uid = "univ_N"

    def add_ufr(self, university_id: str, nom: str, code: str, directeur: str) -> Dict:
        for u in self._structure.get("universités", []):
            if u.get("id") == university_id:
                n = self._next_id("ufr")
                ufr = {"id": f"ufr_{n}", "nom": nom, "code": code, "directeur": directeur, "parcours": []}
                u.setdefault("ufrs", []).append(ufr)
                self._save_structure()
                return {"id": n, "success": True}
        return {"success": False, "error": "Université introuvable"}

    def add_program(self, ufr_id: str, nom: str, code: str, niveau: str, durée_années: int) -> Dict:
        for u in self._structure.get("universités", []):
            for ufr in u.get("ufrs", []):
                if ufr.get("id") == ufr_id:
                    n = self._next_id("program")
                    p = {"id": f"parcours_{n}", "nom": nom, "code": code, "niveau": niveau, "durée_années": durée_années, "classes": []}
                    ufr.setdefault("parcours", []).append(p)
                    self._save_structure()
                    return {"id": n, "success": True}
        return {"success": False, "error": "UFR introuvable"}

    def add_cohort(self, program_id: str, nom: str, année: str, semestre: int, effectif: int, date_début: str, date_fin: str) -> Dict:
        for u in self._structure.get("universités", []):
            for ufr in u.get("ufrs", []):
                for p in ufr.get("parcours", []):
                    if p.get("id") == program_id:
                        n = self._next_id("cohort")
                        c = {"id": f"classe_{n}", "nom": nom, "année_académique": année, "semestre": semestre, "effectif": effectif, "date_début": date_début, "date_fin": date_fin}
                        p.setdefault("classes", []).append(c)
                        self._save_structure()
                        return {"id": n, "success": True}
        return {"success": False, "error": "Parcours introuvable"}

    def _next_id(self, prefix: str) -> int:
        """Génère le prochain ID numérique pour un préfixe (university, ufr, program, cohort)."""
        max_id = 0
        for u in self._structure.get("universités", []):
            if prefix == "university":
                try:
                    n = int(str(u.get("id", "univ_0")).replace("univ_", ""))
                    max_id = max(max_id, n)
                except (ValueError, TypeError):
                    pass
            for ufr in u.get("ufrs", []):
                if prefix == "ufr":
                    try:
                        n = int(str(ufr.get("id", "ufr_0")).replace("ufr_", ""))
                        max_id = max(max_id, n)
                    except (ValueError, TypeError):
                        pass
                for p in ufr.get("parcours", []):
                    if prefix == "program":
                        try:
                            n = int(str(p.get("id", "parcours_0")).replace("parcours_", ""))
                            max_id = max(max_id, n)
                        except (ValueError, TypeError):
                            pass
                    for c in p.get("classes", []):
                        if prefix == "cohort":
                            try:
                                n = int(str(c.get("id", "classe_0")).replace("classe_", ""))
                                max_id = max(max_id, n)
                            except (ValueError, TypeError):
                                pass
        return max_id + 1
<<<<<<< HEAD
        def add_teacher_availability(self, teacher_id: int, day_of_week: int, start_time, end_time, period_start, period_end) -> dict:
            """
            Enregistre une disponibilité récurrente pour un enseignant en base de données.
            Args:
                teacher_id: ID de l'enseignant
                day_of_week: Jour de la semaine (0=lundi, 6=dimanche)
                start_time: Heure de début (datetime.time ou str)
                end_time: Heure de fin (datetime.time ou str)
                period_start: Date de début de la récurrence (datetime.date ou str)
                period_end: Date de fin de la récurrence (datetime.date ou str)
            Returns:
                dict: Résultat de l'opération
            """
            from src.database.db_manager import db_manager
            from src.database.repositories.teacher_availability_repository import TeacherAvailabilityRepository
            import datetime
            session = db_manager.get_session()
            repo = TeacherAvailabilityRepository(session)
            # Conversion des heures et dates si besoin
            if isinstance(start_time, str):
                start_time = datetime.time.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.time.fromisoformat(end_time)
            if isinstance(period_start, str):
                period_start = datetime.date.fromisoformat(period_start)
            if isinstance(period_end, str):
                period_end = datetime.date.fromisoformat(period_end)
            try:
                slot = repo.create(
                    teacher_id=teacher_id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    period_start=period_start,
                    period_end=period_end
                )
                return {"id": slot.id, "success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}
=======

>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # --- Activities (activities.csv) ---

    def _load_activities(self) -> None:
        self._activities = []
        if self._activities_file.exists():
            with open(self._activities_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._activities.append(dict(row))

    def _save_activities(self) -> None:
        if not self._activities:
            return
        cols = ["id", "nom", "code", "type", "classe_id", "enseignant_id", "volume_horaire", "heures_realisees", "facteur_charge", "statut"]
        with open(self._activities_file, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(self._activities)

    def get_activities(self) -> List[SimpleNamespace]:
        result = []
        for a in self._activities:
            result.append(SimpleNamespace(
                id=a.get("id"),
                name=a.get("nom", ""),
                code=a.get("code", ""),
                type=a.get("type", "CM"),
                cohort_id=a.get("classe_id"),
                teacher_id=a.get("enseignant_id") or None,
                volume_hours=float(a.get("volume_horaire", 0) or 0),
                hours_done=float(a.get("heures_realisees", 0) or 0),
                status=a.get("statut", "En attente")
            ))
        return result

    def add_activity(self, nom: str, code: str, type_act: str, classe_id: str, enseignant_id: str, volume: float) -> Dict:
        aid = f"act_{len(self._activities) + 1}"
        self._activities.append({
            "id": aid, "nom": nom, "code": code, "type": type_act,
            "classe_id": classe_id, "enseignant_id": enseignant_id,
            "volume_horaire": str(volume), "heures_realisees": "0", "facteur_charge": "0", "statut": "En attente"
        })
        self._save_activities()
        return {"id": aid, "success": True}

    # --- Teachers (teachers.csv) ---

    def _load_teachers(self) -> None:
        self._teachers = []
        if self._teachers_file.exists():
            with open(self._teachers_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._teachers.append(dict(row))

    def _save_teachers(self) -> None:
        if not self._teachers:
            return
        cols = ["id", "nom_complet", "email", "telephone", "specialite", "statut", "max_heures_semaine", "max_heures_jour"]
        with open(self._teachers_file, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(self._teachers)

    def get_teachers(self) -> List[SimpleNamespace]:
        result = []
        for t in self._teachers:
            result.append(SimpleNamespace(
                id=t.get("id"),
                full_name=t.get("nom_complet", ""),
                email=t.get("email", ""),
                phone=t.get("telephone", ""),
                speciality=t.get("specialite", ""),
                status=t.get("statut", "Permanent"),
                max_hours_per_week=int(t.get("max_heures_semaine", 40) or 40),
                max_hours_per_day=int(t.get("max_heures_jour", 8) or 8)
            ))
        return result

    def add_teacher(self, nom_complet: str, email: str, telephone: str, specialite: str, statut: str = "Permanent") -> Dict:
        tid = f"ens_{len(self._teachers) + 1}"
        self._teachers.append({
            "id": tid, "nom_complet": nom_complet, "email": email, "telephone": telephone,
            "specialite": specialite, "statut": statut, "max_heures_semaine": "40", "max_heures_jour": "8"
        })
        self._save_teachers()
        return {"id": tid, "success": True}

    # --- Leaves (leaves.json) ---

    def _load_leaves(self) -> None:
        if self._leaves_file.exists():
            with open(self._leaves_file, "r", encoding="utf-8") as f:
<<<<<<< HEAD
                self._leaves = json.load(f)
=======
                data = json.load(f)
            # Supporter plusieurs formats de fichier :
            # - liste directe de demandes : [ {..}, {..} ]
            # - ancien format avec racine contenant 'demandes' : { 'demandes': [..], ... }
            if isinstance(data, dict):
                if "demandes" in data and isinstance(data["demandes"], list):
                    self._leaves = data["demandes"]
                elif "leaves" in data and isinstance(data["leaves"], list):
                    self._leaves = data["leaves"]
                else:
                    # si dict mais pas la clé attendue, essayer de détecter une liste de valeurs
                    possible = [v for v in data.values() if isinstance(v, list)]
                    self._leaves = possible[0] if possible else []
            elif isinstance(data, list):
                self._leaves = data
            else:
                self._leaves = []
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        else:
            self._leaves = []

    def _save_leaves(self) -> None:
        with open(self._leaves_file, "w", encoding="utf-8") as f:
            json.dump(self._leaves, f, ensure_ascii=False, indent=2, default=_json_serial)

    def get_leaves(self) -> List[SimpleNamespace]:
<<<<<<< HEAD
        return [SimpleNamespace(**l) for l in self._leaves]
=======
        result: List[SimpleNamespace] = []
        for l in self._leaves:
            if not isinstance(l, dict):
                # ignorer les entrées non-mappables
                continue
            # Normaliser les noms de champs pour compatibilité (FR/EN/anciens formats)
            start = l.get("start_date") or l.get("date_debut") or l.get("date_creation") or l.get("start")
            end = l.get("end_date") or l.get("date_fin") or l.get("end")
            typ = l.get("type") or l.get("type_leave") or l.get("type_conge")
            reason = l.get("reason") or l.get("justification") or l.get("raison") or l.get("motif")
            status = l.get("status") or l.get("statut") or l.get("etat")
            teacher_id = l.get("teacher_id") or l.get("enseignant_id") or l.get("enseignant")
            result.append(SimpleNamespace(
                id=l.get("id"),
                teacher_id=teacher_id,
                start_date=start,
                end_date=end,
                type=typ,
                reason=reason,
                status=status,
                raw=l,
            ))
        return result
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f

    def add_leave(self, teacher_id: str, start: str, end: str, leave_type: str, reason: str) -> Dict:
        lid = f"leave_{len(self._leaves) + 1}"
        self._leaves.append({"id": lid, "teacher_id": teacher_id, "start_date": start, "end_date": end, "type": leave_type, "reason": reason, "status": "En attente"})
        self._save_leaves()
        return {"id": lid, "success": True}

    # --- Schedules (outputs) ---

    def save_schedule_csv(self, schedule: List[Dict], filename: str) -> Path:
        path = self._schedules_dir / filename
        if not schedule:
            return path
        cols = list(schedule[0].keys())
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(schedule)
        return path

    def get_data_dir(self) -> Path:
        return self._data_dir


# Instance globale conforme à la conception
data_manager = DataManager()
