"""
Repository pour les rôles.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import RoleModel


class RoleRepository(BaseRepository[RoleModel]):
    """Repository pour les opérations sur les rôles."""

    def __init__(self, session: Session):
        super().__init__(RoleModel, session)

    def get_by_name(self, name: str) -> Optional[RoleModel]:
        return self.first_by(name=name)

    def list_roles(self) -> List[RoleModel]:
        return self.get_all()
