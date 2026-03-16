"""
Modèles SQLAlchemy (ORM) pour toutes les entités.
"""
from datetime import datetime
from sqlalchemy import (
<<<<<<< HEAD
    Column, Integer, String, Float, Boolean, Date, Time,
=======
    Column, Integer, String, Float, Boolean, Date, Time, 
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
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
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), default="Burkina Faso")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    ufrs = relationship("UFRModel", back_populates="university", cascade="all, delete-orphan")


class UFRModel(Base):
    """Modèle ORM pour UFR."""
    __tablename__ = 'ufrs'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    director = Column(String(200))
    university_id = Column(Integer, ForeignKey('universities.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

    # Relations
    university = relationship("UniversityModel", back_populates="ufrs")
    programs = relationship("ProgramModel", back_populates="ufr", cascade="all, delete-orphan")
    teachers = relationship("TeacherModel", back_populates="ufr", cascade="all, delete-orphan")
=======
    
    # Relations
    university = relationship("UniversityModel", back_populates="ufrs")
    programs = relationship("ProgramModel", back_populates="ufr", cascade="all, delete-orphan")
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f


class ProgramModel(Base):
    """Modèle ORM pour Programme/Parcours."""
    __tablename__ = 'programs'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    level = Column(Enum(ProgramLevelEnum), nullable=False)
    duration_years = Column(Integer, nullable=False)
    ufr_id = Column(Integer, ForeignKey('ufrs.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    ufr = relationship("UFRModel", back_populates="programs")
    cohorts = relationship("CohortModel", back_populates="program", cascade="all, delete-orphan")


class CohortModel(Base):
    """Modèle ORM pour Cohorte/Classe."""
    __tablename__ = 'cohorts'
<<<<<<< HEAD

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    academic_year = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)
=======
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    academic_year = Column(String(20), nullable=False)  # Ex: "2025-2026"
    semester = Column(Integer, nullable=False)  # 1 ou 2
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    student_count = Column(Integer, nullable=False)
    program_id = Column(Integer, ForeignKey('programs.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    program = relationship("ProgramModel", back_populates="cohorts")
    students = relationship("StudentModel", back_populates="cohort", cascade="all, delete-orphan")
    activities = relationship("AcademicActivityModel", back_populates="cohort", cascade="all, delete-orphan")
    schedule_slots = relationship("ScheduleSlotModel", back_populates="cohort", cascade="all, delete-orphan")


class TeacherModel(Base):
    """Modèle ORM pour Enseignant."""
    __tablename__ = 'teachers'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    speciality = Column(String(200), nullable=False)
    max_hours_per_week = Column(Integer, default=40)
    max_hours_per_day = Column(Integer, default=8)
    status = Column(Enum(TeacherStatusEnum), nullable=False)
<<<<<<< HEAD
    ufr_id = Column(Integer, ForeignKey('ufrs.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relations
    ufr = relationship("UFRModel", back_populates="teachers")
=======
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    activities = relationship("AcademicActivityModel", back_populates="teacher")
    schedule_slots = relationship("ScheduleSlotModel", back_populates="teacher")
    leave_requests = relationship("LeaveRequestModel", back_populates="teacher", cascade="all, delete-orphan")
    availability_slots = relationship("TeacherAvailabilityModel", back_populates="teacher", cascade="all, delete-orphan")
    constraint_reports = relationship("TeacherConstraintReportModel", back_populates="teacher", cascade="all, delete-orphan")


class StudentModel(Base):
    """Modèle ORM pour Étudiant."""
    __tablename__ = 'students'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    student_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    birth_date = Column(Date)
    cohort_id = Column(Integer, ForeignKey('cohorts.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    cohort = relationship("CohortModel", back_populates="students")


class AcademicActivityModel(Base):
    """Modèle ORM pour Activité Académique."""
    __tablename__ = 'academic_activities'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    type = Column(Enum(ActivityTypeEnum), nullable=False)
<<<<<<< HEAD
    volume_hours = Column(Float, nullable=False)
    hours_done = Column(Float, default=0.0)
    charge_factor = Column(Float, default=0.0)
    activation_date = Column(Date)
    deadline = Column(Date)
    period = Column(Integer, default=0)
=======
    volume_hours = Column(Float, nullable=False)  # Ci
    hours_done = Column(Float, default=0.0)  # H(t)
    charge_factor = Column(Float, default=0.0)  # U(τi)
    activation_date = Column(Date)  # ri
    deadline = Column(Date)  # Di
    period = Column(Integer, default=0)  # Ti
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.NORMALE)
    status = Column(Enum(ActivityStatusEnum), default=ActivityStatusEnum.PENDING)
    cohort_id = Column(Integer, ForeignKey('cohorts.id', ondelete='CASCADE'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    cohort = relationship("CohortModel", back_populates="activities")
    teacher = relationship("TeacherModel", back_populates="activities")
    schedule_slots = relationship("ScheduleSlotModel", back_populates="activity", cascade="all, delete-orphan")


class ScheduleSlotModel(Base):
    """Modèle ORM pour Créneau Horaire."""
    __tablename__ = 'schedule_slots'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
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
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    activity = relationship("AcademicActivityModel", back_populates="schedule_slots")
    teacher = relationship("TeacherModel", back_populates="schedule_slots")
    cohort = relationship("CohortModel", back_populates="schedule_slots")


<<<<<<< HEAD


class RoomModel(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    capacity = Column(Integer, default=30)
    room_type = Column(String(20), default='TD')
    building = Column(String(100))
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class LeaveRequestModel(Base):
    """Modèle ORM pour Demande de Congé."""
    __tablename__ = 'leave_requests'

=======
class LeaveRequestModel(Base):
    """Modèle ORM pour Demande de Congé."""
    __tablename__ = 'leave_requests'
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
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
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    teacher = relationship("TeacherModel", back_populates="leave_requests")


class TeacherAvailabilityModel(Base):
<<<<<<< HEAD
    """Modèle ORM pour créneau de disponibilité hebdomadaire d'un enseignant."""
=======
    """Modèle ORM pour créneau de disponibilité hebdomadaire d'un enseignant (jour + plage horaire)."""
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    __tablename__ = 'teacher_availability'

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
<<<<<<< HEAD
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
=======
    day_of_week = Column(Integer, nullable=False)  # 0=lundi, 6=dimanche
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
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
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    academic_year = Column(String(20), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    hours_per_day = Column(Integer, default=8)
    semester_count = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    holidays = relationship("HolidayModel", back_populates="calendar", cascade="all, delete-orphan")
    vacation_periods = relationship("VacationPeriodModel", back_populates="calendar", cascade="all, delete-orphan")


class HolidayModel(Base):
    """Modèle ORM pour Jour Férié."""
    __tablename__ = 'holidays'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    is_recurring = Column(Boolean, default=False)
    calendar_id = Column(Integer, ForeignKey('academic_calendars.id', ondelete='CASCADE'), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    calendar = relationship("AcademicCalendarModel", back_populates="holidays")


class VacationPeriodModel(Base):
    """Modèle ORM pour Période de Vacances."""
    __tablename__ = 'vacation_periods'
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    type = Column(Enum(VacationTypeEnum), nullable=False)
    calendar_id = Column(Integer, ForeignKey('academic_calendars.id', ondelete='CASCADE'), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
<<<<<<< HEAD

=======
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    # Relations
    calendar = relationship("AcademicCalendarModel", back_populates="vacation_periods")


# ====================== AUTH / RBAC MODELS ======================

<<<<<<< HEAD
=======
# Association tables
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
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
<<<<<<< HEAD
    """Modèle ORM pour Permission."""
=======
    """Modèle ORM pour Permission (ex: manage_structure, manage_calendar)."""
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)


class RoleModel(Base):
<<<<<<< HEAD
    """Modèle ORM pour Role."""
=======
    """Modèle ORM pour Role (ex: Admin, Planner)."""
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
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
<<<<<<< HEAD
    is_locked = Column(Boolean, default=False)
    login_attempts = Column(Integer, default=0)
    locked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    ufr_id = Column(Integer, ForeignKey('ufrs.id', ondelete='SET NULL'), nullable=True)
    program_id = Column(Integer, ForeignKey('programs.id', ondelete='SET NULL'), nullable=True)
=======
    created_at = Column(DateTime, default=datetime.now)

    # Optional scope: user can be responsible for a specific UFR or Program
    ufr_id = Column(Integer, ForeignKey('ufrs.id', ondelete='SET NULL'), nullable=True)
    program_id = Column(Integer, ForeignKey('programs.id', ondelete='SET NULL'), nullable=True)
    # Lien optionnel vers un enseignant (pour rôle Enseignant)
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='SET NULL'), nullable=True)

    roles = relationship('RoleModel', secondary=user_roles, backref='users')

<<<<<<< HEAD
    ufr = relationship('UFRModel')
    program = relationship('ProgramModel')
    teacher = relationship('TeacherModel')
=======
    # Relationships to scope entities
    ufr = relationship('UFRModel')
    program = relationship('ProgramModel')
    teacher = relationship('TeacherModel')
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
