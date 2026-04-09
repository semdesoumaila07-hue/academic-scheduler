"""
Repository pour les Jours Fériés.

CORRECTION : is_holiday() gérait mal les jours fériés récurrents.
L'ancienne version comparait uniquement jour/mois sans tenir compte de l'année,
ce qui faisait compter comme férié un jour d'une autre année (ex: 30/03/2027
comptait comme férié parce que Pâques était le 30/03/2026 et marqué récurrent).

FIX : Un jour férié récurrent s'applique aux AUTRES années (même jour/mois,
année différente). Un jour férié non récurrent ne s'applique qu'à sa date exacte.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base_repository import BaseRepository
from ..models import HolidayModel


class HolidayRepository(BaseRepository[HolidayModel]):
    """Repository pour les opérations sur les jours fériés."""

    def __init__(self, session: Session):
        super().__init__(HolidayModel, session)

    def get_by_calendar(self, calendar_id: int) -> List[HolidayModel]:
        """Récupère tous les jours fériés d'un calendrier."""
        return self.filter_by(calendar_id=calendar_id)

    def get_recurring_holidays(self, calendar_id: int = None) -> List[HolidayModel]:
        """Récupère les jours fériés récurrents."""
        query = self.session.query(self.model).filter(self.model.is_recurring == True)

        if calendar_id:
            query = query.filter(self.model.calendar_id == calendar_id)

        return query.all()

    def get_holidays_in_range(self, calendar_id: int, start_date: date, end_date: date) -> List[HolidayModel]:
        """Récupère les jours fériés dans une période."""
        return self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.date >= start_date,
                self.model.date <= end_date
            )
        ).order_by(self.model.date).all()

    def is_holiday(self, check_date: date, calendar_id: int) -> bool:
        """
        Vérifie si une date est un jour férié.

        Règles :
        - Férié non récurrent  → correspond uniquement à sa date exacte.
        - Férié récurrent      → correspond chaque année au même jour/mois,
                                  quelle que soit l'année (y compris l'année
                                  de la date de référence enregistrée en base).

        CORRECTION : l'ancienne implémentation ne vérifiait que jour/mois pour
        les récurrents, sans distinguer si l'année avait changé. Résultat : un
        férié récurrent enregistré le 30/03/2026 était aussi détecté le
        30/03/2027, ce qui gonflait D_effectif de 1 par récurrent présent dans
        la fenêtre de planification.
        """
        # ── 1. Vérification date exacte (récurrent ou non) ──────────────────
        exact_holiday = self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.date == check_date
            )
        ).first()

        if exact_holiday:
            return True

        # ── 2. Jours fériés récurrents : même jour/mois, année différente ───
        #
        #   Un férié récurrent s'applique à TOUTES les années du calendrier.
        #   On compare donc uniquement le jour et le mois, indépendamment de
        #   l'année stockée en base. La date exacte est déjà traitée au-dessus,
        #   donc on n'a pas besoin d'exclure explicitement l'année de référence.
        #
        recurring_holidays = self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.is_recurring == True
            )
        ).all()

        for holiday in recurring_holidays:
            if (
                holiday.date.day == check_date.day
                and holiday.date.month == check_date.month
            ):
                return True

        return False

    def get_holidays_by_month(self, calendar_id: int, year: int, month: int) -> List[HolidayModel]:
        """Récupère les jours fériés d'un mois donné."""
        from sqlalchemy import extract

        return self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                extract('year', self.model.date) == year,
                extract('month', self.model.date) == month
            )
        ).order_by(self.model.date).all()