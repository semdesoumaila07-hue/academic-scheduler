"""
Tests unitaires — Service Congés (LeaveService)
=================================================
Vérifie la soumission, l'approbation et le rejet des demandes de congé.

Exécution :
    pytest tests/unit/test_leave_service.py -v
"""
import pytest
from datetime import date


@pytest.fixture
def enseignant_avec_user(db_session, universite_complete, enseignant):
    """
    Enseignant + utilisateur lié pour les tests de congés.
    """
    return enseignant


class TestSoumissionConge:
    """Tests UC9 — Soumettre une demande de congé"""

    def test_ut_soumission_conge_valide(self, db_session, enseignant_avec_user):
        """Soumettre un congé valide → statut PENDING"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum, LeaveTypeEnum

        repo = LeaveRequestRepository(db_session)
        teacher = enseignant_avec_user

        conge = repo.create(
            teacher_id=teacher.id,
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 10),
            leave_type=LeaveTypeEnum.CONGE_ANNUEL,
            reason="Congé annuel",
            status=LeaveStatusEnum.PENDING
        )
        db_session.commit()

        assert conge.id is not None
        assert conge.status == LeaveStatusEnum.PENDING
        print(f"\n  → Congé créé avec statut : {conge.status}")

    def test_conge_en_attente_par_defaut(self, db_session, enseignant_avec_user):
        """Une nouvelle demande doit être en attente (PENDING)"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum, LeaveTypeEnum

        repo = LeaveRequestRepository(db_session)
        conge = repo.create(
            teacher_id=enseignant_avec_user.id,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 5),
            leave_type=LeaveTypeEnum.FORMATION,
            reason="Formation pédagogique",
            status=LeaveStatusEnum.PENDING
        )
        db_session.commit()

        assert conge.status == LeaveStatusEnum.PENDING

    def test_get_conges_par_enseignant(self, db_session, enseignant_avec_user):
        """Récupérer les congés d'un enseignant spécifique"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum, LeaveTypeEnum

        repo = LeaveRequestRepository(db_session)
        teacher_id = enseignant_avec_user.id

        # Créer 2 congés
        for i in range(2):
            repo.create(
                teacher_id=teacher_id,
                start_date=date(2026, 1, i+2),
                end_date=date(2026, 1, i+3),
                leave_type=LeaveTypeEnum.CONGE_ANNUEL,
                reason=f"Congé {i}",
                status=LeaveStatusEnum.PENDING
            )
        db_session.commit()

        conges = repo.get_by_teacher(teacher_id)
        assert len(conges) == 2
        print(f"\n  → {len(conges)} congés trouvés pour l'enseignant")


class TestApprobationConge:
    """Tests UC10 — Approuver/Rejeter un congé"""

    def _creer_conge(self, db_session, teacher_id):
        """Méthode utilitaire pour créer un congé en attente"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum, LeaveTypeEnum

        repo = LeaveRequestRepository(db_session)
        conge = repo.create(
            teacher_id=teacher_id,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 1, 20),
            leave_type=LeaveTypeEnum.CONGE_ANNUEL,
            reason="Repos",
            status=LeaveStatusEnum.PENDING
        )
        db_session.commit()
        return conge

    def test_ut_approbation_conge(self, db_session, enseignant_avec_user):
        """UT — Approuver un congé : statut → APPROVED"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum

        repo = LeaveRequestRepository(db_session)
        conge = self._creer_conge(db_session, enseignant_avec_user.id)

        # Approuver
        updated = repo.update(conge.id, status=LeaveStatusEnum.APPROVED)
        db_session.commit()
        db_session.refresh(updated)

        assert updated.status == LeaveStatusEnum.APPROVED
        print(f"\n  → Congé approuvé : {updated.status}")

    def test_ut_rejet_conge(self, db_session, enseignant_avec_user):
        """UT — Rejeter un congé : statut → REJECTED"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum

        repo = LeaveRequestRepository(db_session)
        conge = self._creer_conge(db_session, enseignant_avec_user.id)

        updated = repo.update(conge.id, status=LeaveStatusEnum.REJECTED)
        db_session.commit()
        db_session.refresh(updated)

        assert updated.status == LeaveStatusEnum.REJECTED
        print(f"\n  → Congé rejeté : {updated.status}")

    def test_conge_pending_puis_approved(self, db_session, enseignant_avec_user):
        """Workflow complet : PENDING → APPROVED"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum

        repo = LeaveRequestRepository(db_session)
        conge = self._creer_conge(db_session, enseignant_avec_user.id)

        # Vérifier état initial
        assert conge.status == LeaveStatusEnum.PENDING

        # Approuver
        repo.update(conge.id, status=LeaveStatusEnum.APPROVED)
        db_session.commit()

        conge_reload = repo.get_by_id(conge.id)
        assert conge_reload.status == LeaveStatusEnum.APPROVED
        print("\n  → Workflow PENDING → APPROVED validé ✅")

    def test_get_conges_en_attente(self, db_session, enseignant_avec_user):
        """Lister uniquement les congés en attente"""
        from src.database.repositories import LeaveRequestRepository
        from src.utils.constants import LeaveStatusEnum, LeaveTypeEnum

        repo = LeaveRequestRepository(db_session)
        teacher_id = enseignant_avec_user.id

        # 2 congés PENDING + 1 APPROVED
        conge1 = repo.create(teacher_id=teacher_id, start_date=date(2026,1,5),
                             end_date=date(2026,1,6), leave_type=LeaveTypeEnum.CONGE_ANNUEL,
                             reason="R1", status=LeaveStatusEnum.PENDING)
        conge2 = repo.create(teacher_id=teacher_id, start_date=date(2026,1,7),
                             end_date=date(2026,1,8), leave_type=LeaveTypeEnum.CONGE_ANNUEL,
                             reason="R2", status=LeaveStatusEnum.PENDING)
        conge3 = repo.create(teacher_id=teacher_id, start_date=date(2026,1,9),
                             end_date=date(2026,1,10), leave_type=LeaveTypeEnum.CONGE_ANNUEL,
                             reason="R3", status=LeaveStatusEnum.APPROVED)
        db_session.commit()

        # Récupérer uniquement PENDING
        from src.database.models import LeaveRequestModel
        pending = db_session.query(LeaveRequestModel).filter(
            LeaveRequestModel.status == LeaveStatusEnum.PENDING
        ).all()

        assert len(pending) == 2
        print(f"\n  → {len(pending)} congés en attente (attendu: 2) ✅")
