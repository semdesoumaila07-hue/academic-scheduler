"""
Script pour créer des données de test.
"""
import sys
from pathlib import Path
from datetime import date, timedelta

# Ajouter src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.db_manager import db_manager
from database.repositories import (
    UniversityRepository,
    UFRRepository,
    ProgramRepository,
    CohortRepository,
    TeacherRepository,
    StudentRepository,
    ActivityRepository,
    CalendarRepository,
    HolidayRepository,
    VacationPeriodRepository
)
from utils.constants import (
    ProgramLevelEnum,
    ActivityTypeEnum,
    ActivityStatusEnum,
    TeacherStatusEnum,
    VacationTypeEnum
)

def create_test_data():
    """Crée des données de test complètes."""
    print("🔄 Création des données de test...")
    
    session = db_manager.get_session()
    
    try:
        # 1. Créer l'université
        print("1️⃣ Création de l'université...")
        univ_repo = UniversityRepository(session)
        university = univ_repo.create(
            name="Université Norbert Zongo",
            code="UNZ",
            address="Avenue de l'Indépendance",
            city="Ouagadougou",
            country="Burkina Faso"
        )
        
        # 2. Créer l'UFR
        print("2️⃣ Création de l'UFR...")
        ufr_repo = UFRRepository(session)
        ufr = ufr_repo.create(
            name="UFR Sciences Exactes et Appliquées",
            code="UFR-SEA",
            director="Pr. Jean-Baptiste OUEDRAOGO",
            university_id=university.id
        )
        
        # 3. Créer le programme
        print("3️⃣ Création du programme...")
        program_repo = ProgramRepository(session)
        program = program_repo.create(
            name="Licence Informatique",
            code="L3-INFO",
            level=ProgramLevelEnum.LICENCE_3,
            duration_years=1,
            ufr_id=ufr.id
        )
        
        # 4. Créer la cohorte
        print("4️⃣ Création de la cohorte...")
        cohort_repo = CohortRepository(session)
        cohort = cohort_repo.create(
            name="L3 Info 2025-2026",
            academic_year="2025-2026",
            semester=1,
            student_count=45,
            program_id=program.id,
            start_date=date(2025, 10, 1),
            end_date=date(2026, 3, 31)
        )
        
        # 5. Créer les enseignants
        print("5️⃣ Création des enseignants...")
        teacher_repo = TeacherRepository(session)
        
        teachers = []
        teachers_data = [
            ("Dr. Marie KABORE", "marie.kabore@unz.bf", "+226 70 12 34 56", "Algorithmique"),
            ("Dr. Moussa TRAORE", "moussa.traore@unz.bf", "+226 70 23 45 67", "Bases de données"),
            ("Dr. Fatimata SAWADOGO", "fatimata.sawadogo@unz.bf", "+226 70 34 56 78", "Réseaux informatiques"),
            ("Dr. Ibrahim OUATTARA", "ibrahim.ouattara@unz.bf", "+226 70 45 67 89", "Développement Web")
        ]
        
        for name, email, phone, speciality in teachers_data:
            teacher = teacher_repo.create(
                full_name=name,
                email=email,
                phone=phone,
                speciality=speciality,
                status=TeacherStatusEnum.PERMANENT,
                max_hours_per_week=40,
                max_hours_per_day=8
            )
            teachers.append(teacher)
        
        # 6. Créer des étudiants
        print("6️⃣ Création des étudiants...")
        student_repo = StudentRepository(session)
        
        students_data = [
            ("Aminata ZONGO", "L3INFO2025001", "aminata.zongo@unz.bf"),
            ("Boureima COMPAORE", "L3INFO2025002", "boureima.compaore@unz.bf"),
            ("Clarisse OUEDRAOGO", "L3INFO2025003", "clarisse.ouedraogo@unz.bf")
        ]
        
        for name, student_id, email in students_data:
            student_repo.create(
                full_name=name,
                student_id=student_id,
                email=email,
                phone="+226 70 00 00 00",
                birth_date=date(2003, 1, 1),
                cohort_id=cohort.id
            )
        
        # 7. Créer les activités
        print("7️⃣ Création des activités...")
        activity_repo = ActivityRepository(session)
        
        activities_data = [
            ("Algorithmique avancée", "ALGO-301", ActivityTypeEnum.COURS, 30, teachers[0].id, 8),
            ("TD Algorithmique", "ALGO-TD-301", ActivityTypeEnum.TD, 20, teachers[0].id, 7),
            ("Bases de données", "BD-301", ActivityTypeEnum.COURS, 25, teachers[1].id, 8),
            ("TP Bases de données", "BD-TP-301", ActivityTypeEnum.TP, 20, teachers[1].id, 7),
            ("Réseaux informatiques", "RESEAUX-301", ActivityTypeEnum.COURS, 25, teachers[2].id, 7),
            ("Développement Web", "WEB-301", ActivityTypeEnum.COURS, 30, teachers[3].id, 8)
        ]
        
        for name, code, activity_type, volume, teacher_id, priority in activities_data:
            activity_repo.create(
                name=name,
                code=code,
                type=activity_type,
                volume_hours=volume,
                hours_done=0,
                cohort_id=cohort.id,
                teacher_id=teacher_id,
                activation_date=cohort.start_date,
                deadline=cohort.end_date,
                priority=priority,
                status=ActivityStatusEnum.PENDING,
                charge_factor=0.0
            )
        
        # 8. Créer le calendrier académique
        print("8️⃣ Création du calendrier académique...")
        calendar_repo = CalendarRepository(session)
        calendar = calendar_repo.create(
            name="Calendrier 2025-2026",
            academic_year="2025-2026",
            start_date=date(2025, 10, 1),
            end_date=date(2026, 7, 31),
            hours_per_day=8
        )
        
        # 9. Créer les jours fériés
        print("9️⃣ Création des jours fériés...")
        holiday_repo = HolidayRepository(session)
        
        holidays_data = [
            ("Jour de l'An", date(2026, 1, 1), True),
            ("Fête du Travail", date(2026, 5, 1), True),
            ("Fête Nationale", date(2026, 8, 5), True),
            ("Noël", date(2025, 12, 25), True)
        ]
        
        for name, holiday_date, is_recurring in holidays_data:
            holiday_repo.create(
                name=name,
                date=holiday_date,
                is_recurring=is_recurring,
                calendar_id=calendar.id
            )
        
        # 10. Créer les périodes de vacances
        print("🔟 Création des périodes de vacances...")
        vacation_repo = VacationPeriodRepository(session)
        
        vacations_data = [
            ("Vacances de Noël", date(2025, 12, 20), date(2026, 1, 5), VacationTypeEnum.NOEL),
            ("Vacances de Pâques", date(2026, 4, 10), date(2026, 4, 20), VacationTypeEnum.PAQUES)
        ]
        
        for name, start, end, vac_type in vacations_data:
            vacation_repo.create(
                name=name,
                start_date=start,
                end_date=end,
                type=vac_type,
                calendar_id=calendar.id
            )
        
        # Commit
        session.commit()
        
        print("\n✅ Données de test créées avec succès !")
        print(f"   • 1 Université")
        print(f"   • 1 UFR")
        print(f"   • 1 Programme")
        print(f"   • 1 Cohorte (45 étudiants)")
        print(f"   • 4 Enseignants")
        print(f"   • 3 Étudiants")
        print(f"   • 6 Activités")
        print(f"   • 1 Calendrier académique")
        print(f"   • 4 Jours fériés")
        print(f"   • 2 Périodes de vacances")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    create_test_data()