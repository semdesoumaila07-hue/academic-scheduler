-- ================================================================
-- SCRIPT D'INITIALISATION DE LA BASE DE DONNÉES
-- Système d'Ordonnancement Académique P-équitable
-- ================================================================

-- Activer les clés étrangères (important pour SQLite)
PRAGMA foreign_keys = ON;

-- ================================================================
-- TABLE: universities
-- ================================================================
CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'Burkina Faso',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_universities_code ON universities(code);
CREATE INDEX idx_universities_city ON universities(city);

-- ================================================================
-- TABLE: ufrs
-- ================================================================
CREATE TABLE IF NOT EXISTS ufrs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    director VARCHAR(200),
    university_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE
);

CREATE INDEX idx_ufrs_code ON ufrs(code);
CREATE INDEX idx_ufrs_university ON ufrs(university_id);

-- ================================================================
-- TABLE: programs
-- ================================================================
CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    level VARCHAR(50) NOT NULL, -- Licence 1, Licence 2, etc.
    duration_years INTEGER NOT NULL,
    ufr_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ufr_id) REFERENCES ufrs(id) ON DELETE CASCADE
);

CREATE INDEX idx_programs_code ON programs(code);
CREATE INDEX idx_programs_ufr ON programs(ufr_id);
CREATE INDEX idx_programs_level ON programs(level);

-- ================================================================
-- TABLE: cohorts
-- ================================================================
CREATE TABLE IF NOT EXISTS cohorts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    academic_year VARCHAR(20) NOT NULL, -- "2025-2026"
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),
    student_count INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE
);

CREATE INDEX idx_cohorts_program ON cohorts(program_id);
CREATE INDEX idx_cohorts_academic_year ON cohorts(academic_year);
CREATE INDEX idx_cohorts_dates ON cohorts(start_date, end_date);

-- ================================================================
-- TABLE: teachers
-- ================================================================
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    speciality VARCHAR(200) NOT NULL,
    max_hours_per_week INTEGER DEFAULT 40,
    max_hours_per_day INTEGER DEFAULT 8,
    status VARCHAR(50) NOT NULL, -- Permanent, Vacataire, Invité
    ufr_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ufr_id) REFERENCES ufrs(id) ON DELETE SET NULL
);

CREATE INDEX idx_teachers_email ON teachers(email);
CREATE INDEX idx_teachers_speciality ON teachers(speciality);
CREATE INDEX idx_teachers_status ON teachers(status);
CREATE INDEX idx_teachers_ufr ON teachers(ufr_id);

-- ================================================================
-- TABLE: students
-- ================================================================
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(200) NOT NULL,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    birth_date DATE,
    cohort_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cohort_id) REFERENCES cohorts(id) ON DELETE CASCADE
);

CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_cohort ON students(cohort_id);

-- ================================================================
-- TABLE: academic_activities
-- ================================================================
CREATE TABLE IF NOT EXISTS academic_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL, -- Cours Magistral, TD, TP, etc.
    volume_hours REAL NOT NULL, -- Ci - Volume horaire total
    hours_done REAL DEFAULT 0.0, -- H(t) - Heures réalisées
    charge_factor REAL DEFAULT 0.0, -- U(τi) - Facteur de charge
    activation_date DATE, -- ri - Date d'activation
    deadline DATE, -- Di - Date limite
    period INTEGER DEFAULT 0, -- Ti - Période en jours
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 10),
    status VARCHAR(50) DEFAULT 'En attente', -- En attente, Planifié, En cours, Terminé, Annulé
    cohort_id INTEGER NOT NULL,
    teacher_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cohort_id) REFERENCES cohorts(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
);

CREATE INDEX idx_activities_code ON academic_activities(code);
CREATE INDEX idx_activities_cohort ON academic_activities(cohort_id);
CREATE INDEX idx_activities_teacher ON academic_activities(teacher_id);
CREATE INDEX idx_activities_status ON academic_activities(status);
CREATE INDEX idx_activities_dates ON academic_activities(activation_date, deadline);

-- ================================================================
-- TABLE: schedule_slots
-- ================================================================
CREATE TABLE IF NOT EXISTS schedule_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room VARCHAR(50),
    activity_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    cohort_id INTEGER NOT NULL,
    delay_value REAL DEFAULT 0.0,
    blocked_by_leave BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES academic_activities(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (cohort_id) REFERENCES cohorts(id) ON DELETE CASCADE
);

CREATE INDEX idx_schedule_date ON schedule_slots(date);
CREATE INDEX idx_schedule_activity ON schedule_slots(activity_id);
CREATE INDEX idx_schedule_teacher ON schedule_slots(teacher_id);
CREATE INDEX idx_schedule_cohort ON schedule_slots(cohort_id);
CREATE INDEX idx_schedule_room ON schedule_slots(room);
CREATE INDEX idx_schedule_blocked ON schedule_slots(blocked_by_leave);

-- ================================================================
-- TABLE: leave_requests
-- ================================================================
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    leave_type VARCHAR(50) NOT NULL, -- Maladie, Congé annuel, Formation, etc.
    reason TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'En attente', -- En attente, Approuvé, Rejeté, Annulé
    working_days INTEGER,
    approver_email VARCHAR(100),
    approved_at DATETIME,
    rejected_at DATETIME,
    rejection_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

CREATE INDEX idx_leave_teacher ON leave_requests(teacher_id);
CREATE INDEX idx_leave_status ON leave_requests(status);
CREATE INDEX idx_leave_dates ON leave_requests(start_date, end_date);

-- ================================================================
-- TABLE: academic_calendars
-- ================================================================
CREATE TABLE IF NOT EXISTS academic_calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    academic_year VARCHAR(20) UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    hours_per_day INTEGER DEFAULT 8,
    semester_count INTEGER DEFAULT 2,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_calendar_year ON academic_calendars(academic_year);
CREATE INDEX idx_calendar_dates ON academic_calendars(start_date, end_date);

-- ================================================================
-- TABLE: holidays
-- ================================================================
CREATE TABLE IF NOT EXISTS holidays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    is_recurring BOOLEAN DEFAULT 0,
    calendar_id INTEGER NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (calendar_id) REFERENCES academic_calendars(id) ON DELETE CASCADE
);

CREATE INDEX idx_holidays_calendar ON holidays(calendar_id);
CREATE INDEX idx_holidays_date ON holidays(date);
CREATE INDEX idx_holidays_recurring ON holidays(is_recurring);

-- ================================================================
-- TABLE: vacation_periods
-- ================================================================
CREATE TABLE IF NOT EXISTS vacation_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    type VARCHAR(50) NOT NULL, -- Vacances de Noël, Pâques, Été, Toussaint
    calendar_id INTEGER NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (calendar_id) REFERENCES academic_calendars(id) ON DELETE CASCADE
);

CREATE INDEX idx_vacation_calendar ON vacation_periods(calendar_id);
CREATE INDEX idx_vacation_dates ON vacation_periods(start_date, end_date);
CREATE INDEX idx_vacation_type ON vacation_periods(type);



-- ('Université Norbert Zongo', 'UNZ', 'Avenue de la République', 'Ouagadougou', 'Burkina Faso');


-- ================================================================
-- FIN DU SCRIPT
-- ================================================================