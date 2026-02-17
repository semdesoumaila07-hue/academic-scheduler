"""
Charge et exporte la configuration des calendriers (jours fériés, vacances) via calendrier.xml.

Format XML attendu : voir config/calendrier.xml
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import date

# Chemin par défaut du fichier calendrier (depuis la racine du projet)
def _default_calendar_path() -> Path:
    base = Path(__file__).resolve().parent.parent.parent
    return base / "config" / "calendrier.xml"


def load_calendar_xml(path: Path = None) -> List[Dict[str, Any]]:
    """
    Charge un fichier calendrier.xml et retourne la liste des calendriers
    (chacun avec jours_feries et periodes_vacances).

    Returns:
        Liste de dicts :
        - nom, annee_academique, date_debut, date_fin, heures_par_jour, nombre_semestres
        - jours_feries: list of {nom, date, recurrent, description}
        - periodes_vacances: list of {nom, date_debut, date_fin, type, description}
    """
    if path is None:
        path = _default_calendar_path()
    path = Path(path)
    if not path.exists():
        return []

    tree = ET.parse(path)
    root = tree.getroot()

    if root.tag != "calendriers":
        return []

    result = []
    for cal in root.findall("calendrier"):
        name_el = cal.find("nom")
        year_el = cal.find("annee_academique")
        start_el = cal.find("date_debut")
        end_el = cal.find("date_fin")
        hours_el = cal.find("heures_par_jour")
        sem_el = cal.find("nombre_semestres")

        if name_el is None or year_el is None or start_el is None or end_el is None:
            continue

        try:
            start_date = date.fromisoformat(start_el.text.strip())
            end_date = date.fromisoformat(end_el.text.strip())
        except (ValueError, AttributeError):
            continue

        entry = {
            "nom": name_el.text.strip() if name_el.text else "",
            "annee_academique": year_el.text.strip() if year_el.text else "",
            "date_debut": start_date,
            "date_fin": end_date,
            "heures_par_jour": int(hours_el.text) if hours_el is not None and hours_el.text else 8,
            "nombre_semestres": int(sem_el.text) if sem_el is not None and sem_el.text else 2,
            "jours_feries": [],
            "periodes_vacances": [],
        }

        for jf in cal.findall(".//jours_feries/jour_ferie") or cal.findall("jours_feries/jour_ferie"):
            jf_children = list(jf)
            jf_map = {c.tag: c for c in jf_children}
            nom_el = jf_map.get("nom")
            date_el = jf_map.get("date")
            rec_el = jf_map.get("recurrent")
            desc_el = jf_map.get("description")
            if not date_el or not date_el.text:
                continue
            try:
                jf_date = date.fromisoformat(date_el.text.strip())
            except ValueError:
                continue
            entry["jours_feries"].append({
                "nom": nom_el.text.strip() if nom_el is not None and nom_el.text else "Sans nom",
                "date": jf_date,
                "recurrent": (rec_el.text or "").strip().lower() in ("1", "true", "oui", "yes"),
                "description": desc_el.text.strip() if desc_el is not None and desc_el.text else None,
            })

        # support both direct children and nested
        jf_container = cal.find("jours_feries")
        if jf_container is not None and not entry["jours_feries"]:
            for jf in jf_container.findall("jour_ferie"):
                jf_map = {c.tag: c for c in jf}
                nom_el = jf_map.get("nom")
                date_el = jf_map.get("date")
                rec_el = jf_map.get("recurrent")
                desc_el = jf_map.get("description")
                if not date_el or not date_el.text:
                    continue
                try:
                    jf_date = date.fromisoformat(date_el.text.strip())
                except ValueError:
                    continue
                entry["jours_feries"].append({
                    "nom": nom_el.text.strip() if nom_el is not None and nom_el.text else "Sans nom",
                    "date": jf_date,
                    "recurrent": (rec_el.text or "").strip().lower() in ("1", "true", "oui", "yes"),
                    "description": desc_el.text.strip() if desc_el is not None and desc_el.text else None,
                })

        for pv in cal.findall("periodes_vacances/periode") or cal.findall("periodes_vacances/periode"):
            pv_children = list(pv)
            pv_map = {c.tag: c for c in pv_children}
            nom_el = pv_map.get("nom")
            ddeb = pv_map.get("date_debut")
            dfin = pv_map.get("date_fin")
            type_el = pv_map.get("type")
            desc_el = pv_map.get("description")
            if not ddeb or not ddeb.text or not dfin or not dfin.text:
                continue
            try:
                start_p = date.fromisoformat(ddeb.text.strip())
                end_p = date.fromisoformat(dfin.text.strip())
            except ValueError:
                continue
            type_val = (type_el.text or "NOEL").strip().upper() if type_el is not None else "NOEL"
            if type_val not in ("NOEL", "PAQUES", "ETE", "TOUSSAINT"):
                type_val = "NOEL"
            entry["periodes_vacances"].append({
                "nom": nom_el.text.strip() if nom_el is not None and nom_el.text else "Vacances",
                "date_debut": start_p,
                "date_fin": end_p,
                "type": type_val,
                "description": desc_el.text.strip() if desc_el is not None and desc_el.text else None,
            })

        pv_container = cal.find("periodes_vacances")
        if pv_container is not None and not entry["periodes_vacances"]:
            for pv in pv_container.findall("periode"):
                pv_map = {c.tag: c for c in pv}
                nom_el = pv_map.get("nom")
                ddeb = pv_map.get("date_debut")
                dfin = pv_map.get("date_fin")
                type_el = pv_map.get("type")
                desc_el = pv_map.get("description")
                if not ddeb or not ddeb.text or not dfin or not dfin.text:
                    continue
                try:
                    start_p = date.fromisoformat(ddeb.text.strip())
                    end_p = date.fromisoformat(dfin.text.strip())
                except ValueError:
                    continue
                type_val = (type_el.text or "NOEL").strip().upper() if type_el is not None else "NOEL"
                if type_val not in ("NOEL", "PAQUES", "ETE", "TOUSSAINT"):
                    type_val = "NOEL"
                entry["periodes_vacances"].append({
                    "nom": nom_el.text.strip() if nom_el is not None and nom_el.text else "Vacances",
                    "date_debut": start_p,
                    "date_fin": end_p,
                    "type": type_val,
                    "description": desc_el.text.strip() if desc_el is not None and desc_el.text else None,
                })

        result.append(entry)
    return result


def import_calendar_xml_to_db(session, path: Path = None) -> Dict[str, Any]:
    """
    Importe le contenu d'un calendrier.xml dans la base de données.
    Crée ou met à jour le calendrier académique et ses jours fériés / périodes de vacances.

    Args:
        session: Session SQLAlchemy
        path: Chemin vers calendrier.xml (défaut: config/calendrier.xml)

    Returns:
        Dict avec 'success', 'created', 'updated', 'errors'
    """
    from ..database.repositories import CalendarRepository, HolidayRepository, VacationPeriodRepository
    from ..database.models import HolidayModel, VacationPeriodModel, VacationTypeEnum

    data = load_calendar_xml(path)
    calendar_repo = CalendarRepository(session)
    holiday_repo = HolidayRepository(session)
    vacation_repo = VacationPeriodRepository(session)

    created = 0
    updated = 0
    errors = []

    for cal_data in data:
        try:
            existing = calendar_repo.get_by_academic_year(cal_data["annee_academique"])
            if existing:
                existing.name = cal_data["nom"]
                existing.start_date = cal_data["date_debut"]
                existing.end_date = cal_data["date_fin"]
                existing.hours_per_day = cal_data["heures_par_jour"]
                existing.semester_count = cal_data["nombre_semestres"]
                session.commit()
                session.refresh(existing)
                cal_id = existing.id
                updated += 1
            else:
                cal = calendar_repo.create(
                    name=cal_data["nom"],
                    academic_year=cal_data["annee_academique"],
                    start_date=cal_data["date_debut"],
                    end_date=cal_data["date_fin"],
                    hours_per_day=cal_data["heures_par_jour"],
                    semester_count=cal_data["nombre_semestres"],
                )
                cal_id = cal.id
                created += 1

            # Supprimer anciens jours fériés et périodes pour ce calendrier (réimport = remplacement)
            for h in holiday_repo.get_by_calendar(cal_id):
                session.delete(h)
            for v in vacation_repo.get_by_calendar(cal_id):
                session.delete(v)
            session.commit()

            for jf in cal_data["jours_feries"]:
                holiday_repo.create(
                    name=jf["nom"],
                    date=jf["date"],
                    is_recurring=jf["recurrent"],
                    calendar_id=cal_id,
                    description=jf.get("description"),
                )
            type_map = {
                "NOEL": VacationTypeEnum.NOEL,
                "PAQUES": VacationTypeEnum.PAQUES,
                "ETE": VacationTypeEnum.ETE,
                "TOUSSAINT": VacationTypeEnum.TOUSSAINT,
            }
            for pv in cal_data["periodes_vacances"]:
                vacation_repo.create(
                    name=pv["nom"],
                    start_date=pv["date_debut"],
                    end_date=pv["date_fin"],
                    type=type_map.get(pv["type"], VacationTypeEnum.NOEL),
                    calendar_id=cal_id,
                    description=pv.get("description"),
                )
            session.commit()
        except Exception as e:
            session.rollback()
            errors.append(f"{cal_data.get('annee_academique', '?')}: {e}")

    return {
        "success": len(errors) == 0,
        "created": created,
        "updated": updated,
        "errors": errors,
        "calendars_processed": len(data),
    }


def export_db_to_calendar_xml(session, path: Path) -> None:
    """
    Exporte les calendriers académiques (avec jours fériés et vacances) de la base vers un fichier XML.

    Args:
        session: Session SQLAlchemy
        path: Chemin du fichier XML de sortie
    """
    from ..database.repositories import CalendarRepository

    calendar_repo = CalendarRepository(session)
    path = Path(path)

    root = ET.Element("calendriers")

    for cal in calendar_repo.get_all(limit=1000):
        cal = calendar_repo.get_complete_calendar(cal.id) or cal
        cal_el = ET.SubElement(root, "calendrier")
        ET.SubElement(cal_el, "nom").text = cal.name or ""
        ET.SubElement(cal_el, "annee_academique").text = cal.academic_year or ""
        ET.SubElement(cal_el, "date_debut").text = (cal.start_date.isoformat() if cal.start_date else "")
        ET.SubElement(cal_el, "date_fin").text = (cal.end_date.isoformat() if cal.end_date else "")
        ET.SubElement(cal_el, "heures_par_jour").text = str(cal.hours_per_day or 8)
        ET.SubElement(cal_el, "nombre_semestres").text = str(cal.semester_count or 2)

        jf_container = ET.SubElement(cal_el, "jours_feries")
        for h in getattr(cal, "holidays", []) or []:
            jf = ET.SubElement(jf_container, "jour_ferie")
            ET.SubElement(jf, "nom").text = h.name or ""
            ET.SubElement(jf, "date").text = (h.date.isoformat() if h.date else "")
            ET.SubElement(jf, "recurrent").text = "true" if getattr(h, "is_recurring", False) else "false"
            if getattr(h, "description", None):
                ET.SubElement(jf, "description").text = h.description

        pv_container = ET.SubElement(cal_el, "periodes_vacances")
        for v in getattr(cal, "vacation_periods", []) or []:
            pv = ET.SubElement(pv_container, "periode")
            ET.SubElement(pv, "nom").text = v.name or ""
            ET.SubElement(pv, "date_debut").text = (v.start_date.isoformat() if v.start_date else "")
            ET.SubElement(pv, "date_fin").text = (v.end_date.isoformat() if v.end_date else "")
            type_val = getattr(v.type, "value", str(v.type)) if hasattr(v, "type") else "NOEL"
            type_key = type_val.upper().replace(" ", "_")[:10]
            if "NOEL" in type_val.upper():
                type_key = "NOEL"
            elif "PAQUES" in type_val.upper():
                type_key = "PAQUES"
            elif "ETE" in type_val.upper():
                type_key = "ETE"
            elif "TOUSSAINT" in type_val.upper():
                type_key = "TOUSSAINT"
            else:
                type_key = "NOEL"
            ET.SubElement(pv, "type").text = type_key
            if getattr(v, "description", None):
                ET.SubElement(pv, "description").text = v.description

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(
        path,
        encoding="utf-8",
        xml_declaration=True,
        default_namespace=None,
        method="xml",
    )


def get_default_calendar_path() -> Path:
    """Retourne le chemin par défaut du fichier calendrier.xml."""
    return _default_calendar_path()
