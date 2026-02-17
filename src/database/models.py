"""
Modèles SQLAlchemy (ORM) pour toutes les entités.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, Time, 
    DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

# Base pour tous les modèles
Base = declarative_base()


# Enums
class ProgramLevelEnum(enum.Enum):
    """Niveaux de programmes."""
    LICENCE_1 = "Licence 1"
    LICENCE_2 = "Licence 2"
    LICENCE_3 = "Licence 3"
    MASTER_1 = "Master 1"
    MASTER_2 = "Master 2"
    DOCTORAT = "Doctorat"


class ActivityTypeEnum(enum.Enum):
    """Types d'activités académiques."""
    COURS_MAGISTRAL = "Cours Magistral"
    TD = "Travaux Dirigés"
    TP = "Travaux Pratiques"
    EXAMEN = "Examen"
    SOUTENANCE = "Soutenance"
    SEMINAIRE = "Séminaire"


class ActivityStatusEnum(enum.Enum):
    """Statuts des activités."""
    PENDING = "En attente"
    SCHEDULED = "Planifié"
    IN_PROGRESS = "En cours"
    COMPLETED = "Terminé"
    CANCELLED = "Annulé"


class PriorityEnum(enum.Enum):
    """Priorités des activités."""
    BASSE = "Basse"
    NORMALE = "Normale"
    HAUTE = "Haute"
    URGENTE = "Urgente"


class TeacherStatusEnum(enum.Enum):
    """Statuts des enseignants."""
    PERMANENT = "Permanent"
    VACATAIRE = "Vacataire"
    INVITE = "Invité"


class LeaveStatusEnum(enum.Enum):
    """Statuts des demandes de congés."""
    PENDING = "En attente"
    APPROVED = "Approuvé"
    REJECTED = "Rejeté"
    CANCELLED = "Annulé"


class LeaveTypeEnum(enum.Enum):
    """Types de congés."""
    MALADIE = "Maladie"
    CONGE_ANNUEL = "Congé annuel"
    FORMATION = "Formation"
    MISSION = "Mission"
    MATERNITE = "Maternité/Paternité"
    SANS_SOLDE = "Sans solde"
    AUTRE = "Autre"


class VacationTypeEnum(enum.Enum):
    """Types de périodes de vacances."""
    NOEL = "Vacances de Noël"
    PAQUES = "Vacances de Pâques"
    ETE = "Vacances d'été"
    TOUSSAINT = "Vacances de Toussaint"


# Modèles
class UniversityModel(Base):
    """Modèle ORM pour Université."""
    __tablename__ = 'universities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), default="Burkina Faso")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    ufrs = relationship("UFRModel", back_populates="university", cascade="all, delete-orphan")


class UFRModel(Base):
    """Modèle ORM pour UFR."""
    __tablename__ = 'ufrs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    director = Column(String(200))
    university_id = Column(Integer, ForeignKey('universities.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    university = relationship("UniversityModel", back_populates="ufrs")
    programs = relationship("ProgramModel", back_populates="ufr", cascade="all, delete-orphan")


class ProgramModel(Base):
    """Modèle ORM pour Programme/Parcours."""
    __tablename__ = 'programs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    level = Column(Enum(ProgramLevelEnum), nullable=False)
    duration_years = Column(Integer, nullable=False)
    ufr_id = Column(Integer, ForeignKey('ufrs.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    ufr = relationship("UFRModel", back_populates="programs")
    cohorts = relationship("CohortModel", back_populates="program", cascade="all, delete-orphan")


class CohortModel(Base):
    """Modèle ORM pour Cohorte/Classe."""
    __tablename__ = 'cohorts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    academic_year = Column(String(20), nullable=False)  # Ex: "2025-2026"
    semester = Column(Integer, nullable=False)  # 1 ou 2
    student_count = Column(Integer, nullable=False)
    program_id = Column(Integer, ForeignKey('programs.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    program = relationship("ProgramModel", back_populates="cohorts")
    students = relationship("StudentModel", back_populates="cohort", cascade="all, delete-orphan")
    activities = relationship("AcademicActivityModel", back_populates="cohort", cascade="all, delete-orphan")
    schedule_slots = relationship("ScheduleSlotModel", back_populates="cohort", cascade="all, delete-orphan")


class TeacherModel(Base):
    """Modèle ORM pour Enseignant."""
    __tablename__ = 'teachers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    speciality = Column(String(200), nullable=False)
    max_hours_per_week = Column(Integer, default=40)
    max_hours_per_day = Column(Integer, default=8)
    status = Column(Enum(TeacherStatusEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    activities = relationship("AcademicActivityModel", back_populates="teacher")
    schedule_slots = relationship("ScheduleSlotModel", back_populates="teacher")
    leave_requests = relationship("LeaveRequestModel", back_populates="teacher", cascade="all, delete-orphan")
    availability_slots = relationship("TeacherAvailabilityModel", back_populates="teacher", cascade="all, delete-orphan")
    constraint_reports = relationship("TeacherConstraintReportModel", back_populates="teacher", cascade="all, delete-orphan")


class StudentModel(Base):
    """Modèle ORM pour Étudiant."""
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    student_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    birth_date = Column(Date)
    cohort_id = Column(Integer, ForeignKey('cohorts.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    cohort = relationship("CohortModel", back_populates="students")


class AcademicActivityModel(Base):
    """Modèle ORM pour Activité Académique."""
    __tablename__ = 'academic_activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    type = Column(Enum(ActivityTypeEnum), nullable=False)
    volume_hours = Column(Float, nullable=False)  # Ci
    hours_done = Column(Float, default=0.0)  # H(t)
    charge_factor = Column(Float, default=0.0)  # U(τi)
    activation_date = Column(Date)  # ri
    deadline = Column(Date)  # Di
    period = Column(Integer, default=0)  # Ti
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.NORMALE)
    status = Column(Enum(ActivityStatusEnum), default=ActivityStatusEnum.PENDING)
    cohort_id = Column(Integer, ForeignKey('cohorts.id', ondelete='CASCADE'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    cohort = relationship("CohortModel", back_populates="activities")
    teacher = relationship("TeacherModel", back_populates="activities")
    schedule_slots = relationship("ScheduleSlotModel", back_populates="activity", cascade="all, delete-orphan")


class ScheduleSlotModel(Base):
    """Modèle ORM pour Créneau Horaire."""
    __tablename__ = 'schedule_slots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room = Column(String(50))
    activity_id = Column(Integer, ForeignKey('academic_activities.id', ondelete='CASCADE'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    cohort_id = Column(Integer, ForeignKey('cohorts.id', ondelete='CASCADE'), nullable=False)
    delay_value = Column(Float, default=0.0)
    blocked_by_leave = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    activity = relationship("AcademicActivityModel", back_populates="schedule_slots")
    teacher = relationship("TeacherModel", back_populates="schedule_slots")
    cohort = relationship("CohortModel", back_populates="schedule_slots")


class LeaveRequestModel(Base):
    """Modèle ORM pour Demande de Congé."""
    __tablename__ = 'leave_requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    leave_type = Column(Enum(LeaveTypeEnum), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(LeaveStatusEnum), default=LeaveStatusEnum.PENDING)
    working_days = Column(Integer)
    approver_email = Column(String(100))
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    teacher = relationship("TeacherModel", back_populates="leave_requests")


class TeacherAvailabilityModel(Base):
    """Modèle ORM pour créneau de disponibilité hebdomadaire d'un enseignant (jour + plage horaire)."""
    __tablename__ = 'teacher_availability'

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=lundi, 6=dimanche
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    teacher = relationship("TeacherModel", back_populates="availability_slots")


class ConstraintReportTypeEnum(enum.Enum):
    """Type de signalement."""
    CONFLIT = "Conflit d'emploi du temps"
    CONTRAINTE = "Contrainte particulière"
    AUTRE = "Autre"


class ConstraintReportStatusEnum(enum.Enum):
    """Statut du signalement."""
    PENDING = "En attente"
    VU = "Vu"
    TRAITE = "Traité"


class TeacherConstraintReportModel(Base):
    """Modèle ORM pour signalement de conflit ou contrainte par un enseignant."""
    __tablename__ = 'teacher_constraint_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    report_type = Column(Enum(ConstraintReportTypeEnum), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ConstraintReportStatusEnum), default=ConstraintReportStatusEnum.PENDING)
    reported_at = Column(DateTime, default=datetime.now)
    admin_notes = Column(Text)

    teacher = relationship("TeacherModel", back_populates="constraint_reports")


class AcademicCalendarModel(Base):
    """Modèle ORM pour Calendrier Académique."""
    __tablename__ = 'academic_calendars'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    academic_year = Column(String(20), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    hours_per_day = Column(Integer, default=8)
    semester_count = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    holidays = relationship("HolidayModel", back_populates="calendar", cascade="all, delete-orphan")
    vacation_periods = relationship("VacationPeriodModel", back_populates="calendar", cascade="all, delete-orphan")


class HolidayModel(Base):
    """Modèle ORM pour Jour Férié."""
    __tablename__ = 'holidays'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    is_recurring = Column(Boolean, default=False)
    calendar_id = Column(Integer, ForeignKey('academic_calendars.id', ondelete='CASCADE'), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    calendar = relationship("AcademicCalendarModel", back_populates="holidays")


class VacationPeriodModel(Base):
    """Modèle ORM pour Période de Vacances."""
    __tablename__ = 'vacation_periods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    type = Column(Enum(VacationTypeEnum), nullable=False)
    calendar_id = Column(Integer, ForeignKey('academic_calendars.id', ondelete='CASCADE'), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    calendar = relationship("AcademicCalendarModel", back_populates="vacation_periods")


# ====================== AUTH / RBAC MODELS ======================

# Association tables
from sqlalchemy import Table

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)

user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'))
)


class PermissionModel(Base):
    """Modèle ORM pour Permission (ex: manage_structure, manage_calendar)."""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)


class RoleModel(Base):
    """Modèle ORM pour Role (ex: Admin, Planner)."""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)

    permissions = relationship('PermissionModel', secondary=role_permissions, backref='roles')


class UserModel(Base):
    """Modèle ORM pour utilisateur de l'application."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Optional scope: user can be responsible for a specific UFR or Program
    ufr_id = Column(Integer, ForeignKey('ufrs.id', ondelete='SET NULL'), nullable=True)
    program_id = Column(Integer, ForeignKey('programs.id', ondelete='SET NULL'), nullable=True)
    # Lien optionnel vers un enseignant (pour rôle Enseignant)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='SET NULL'), nullable=True)

    roles = relationship('RoleModel', secondary=user_roles, backref='users')

    # Relationships to scope entities
    ufr = relationship('UFRModel')
    program = relationship('ProgramModel')
    teacher = relationship('TeacherModel')
