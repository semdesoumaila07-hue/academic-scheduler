# 📊 Diagramme de Classes

## Vue d'ensemble

Ce document décrit le diagramme de classes complet du système d'ordonnancement académique.

---

## 🎯 Classes Principales

### **Entités (Domain Objects)**

```
┌─────────────────────────┐
│      University         │
├─────────────────────────┤
│ - id: int               │
│ - name: str             │
│ - code: str             │
│ - address: str          │
│ - city: str             │
│ - country: str          │
├─────────────────────────┤
│ + validate(): bool      │
└─────────────────────────┘
         ▲ 1
         │ a
         │ *
┌─────────────────────────┐
│         UFR             │
├─────────────────────────┤
│ - id: int               │
│ - name: str             │
│ - code: str             │
│ - director: str         │
│ - university_id: int    │
├─────────────────────────┤
│ + validate(): bool      │
└─────────────────────────┘
         ▲ 1
         │ contient
         │ *
┌─────────────────────────┐
│       Program           │
├─────────────────────────┤
│ - id: int               │
│ - name: str             │
│ - code: str             │
│ - level: ProgramLevel   │
│ - duration_years: int   │
│ - ufr_id: int           │
├─────────────────────────┤
│ + validate(): bool      │
└─────────────────────────┘
         ▲ 1
         │ propose
         │ *
┌─────────────────────────┐
│        Cohort           │
├─────────────────────────┤
│ - id: int               │
│ - name: str             │
│ - academic_year: str    │
│ - semester: int         │
│ - student_count: int    │
│ - program_id: int       │
│ - start_date: date      │
│ - end_date: date        │
├─────────────────────────┤
│ + validate(): bool      │
│ + is_active(): bool     │
└─────────────────────────┘
```

---

### **Activités Académiques (avec Pfair)**

```
┌──────────────────────────────────────┐
│        AcademicActivity              │
├──────────────────────────────────────┤
│ - id: int                            │
│ - name: str                          │
│ - code: str                          │
│ - type: ActivityTypeEnum             │
│ - volume_hours: float    (Ci)        │
│ - hours_done: float      (H(t))      │
│ - charge_factor: float   (U)         │
│ - cohort_id: int                     │
│ - teacher_id: int                    │
│ - activation_date: date  (ri)        │
│ - deadline: date         (Di)        │
│ - priority: int                      │
│ - status: ActivityStatusEnum         │
├──────────────────────────────────────┤
│ + validate(): bool                   │
│ + calculate_charge_factor(D): void  │
│ + add_hours(hours): void             │
│ + get_remaining_hours(): float       │
│ + get_completion_percentage(): float │
└──────────────────────────────────────┘
              ▲
              │ planifie
              │ *
┌──────────────────────────────────────┐
│         ScheduleSlot                 │
├──────────────────────────────────────┤
│ - id: int                            │
│ - cohort_id: int                     │
│ - activity_id: int                   │
│ - teacher_id: int                    │
│ - date: date                         │
│ - start_time: time                   │
│ - end_time: time                     │
│ - room: str                          │
│ - is_blocked: bool                   │
│ - delay_value: float                 │
├──────────────────────────────────────┤
│ + validate(): bool                   │
│ + get_duration_hours(): float        │
└──────────────────────────────────────┘
```

---

### **Personnes**

```
┌─────────────────────────┐
│       Teacher           │
├─────────────────────────┤
│ - id: int               │
│ - full_name: str        │
│ - email: str            │
│ - phone: str            │
│ - speciality: str       │
│ - status: TeacherStatus │
│ - max_hours_per_week    │
│ - max_hours_per_day     │
├─────────────────────────┤
│ + validate(): bool      │
│ + is_available(): bool  │
└─────────────────────────┘

┌─────────────────────────┐
│       Student           │
├─────────────────────────┤
│ - id: int               │
│ - full_name: str        │
│ - student_id: str       │
│ - email: str            │
│ - phone: str            │
│ - birth_date: date      │
│ - cohort_id: int        │
├─────────────────────────┤
│ + validate(): bool      │
│ + get_age(): int        │
└─────────────────────────┘
```

---

### **Calendrier**

```
┌─────────────────────────────┐
│    AcademicCalendar         │
├─────────────────────────────┤
│ - id: int                   │
│ - name: str                 │
│ - academic_year: str        │
│ - start_date: date          │
│ - end_date: date            │
│ - hours_per_day: int        │
├─────────────────────────────┤
│ + validate(): bool          │
└─────────────────────────────┘
         ▲ 1
         │ contient
         │ *
┌─────────────────────────────┐
│         Holiday             │
├─────────────────────────────┤
│ - id: int                   │
│ - name: str                 │
│ - date: date                │
│ - is_recurring: bool        │
│ - calendar_id: int          │
├─────────────────────────────┤
│ + validate(): bool          │
└─────────────────────────────┘

┌─────────────────────────────┐
│      VacationPeriod         │
├─────────────────────────────┤
│ - id: int                   │
│ - name: str                 │
│ - start_date: date          │
│ - end_date: date            │
│ - type: VacationTypeEnum    │
│ - calendar_id: int          │
├─────────────────────────────┤
│ + validate(): bool          │
│ + get_duration_days(): int  │
└─────────────────────────────┘
```

---

## 🔧 Services

```
┌────────────────────────────────────┐
│       PfairScheduler               │
├────────────────────────────────────┤
│ - session: Session                 │
│ - activity_repo: ActivityRepo      │
│ - schedule_repo: ScheduleRepo      │
│ - calendar_service: CalendarSvc    │
├────────────────────────────────────┤
│ + schedule_cohort(...)             │
│ + is_schedulable(...): Dict        │
│ + calculate_activity_priority(...) │
│ + rebalance_schedule()             │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│      CalendarService               │
├────────────────────────────────────┤
│ - session: Session                 │
│ - calendar_repo: CalendarRepo      │
├────────────────────────────────────┤
│ + is_workday(date): bool           │
│ + calculate_effective_days(...)    │
│ + get_workdays_list(...): List     │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│      DelayCalculator               │
├────────────────────────────────────┤
│ - session: Session                 │
│ - activity_repo: ActivityRepo      │
├────────────────────────────────────┤
│ + calculate_activity_delay(...)    │
│ + calculate_cohort_delay(...)      │
│ + get_urgent_activities(...)       │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│       LeaveService                 │
├────────────────────────────────────┤
│ - session: Session                 │
│ - leave_repo: LeaveRequestRepo     │
│ - schedule_repo: ScheduleRepo      │
├────────────────────────────────────┤
│ + submit_leave_request(...)        │
│ + approve_leave_request(...)       │
│ + reject_leave_request(...)        │
│ + check_teacher_availability(...)  │
└────────────────────────────────────┘
```

---

## 🏗️ Managers

```
┌────────────────────────────────────┐
│      StructureManager              │
├────────────────────────────────────┤
│ - session: Session                 │
│ - university_repo: UniversityRepo  │
│ - ufr_repo: UFRRepo                │
│ - program_repo: ProgramRepo        │
│ - cohort_repo: CohortRepo          │
├────────────────────────────────────┤
│ + create_university(...)           │
│ + create_ufr(...)                  │
│ + create_program(...)              │
│ + create_cohort(...)               │
│ + get_global_statistics(): Dict    │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│      ActivityManager               │
├────────────────────────────────────┤
│ - session: Session                 │
│ - activity_repo: ActivityRepo      │
│ - delay_calculator: DelayCalc      │
├────────────────────────────────────┤
│ + create_activity(...)             │
│ + assign_teacher(...)              │
│ + update_activity_hours(...)       │
│ + get_urgent_activities(...)       │
│ + calculate_cohort_workload(...)   │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│     ScheduleGenerator              │
├────────────────────────────────────┤
│ - session: Session                 │
│ - pfair_scheduler: PfairScheduler  │
│ - calendar_service: CalendarSvc    │
│ - schedule_repo: ScheduleRepo      │
├────────────────────────────────────┤
│ + generate_schedule(...)           │
│ + create_manual_slot(...)          │
│ + delete_slot(...)                 │
│ + check_conflicts(...)             │
│ + get_schedule_statistics(...)     │
└────────────────────────────────────┘
```

---

## ✅ Validators

```
┌────────────────────────────────────┐
│     ScheduleValidator              │
├────────────────────────────────────┤
│ + validate_time_slot(...): Tuple   │
│ + validate_date(...): Tuple        │
│ + validate_teacher_workload(...)   │
│ + validate_room(...): Tuple        │
│ + validate_complete_slot(...)      │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│      LeaveValidator                │
├────────────────────────────────────┤
│ + validate_dates(...): Tuple       │
│ + validate_duration(...): Tuple    │
│ + check_overlap(...): Tuple        │
│ + check_schedule_impact(...)       │
│ + validate_complete_request(...)   │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│     ConflictDetector               │
├────────────────────────────────────┤
│ + detect_teacher_conflicts(...)    │
│ + detect_cohort_conflicts(...)     │
│ + detect_room_conflicts(...)       │
│ + detect_all_conflicts(...): Dict  │
│ + find_gaps_in_schedule(...)       │
└────────────────────────────────────┘
```

---

## 🗄️ Repositories (Pattern)

```
┌────────────────────────────────────┐
│      BaseRepository<T>             │
├────────────────────────────────────┤
│ # session: Session                 │
│ # model_class: Type[T]             │
├────────────────────────────────────┤
│ + create(**kwargs): T              │
│ + get_by_id(id): T                 │
│ + get_all(): List[T]               │
│ + update(id, **kwargs): T          │
│ + delete(id): bool                 │
└────────────────────────────────────┘
              ▲
              │ hérite
              │
    ┌─────────┴─────────┐
    │                   │
┌───────────────┐  ┌──────────────┐
│ UniversityRepo│  │ActivityRepo  │
├───────────────┤  ├──────────────┤
│+ get_by_code()│  │+ get_by_...  │
│               │  │+ get_urgent()│
└───────────────┘  └──────────────┘
```

---

## 📊 Relations Principales

### **Hiérarchie Structurelle**
```
University (1) ──── a ───── (n) UFR
    UFR    (1) ── contient ─ (n) Program
   Program (1) ── propose ── (n) Cohort
   Cohort  (1) ── contient ─ (n) Student
```

### **Activités et Emploi du Temps**
```
Cohort (1) ──── a ───── (n) AcademicActivity
Activity (1) ── planifié ─ (n) ScheduleSlot
Teacher (1) ─── enseigne ─ (n) ScheduleSlot
```

### **Calendrier**
```
AcademicCalendar (1) ─── contient ─── (n) Holiday
AcademicCalendar (1) ─── contient ─── (n) VacationPeriod
```

---

## 🔗 Multiplicités

| Relation | Type | Description |
|----------|------|-------------|
| University → UFR | 1:n | Une université a plusieurs UFR |
| UFR → Program | 1:n | Une UFR propose plusieurs programmes |
| Program → Cohort | 1:n | Un programme a plusieurs cohortes |
| Cohort → Student | 1:n | Une cohorte contient plusieurs étudiants |
| Cohort → Activity | 1:n | Une cohorte a plusieurs activités |
| Activity → ScheduleSlot | 1:n | Une activité a plusieurs créneaux |
| Teacher → ScheduleSlot | 1:n | Un enseignant a plusieurs créneaux |

---

## 🎯 Patterns Utilisés

1. **Repository Pattern** - Abstraction accès données
2. **Service Pattern** - Logique métier
3. **Manager Pattern** - Orchestration haut niveau
4. **Validator Pattern** - Validation stateless
5. **Strategy Pattern** - Algorithmes interchangeables

---

## 📝 Notes pour Draw.io

Pour créer le diagramme dans draw.io :
1. Utiliser les boîtes UML standard
2. Connecteurs avec multiplicités
3. Couleurs par couche :
   - Entités : Bleu clair
   - Services : Vert clair
   - Managers : Orange clair
   - Validators : Rouge clair
   - Repositories : Violet clair