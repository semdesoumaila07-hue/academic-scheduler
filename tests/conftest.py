"""
Fixtures partagées pour tous les tests.
Base SQLite en mémoire — créée et détruite à chaque test.
"""
import sys
import os
import pytest
from datetime import date, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import create_engine, event          # ← "event" ajouté
from sqlalchemy.orm import sessionmaker
from src.database.models import Base


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)

    # ── Activer les clés étrangères SQLite (désactivées par défaut) ──
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def universite_complete(db_session):
    from src.database.repositories import (
        UniversityRepository, UFRRepository,
        ProgramRepository, CohortRepository
    )
    from src.utils.constants import ProgramLevelEnum

    univ_repo   = UniversityRepository(db_session)
    ufr_repo    = UFRRepository(db_session)
    prog_repo   = ProgramRepository(db_session)
    cohort_repo = CohortRepository(db_session)

    univ = univ_repo.create(
        name="Université Norbert Zongo",
        code="UNZ",
        address="Avenue de l'Indépendance",
        city="Koudougou",
        country="Burkina Faso"
    )
    ufr = ufr_repo.create(
        name="UFR Sciences et Techniques",
        code="UFR-ST",
        director="Pr. KABORE",
        university_id=univ.id
    )
    programme = prog_repo.create(
        name="Licence Informatique",
        code="L3-INFO",
        level=ProgramLevelEnum.LICENCE_3,
        duration_years=1,
        ufr_id=ufr.id
    )
    cohorte = cohort_repo.create(
        name="L3 Info 2025-2026",
        academic_year="2025-2026",
        semester=1,
        student_count=45,
        program_id=programme.id,
        start_date=date(2025, 10, 1),
        end_date=date(2026, 2, 28)
    )
    db_session.commit()
    return {"univ": univ, "ufr": ufr, "programme": programme, "cohorte": cohorte}


@pytest.fixture
def enseignant(db_session):
    from src.database.repositories import TeacherRepository
    from src.utils.constants import TeacherStatusEnum

    repo = TeacherRepository(db_session)
    teacher = repo.create(
        full_name="Jean KABORE",
        email="j.kabore@unz.bf",
        phone="+226 70 00 00 00",
        speciality="Informatique",
        status=TeacherStatusEnum.PERMANENT,
        max_hours_per_week=20,
        max_hours_per_day=8
    )
    db_session.commit()
    return teacher