"""
Tests unitaires — Modèles SQLAlchemy
======================================
Vérifie les contraintes de la base de données (unicité, FK, CRUD).

Exécution :
    pytest tests/unit/test_models.py -v
"""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError


class TestUniversityModel:
    """Tests sur la table universities"""

    def test_creation_universite_valide(self, db_session):
        """Créer une université avec tous les champs requis"""
        from src.database.repositories import UniversityRepository
        repo = UniversityRepository(db_session)
        univ = repo.create(
            name="Université Norbert Zongo",
            code="UNZ",
            address="Koudougou",
            city="Koudougou",
            country="Burkina Faso"
        )
        db_session.commit()
        assert univ.id is not None
        assert univ.code == "UNZ"
        print(f"\n  → Université créée avec ID={univ.id}")

    def test_ut15_code_universite_unique(self, db_session):
        """UT-15 : Deux universités avec le même code → IntegrityError"""
        from src.database.repositories import UniversityRepository
        repo = UniversityRepository(db_session)

        repo.create(name="Univ A", code="UNZ",
                    address="Addr", city="Ville", country="Burkina Faso")
        db_session.commit()

        with pytest.raises(Exception):  # IntegrityError ou similaire
            repo.create(name="Univ B", code="UNZ",  # même code !
                        address="Addr2", city="Ville2", country="Burkina Faso")
            db_session.commit()
        print("\n  → Doublon de code correctement rejeté")

    def test_get_by_id(self, db_session):
        """Récupérer une université par son ID"""
        from src.database.repositories import UniversityRepository
        repo = UniversityRepository(db_session)
        univ = repo.create(name="UNZ Test", code="UNZT",
                           address="Addr", city="Ville", country="BF")
        db_session.commit()

        found = repo.get_by_id(univ.id)
        assert found is not None
        assert found.name == "UNZ Test"

    def test_update_universite(self, db_session):
        """Modifier le nom d'une université"""
        from src.database.repositories import UniversityRepository
        repo = UniversityRepository(db_session)
        univ = repo.create(name="Ancien Nom", code="XX1",
                           address="Addr", city="Ville", country="BF")
        db_session.commit()

        updated = repo.update(univ.id, name="Nouveau Nom")
        db_session.commit()
        assert updated.name == "Nouveau Nom"

    def test_delete_universite(self, db_session):
        """Supprimer une université sans UFR liée"""
        from src.database.repositories import UniversityRepository
        repo = UniversityRepository(db_session)
        univ = repo.create(name="À supprimer", code="DEL1",
                           address="Addr", city="Ville", country="BF")
        db_session.commit()
        univ_id = univ.id

        result = repo.delete(univ_id)
        db_session.commit()
        assert result == True
        assert repo.get_by_id(univ_id) is None

    def test_count_universites(self, db_session):
        """Compter les universités en base"""
        from src.database.repositories import UniversityRepository
        repo = UniversityRepository(db_session)
        assert repo.count() == 0

        repo.create(name="U1", code="U01", address="A", city="C", country="BF")
        repo.create(name="U2", code="U02", address="A", city="C", country="BF")
        db_session.commit()
        assert repo.count() == 2


class TestHierarchieComplete:
    """Tests sur la hiérarchie Université → UFR → Programme → Cohorte"""

    def test_creation_hierarchie_complete(self, universite_complete):
        """La fixture conftest crée toute la hiérarchie"""
        data = universite_complete
        assert data["univ"].id is not None
        assert data["ufr"].university_id == data["univ"].id
        assert data["programme"].ufr_id == data["ufr"].id
        assert data["cohorte"].program_id == data["programme"].id
        print(f"\n  → Hiérarchie : {data['univ'].code} → {data['ufr'].code} "
              f"→ {data['programme'].code} → {data['cohorte'].name}")

    def test_ut16_suppression_ufr_avec_programmes(self, db_session, universite_complete):
        """UT-16 : Supprimer une UFR qui a des programmes → doit échouer"""
        from src.database.repositories import UFRRepository
        ufr_repo = UFRRepository(db_session)

        with pytest.raises(Exception):
            ufr_repo.delete(universite_complete["ufr"].id)
            db_session.commit()
        print("\n  → Suppression d'UFR avec programmes correctement bloquée")

    def test_cohorte_liee_au_programme(self, db_session, universite_complete):
        """La cohorte doit référencer un programme existant"""
        cohorte = universite_complete["cohorte"]
        programme = universite_complete["programme"]
        assert cohorte.program_id == programme.id


class TestActivityModel:
    """Tests sur la table academic_activities"""

    def test_creation_activite_valide(self, db_session, universite_complete, enseignant):
        """Créer une activité avec tous les champs requis"""
        from src.database.repositories import ActivityRepository
        from src.utils.constants import ActivityTypeEnum, ActivityStatusEnum

        repo = ActivityRepository(db_session)
        cohorte = universite_complete["cohorte"]

        activite = repo.create(
            name="Algorithmique avancée",
            code="ALGO-301",
            type=ActivityTypeEnum.COURS_MAGISTRAL,
            volume_hours=30.0,
            hours_done=0.0,
            cohort_id=cohorte.id,
            teacher_id=enseignant.id,
            status=ActivityStatusEnum.PENDING
        )
        db_session.commit()

        assert activite.id is not None
        assert activite.volume_hours == 30.0
        assert activite.hours_done == 0.0
        print(f"\n  → Activité créée : {activite.name} (ID={activite.id})")

    def test_ut17_mise_a_jour_hours_done(self, db_session, universite_complete, enseignant):
        """UT-17 : Mettre à jour hours_done après planification"""
        from src.database.repositories import ActivityRepository
        from src.utils.constants import ActivityTypeEnum, ActivityStatusEnum

        repo = ActivityRepository(db_session)
        activite = repo.create(
            name="BD Test",
            code="BD-001",
            type=ActivityTypeEnum.TD,
            volume_hours=20.0,
            hours_done=0.0,
            cohort_id=universite_complete["cohorte"].id,
            teacher_id=enseignant.id,
            status=ActivityStatusEnum.PENDING
        )
        db_session.commit()

        # Simuler planification de 8h
        updated = repo.update(activite.id, hours_done=8.0)
        db_session.commit()

        db_session.refresh(updated)
        assert updated.hours_done == 8.0
        progression = (updated.hours_done / updated.volume_hours) * 100
        assert progression == 40.0
        print(f"\n  → hours_done mis à jour : 8h/20h = {progression:.0f}%")

    def test_get_activites_par_cohorte(self, db_session, universite_complete, enseignant):
        """Récupérer toutes les activités d'une cohorte"""
        from src.database.repositories import ActivityRepository
        from src.utils.constants import ActivityTypeEnum, ActivityStatusEnum

        repo = ActivityRepository(db_session)
        cohorte_id = universite_complete["cohorte"].id

        # Créer 3 activités
        for i in range(3):
            repo.create(
                name=f"Activite {i}",
                code=f"ACT-00{i}",
                type=ActivityTypeEnum.COURS_MAGISTRAL,
                volume_hours=20.0,
                hours_done=0.0,
                cohort_id=cohorte_id,
                teacher_id=enseignant.id,
                status=ActivityStatusEnum.PENDING
            )
        db_session.commit()

        activites = repo.get_by_cohort(cohorte_id)
        assert len(activites) == 3
        print(f"\n  → {len(activites)} activités trouvées pour la cohorte")
