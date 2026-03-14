"""
Repository pour les permissions.
"""
from typing import Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import PermissionModel


class PermissionRepository(BaseRepository[PermissionModel]):
    """Repository pour les opérations sur les permissions."""

    def __init__(self, session: Session):
        super().__init__(PermissionModel, session)

    def get_by_name(self, name: str) -> Optional[PermissionModel]:
        return self.first_by(name=name)
