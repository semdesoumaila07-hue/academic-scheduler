"""
Script pour créer des données de test dans la base de données.

Ce script peuple la base de données avec des données réalistes
pour tester l'application.
"""
from datetime import date, time, timedelta
from src.database.db_manager import db_manager
from src.database.models import (
    UniversityModel, UFRModel, ProgramModel, CohortModel,
    TeacherModel, StudentModel, AcademicActivityModel,
    AcademicCalendarModel, HolidayModel, VacationPeriodModel,
    ProgramLevelEnum, TeacherStatusEnum, ActivityTypeEnum,
    ActivityStatusEnum, VacationTypeEnum
)


def create_test_data():
    """Crée les données de test."""
    print("🔄 Création des données de test...")
    
    # Initialiser la base de données
    db_manager.initialize()
    session = db_manager.get_session()
    
    try:
        # 1. Créer une université
        print("1️⃣ Création de l'université...")
        university = UniversityModel(
            name="Université Norbert Zongo",
            code="UNZ",
            address="Avenue Kwame N'Krumah",
            city="Ouagadougou",
            country="Burkina Faso"
        )
        session.add(university)
        session.flush()
        
        # 2. Créer une UFR
        print("2️⃣ Création de l'UFR...")
        ufr = UFRModel(
            name="UFR Sciences Exactes et Appliquées",
            code="UFR-SEA",
            director="Prof. Aminata OUEDRAOGO",
            university_id=university.id
        )
        session.add(ufr)
        session.flush()
        
        # 3. Créer un programme
        print("3️⃣ Création du programme...")
        program = ProgramModel(
            name="Licence Informatique",
            code="L3-INFO",
            level=ProgramLevelEnum.LICENCE_3,
            duration_years=1,
            ufr_id=ufr.id
        )
        session.add(program)
        session.flush()
        
        # 4. Créer une cohorte
        print("4️⃣ Création de la cohorte...")
        cohort = CohortModel(
            name="L3 Info 2025-2026",
            academic_year="2025-2026",
            semester=1,
            student_count=45,
            program_id=program.id,
            start_date=date(2025, 10, 1),
            end_date=date(2026, 3, 31)
        )
        session.add(cohort)
        session.flush()
        
        # 5. Créer des enseignants
        print("5️⃣ Création des enseignants...")
        teachers_data = [
            ("Dr. Marie KABORE", "marie.kabore@unz.bf", "+226 70 12 34 56", "Algorithmique"),
            ("Dr. Moussa TRAORE", "moussa.traore@unz.bf", "+226 70 23 45 67", "Bases de données"),
            ("Dr. Fatimata SAWADOGO", "fatimata.sawadogo@unz.bf", "+226 70 34 56 78", "Réseaux"),
            ("Dr. Ibrahim OUATTARA", "ibrahim.ouattara@unz.bf", "+226 70 45 67 89", "Développement Web"),
        ]
        
        teachers = []
        for name, email, phone, speciality in teachers_data:
            teacher = TeacherModel(
                full_name=name,
                email=email,
                phone=phone,
                speciality=speciality,
                status=TeacherStatusEnum.PERMANENT,
                max_hours_per_week=40,
                max_hours_per_day=8
            )
            session.add(teacher)
            teachers.append(teacher)
        
        session.flush()
        
        # 6. Créer des étudiants
        print("6️⃣ Création des étudiants...")
        students_data = [
            ("Abdoulaye DIALLO", "ET2025001", "abdoulaye.diallo@unz.bf", "+226 60 11 22 33", date(2004, 5, 15)),
            ("Aminata KONE", "ET2025002", "aminata.kone@unz.bf", "+226 60 22 33 44", date(2004, 8, 20)),
            ("Boureima OUEDRAOGO", "ET2025003", "boureima.ouedraogo@unz.bf", "+226 60 33 44 55", date(2003, 12, 10)),
        ]
        
        for name, student_id, email, phone, birth_date in students_data:
            student = StudentModel(
                full_name=name,
                student_id=student_id,
                email=email,
                phone=phone,
                birth_date=birth_date,
                cohort_id=cohort.id
            )
            session.add(student)
        
        session.flush()
        
        # 7. Créer des activités
        print("7️⃣ Création des activités...")
        activities_data = [
            ("Algorithmique avancée", "ALGO-301", ActivityTypeEnum.COURS, 30, 1, teachers[0].id, 8),
            ("TD Algorithmique", "ALGO-301-TD", ActivityTypeEnum.TD, 20, 1, teachers[0].id, 7),
            ("Bases de données", "BD-301", ActivityTypeEnum.COURS, 25, 1, teachers[1].id, 8),
            ("TP Bases de données", "BD-301-TP", ActivityTypeEnum.TP, 20, 1, teachers[1].id, 6),
            ("Réseaux informatiques", "RES-301", ActivityTypeEnum.COURS, 25, 1, teachers[2].id, 7),
            ("Développement Web", "WEB-301", ActivityTypeEnum.COURS, 30, 1, teachers[3].id, 9),
        ]
        
        today = date.today()
        activities = []
        for name, code, act_type, volume, cohort_id, teacher_id, priority in activities_data:
            activity = AcademicActivityModel(
                name=name,
                code=code,
                type=act_type,
                volume_hours=volume,
                hours_done=0,
                cohort_id=cohort.id,
                teacher_id=teacher_id,
                activation_date=today,
                deadline=today + timedelta(days=180),
                priority=priority,
                status=ActivityStatusEnum.PENDING,
                charge_factor=0.0
            )
            session.add(activity)
            activities.append(activity)
        
        session.flush()
        
        # 8. Créer un calendrier académique
        print("8️⃣ Création du calendrier académique...")
        calendar = AcademicCalendarModel(
            name="Calendrier 2025-2026",
            academic_year="2025-2026",
            start_date=date(2025, 10, 1),
            end_date=date(2026, 7, 31),
            hours_per_day=8
        )
        session.add(calendar)
        session.flush()
        
        # 9. Créer des jours fériés
        print("9️⃣ Création des jours fériés...")
        holidays_data = [
            ("Jour de l'An", date(2026, 1, 1), True),
            ("Fête du Travail", date(2026, 5, 1), True),
            ("Fête Nationale", date(2026, 8, 5), True),
            ("Noël", date(2026, 12, 25), True),
        ]
        
        for name, holiday_date, recurring in holidays_data:
            holiday = HolidayModel(
                name=name,
                date=holiday_date,
                is_recurring=recurring,
                calendar_id=calendar.id
            )
            session.add(holiday)
        
        session.flush()
        
        # 10. Créer des périodes de vacances
        print("🔟 Création des périodes de vacances...")
        vacations_data = [
            ("Vacances de Noël", date(2025, 12, 20), date(2026, 1, 5), VacationTypeEnum.NOEL),
            ("Vacances de Pâques", date(2026, 4, 10), date(2026, 4, 20), VacationTypeEnum.PAQUES),
        ]
        
        for name, start, end, vac_type in vacations_data:
            vacation = VacationPeriodModel(
                name=name,
                start_date=start,
                end_date=end,
                type=vac_type,
                calendar_id=calendar.id
            )
            session.add(vacation)
        
        session.flush()
        
        # Commit final
        session.commit()
        
        print("\n✅ Données de test créées avec succès !")
        print(f"   • 1 Université")
        print(f"   • 1 UFR")
        print(f"   • 1 Programme")
        print(f"   • 1 Cohorte (45 étudiants)")
        print(f"   • {len(teachers)} Enseignants")
        print(f"   • {len(students_data)} Étudiants")
        print(f"   • {len(activities)} Activités")
        print(f"   • 1 Calendrier académique")
        print(f"   • {len(holidays_data)} Jours fériés")
        print(f"   • {len(vacations_data)} Périodes de vacances")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des données : {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        db_manager.close()


if __name__ == "__main__":
    create_test_data()