"""
Manager pour la gestion de la structure universitaire.

Gère les universités, UFR, programmes, cohortes et étudiants.
"""
from typing import List, Optional, Dict
from datetime import date
from sqlalchemy.orm import Session

from ..database.repositories import (
    UniversityRepository, UFRRepository, ProgramRepository,
    CohortRepository, StudentRepository
)
from ..services.auth_service import require_permission
from ..database.models import (
    UniversityModel, UFRModel, ProgramModel, CohortModel, StudentModel,
    ProgramLevelEnum
)
from ..utils.constants import ProgramLevel
from ..entité import University, UFR, Program, Cohort, Student


class StructureManager:
    """
    Manager pour la gestion de la structure universitaire.
    
    Attributes:
        session: Session de base de données
    """
    
    def __init__(self, session: Session):
        """
        Initialise le manager de structure.
        
        Args:
            session: Session de base de données
        """
        self.session = session
        self.university_repo = UniversityRepository(session)
        self.ufr_repo = UFRRepository(session)
        self.program_repo = ProgramRepository(session)
        self.cohort_repo = CohortRepository(session)
        self.student_repo = StudentRepository(session)
    
    # ==================== UNIVERSITÉS ====================
    
<<<<<<< HEAD
    def create_university(self, name: str, code: str, address: str, 
                         city: str, country: str = "Burkina Faso", current_user=None) -> Dict:
=======
    @require_permission('manage_structure')
    def create_university(self, name: str, code: str, address: str, 
                         city: str, country: str = "Burkina Faso") -> Dict:
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        """
        Crée une nouvelle université.
        
        Args:
            name: Nom de l'université
            code: Code unique
            address: Adresse
            city: Ville
            country: Pays
            
        Returns:
            Dictionnaire avec le résultat
        """
        # Vérifier si le code existe déjà
        existing = self.university_repo.get_by_code(code)
        if existing:
            return {
                'success': False,
                'error': f'Une université avec le code {code} existe déjà'
            }
        
        # Créer l'entité et valider
        university = University(
            name=name, code=code, address=address,
            city=city, country=country
        )
        
        is_valid, error = university.validate()
        if not is_valid:
            return {'success': False, 'error': error}
        
        # Créer dans la base de données
        university_model = self.university_repo.create(
            name=name, code=code, address=address,
            city=city, country=country
        )
        
        return {
            'success': True,
            'university_id': university_model.id,
            'message': f'Université {name} créée avec succès'
        }
    
    def get_all_universities(self) -> List[UniversityModel]:
        """Récupère toutes les universités."""
        return self.university_repo.get_all()
    
    def get_university_structure(self, university_id: int) -> Dict:
        """
        Récupère la structure complète d'une université.
        
        Args:
            university_id: ID de l'université
            
        Returns:
            Dictionnaire avec la structure
        """
        university = self.university_repo.get_with_ufrs(university_id)
        
        if not university:
            return {'error': 'Université introuvable'}
        
        ufrs_data = []
        for ufr in university.ufrs:
            programs = self.program_repo.get_by_ufr(ufr.id)
            ufrs_data.append({
                'id': ufr.id,
                'name': ufr.name,
                'code': ufr.code,
                'director': ufr.director,
                'programs_count': len(programs)
            })
        
        return {
            'id': university.id,
            'name': university.name,
            'code': university.code,
            'city': university.city,
            'ufrs': ufrs_data,
            'ufrs_count': len(ufrs_data)
        }
    
    # ==================== UFR ====================
    
<<<<<<< HEAD
    def create_ufr(self, name: str, code: str, director: str, 
                   university_id: int, current_user=None) -> Dict:
=======
    @require_permission('manage_structure')
    def create_ufr(self, name: str, code: str, director: str, 
                   university_id: int) -> Dict:
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        """
        Crée une nouvelle UFR.
        
        Args:
            name: Nom de l'UFR
            code: Code unique
            director: Nom du directeur
            university_id: ID de l'université
            
        Returns:
            Dictionnaire avec le résultat
        """
        # Vérifier que l'université existe
        university = self.university_repo.get_by_id(university_id)
        if not university:
            return {'success': False, 'error': 'Université introuvable'}
        
        # Vérifier si le code existe déjà
        existing = self.ufr_repo.get_by_code(code)
        if existing:
            return {
                'success': False,
                'error': f'Une UFR avec le code {code} existe déjà'
            }
        
        # Créer l'entité et valider
        ufr = UFR(name=name, code=code, director=director, university_id=university_id)
        is_valid, error = ufr.validate()
        if not is_valid:
            return {'success': False, 'error': error}
        
        # Créer dans la base de données
        ufr_model = self.ufr_repo.create(
            name=name, code=code, director=director, university_id=university_id
        )
        
        return {
            'success': True,
            'ufr_id': ufr_model.id,
            'message': f'UFR {name} créée avec succès'
        }
    
    def get_ufrs_by_university(self, university_id: int) -> List[UFRModel]:
        """Récupère toutes les UFR d'une université."""
        return self.ufr_repo.get_by_university(university_id)
    
    # ==================== PROGRAMMES ====================
    
<<<<<<< HEAD
    def create_program(self, name: str, code: str, level: ProgramLevelEnum,
                      duration_years: int, ufr_id: int, current_user=None) -> Dict:
=======
    @require_permission('manage_structure')
    def create_program(self, name: str, code: str, level: ProgramLevelEnum,
                      duration_years: int, ufr_id: int) -> Dict:
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        """
        Crée un nouveau programme.
        
        Args:
            name: Nom du programme
            code: Code unique
            level: Niveau (enum)
            duration_years: Durée en années
            ufr_id: ID de l'UFR
            
        Returns:
            Dictionnaire avec le résultat
        """
        # Vérifier que l'UFR existe
        ufr = self.ufr_repo.get_by_id(ufr_id)
        if not ufr:
            return {'success': False, 'error': 'UFR introuvable'}
        
        # Vérifier si le code existe déjà
        existing = self.program_repo.get_by_code(code)
        if existing:
            return {
                'success': False,
                'error': f'Un programme avec le code {code} existe déjà'
            }
        
        # Créer l'entité et valider (convertir ProgramLevelEnum vers ProgramLevel)
        level_for_entity = ProgramLevel(level.value) if hasattr(level, 'value') else level
        program = Program(
            name=name, code=code, level=level_for_entity,
            duration_years=duration_years, ufr_id=ufr_id
        )
        is_valid, error = program.validate()
        if not is_valid:
            return {'success': False, 'error': error}
        
        # Créer dans la base de données
        program_model = self.program_repo.create(
            name=name, code=code, level=level,
            duration_years=duration_years, ufr_id=ufr_id
        )
        
        return {
            'success': True,
            'program_id': program_model.id,
            'message': f'Programme {name} créé avec succès'
        }
    
    def get_programs_by_ufr(self, ufr_id: int) -> List[ProgramModel]:
        """Récupère tous les programmes d'une UFR."""
        return self.program_repo.get_by_ufr(ufr_id)
    
    def get_programs_by_level(self, level: ProgramLevelEnum) -> List[ProgramModel]:
        """Récupère tous les programmes d'un niveau donné."""
        return self.program_repo.get_by_level(level)
    
    # ==================== COHORTES ====================
    
<<<<<<< HEAD
    def create_cohort(self, name: str, academic_year: str, semester: int,
                     student_count: int, program_id: int, 
                     start_date: date, end_date: date, current_user=None) -> Dict:
=======
    @require_permission('manage_structure')
    def create_cohort(self, name: str, academic_year: str, semester: int,
                     student_count: int, program_id: int, 
                     start_date: date, end_date: date) -> Dict:
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        """
        Crée une nouvelle cohorte.
        
        Args:
            name: Nom de la cohorte
            academic_year: Année académique (ex: "2025-2026")
            semester: Semestre (1 ou 2)
            student_count: Nombre d'étudiants
            program_id: ID du programme
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire avec le résultat
        """
        # Vérifier que le programme existe
        program = self.program_repo.get_by_id(program_id)
        if not program:
            return {'success': False, 'error': 'Programme introuvable'}
        
        # Créer l'entité et valider
        cohort = Cohort(
            name=name, academic_year=academic_year, semester=semester,
            student_count=student_count, program_id=program_id,
            start_date=start_date, end_date=end_date
        )
        is_valid, error = cohort.validate()
        if not is_valid:
            return {'success': False, 'error': error}
        
        # Créer dans la base de données
        cohort_model = self.cohort_repo.create(
            name=name, academic_year=academic_year, semester=semester,
            student_count=student_count, program_id=program_id,
            start_date=start_date, end_date=end_date
        )
        
        return {
            'success': True,
            'cohort_id': cohort_model.id,
            'message': f'Cohorte {name} créée avec succès'
        }
    
    def get_cohorts_by_program(self, program_id: int) -> List[CohortModel]:
        """Récupère toutes les cohortes d'un programme."""
        return self.cohort_repo.get_by_program(program_id)
    
    def get_active_cohorts(self, reference_date: date = None) -> List[CohortModel]:
        """Récupère les cohortes actives."""
        return self.cohort_repo.get_active_cohorts(reference_date)
    
    def get_cohort_info(self, cohort_id: int) -> Dict:
        """
        Récupère les informations complètes d'une cohorte.
        
        Args:
            cohort_id: ID de la cohorte
            
        Returns:
            Dictionnaire avec les informations
        """
        cohort = self.cohort_repo.get_with_students(cohort_id)
        
        if not cohort:
            return {'error': 'Cohorte introuvable'}
        
        program = self.program_repo.get_by_id(cohort.program_id)
        
        return {
            'id': cohort.id,
            'name': cohort.name,
            'academic_year': cohort.academic_year,
            'semester': cohort.semester,
            'student_count': cohort.student_count,
            'actual_students': len(cohort.students),
            'start_date': cohort.start_date.isoformat(),
            'end_date': cohort.end_date.isoformat(),
            'program': {
                'id': program.id,
                'name': program.name,
                'level': program.level.value
            } if program else None
        }
    
    # ==================== ÉTUDIANTS ====================
    
<<<<<<< HEAD
    def create_student(self, full_name: str, student_id: str, email: str,
                      phone: str, birth_date: date, cohort_id: int, current_user=None) -> Dict:
=======
    @require_permission('manage_structure')
    def create_student(self, full_name: str, student_id: str, email: str,
                      phone: str, birth_date: date, cohort_id: int) -> Dict:
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        """
        Crée un nouveau étudiant.
        
        Args:
            full_name: Nom complet
            student_id: Matricule
            email: Email
            phone: Téléphone
            birth_date: Date de naissance
            cohort_id: ID de la cohorte
            
        Returns:
            Dictionnaire avec le résultat
        """
        # Vérifier que la cohorte existe
        cohort = self.cohort_repo.get_by_id(cohort_id)
        if not cohort:
            return {'success': False, 'error': 'Cohorte introuvable'}
        
        # Vérifier si le matricule existe déjà
        existing = self.student_repo.get_by_student_id(student_id)
        if existing:
            return {
                'success': False,
                'error': f'Un étudiant avec le matricule {student_id} existe déjà'
            }
        
        # Créer l'entité et valider
        student = Student(
            full_name=full_name, student_id=student_id, email=email,
            phone=phone, birth_date=birth_date, cohort_id=cohort_id
        )
        is_valid, error = student.validate()
        if not is_valid:
            return {'success': False, 'error': error}
        
        # Créer dans la base de données
        student_model = self.student_repo.create(
            full_name=full_name, student_id=student_id, email=email,
            phone=phone, birth_date=birth_date, cohort_id=cohort_id
        )
        
        return {
            'success': True,
            'student_id': student_model.id,
            'message': f'Étudiant {full_name} créé avec succès'
        }
    
    def get_students_by_cohort(self, cohort_id: int) -> List[StudentModel]:
        """Récupère tous les étudiants d'une cohorte."""
        return self.student_repo.get_by_cohort(cohort_id)
    
    def search_students(self, search_term: str) -> List[StudentModel]:
        """Recherche des étudiants par nom."""
        return self.student_repo.search_by_name(search_term)
    
    # ==================== STATISTIQUES ====================
    
    def get_global_statistics(self) -> Dict:
        """
        Calcule les statistiques globales de la structure.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        universities = self.university_repo.get_all()
        ufrs = self.ufr_repo.get_all()
        programs = self.program_repo.get_all()
        cohorts = self.cohort_repo.get_all()
        students = self.student_repo.get_all()
        
        active_cohorts = self.cohort_repo.get_active_cohorts()
        
        # Compter les étudiants par niveau
        licence_programs = self.program_repo.get_licence_programs()
        master_programs = self.program_repo.get_master_programs()
        
        return {
            'universities_count': len(universities),
            'ufrs_count': len(ufrs),
            'programs_count': len(programs),
            'licence_programs': len(licence_programs),
            'master_programs': len(master_programs),
            'cohorts_count': len(cohorts),
            'active_cohorts_count': len(active_cohorts),
            'students_count': len(students),
            'total_capacity': sum(c.student_count for c in cohorts)
        }