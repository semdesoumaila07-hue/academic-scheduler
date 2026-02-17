"""
Fonctions utilitaires.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
import json


def is_workday(date_obj: date, holidays: List[date] = None) -> bool:
    """
    Vérifie si une date est un jour ouvrable.
    
    Args:
        date_obj: Date à vérifier
        holidays: Liste des jours fériés
        
    Returns:
        True si c'est un jour ouvrable, False sinon
    """
    # Vérifier si c'est un weekend
    if date_obj.weekday() >= 5:  # Samedi ou Dimanche
        return False
    
    # Vérifier si c'est un jour férié
    if holidays and date_obj in holidays:
        return False
    
    return True


def count_workdays(start_date: date, end_date: date, holidays: List[date] = None) -> int:
    """
    Compte le nombre de jours ouvrables entre deux dates.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        holidays: Liste des jours fériés
        
    Returns:
        Nombre de jours ouvrables
    """
    count = 0
    current_date = start_date
    
    while current_date <= end_date:
        if is_workday(current_date, holidays):
            count += 1
        current_date += timedelta(days=1)
    
    return count


def get_academic_year(date_obj: date) -> str:
    """
    Retourne l'année académique pour une date donnée.
    
    Args:
        date_obj: Date
        
    Returns:
        Année académique au format "2025-2026"
    """
    if date_obj.month >= 9:  # Septembre ou après
        return f"{date_obj.year}-{date_obj.year + 1}"
    else:
        return f"{date_obj.year - 1}-{date_obj.year}"


def format_duration(hours: float) -> str:
    """
    Formate une durée en heures en format lisible.
    
    Args:
        hours: Durée en heures
        
    Returns:
        Durée formatée (ex: "2h30")
    """
    h = int(hours)
    m = int((hours - h) * 60)
    
    if m == 0:
        return f"{h}h"
    return f"{h}h{m:02d}"


def parse_time_slot(time_str: str) -> tuple:
    """
    Parse une chaîne de créneau horaire.
    
    Args:
        time_str: Chaîne au format "08:00-10:00"
        
    Returns:
        Tuple (heure_debut, heure_fin)
    """
    start_str, end_str = time_str.split("-")
    start_h, start_m = map(int, start_str.split(":"))
    end_h, end_m = map(int, end_str.split(":"))
    
    return (start_h + start_m/60, end_h + end_m/60)


def time_to_str(hour: float) -> str:
    """
    Convertit une heure décimale en format HH:MM.
    
    Args:
        hour: Heure décimale (ex: 8.5 pour 08:30)
        
    Returns:
        Heure au format "HH:MM"
    """
    h = int(hour)
    m = int((hour - h) * 60)
    return f"{h:02d}:{m:02d}"


def validate_email(email: str) -> bool:
    """
    Valide un format d'email.
    
    Args:
        email: Adresse email
        
    Returns:
        True si valide, False sinon
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def load_json_file(filepath: str) -> dict:
    """
    Charge un fichier JSON.
    
    Args:
        filepath: Chemin du fichier
        
    Returns:
        Dictionnaire Python
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: dict, filepath: str) -> None:
    """
    Sauvegarde des données dans un fichier JSON.
    
    Args:
        data: Données à sauvegarder
        filepath: Chemin du fichier
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Tronque un texte à une longueur maximale.
    
    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        
    Returns:
        Texte tronqué
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def generate_unique_code(prefix: str = "") -> str:
    """
    Génère un code unique.
    
    Args:
        prefix: Préfixe optionnel
        
    Returns:
        Code unique
    """
    import uuid
    code = str(uuid.uuid4())[:8].upper()
    return f"{prefix}{code}" if prefix else code