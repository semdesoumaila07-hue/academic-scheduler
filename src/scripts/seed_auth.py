"""Seed roles, permissions and example users.

Run this script after initializing the database to create an Admin and a
Responsable pédagogique sample user.
"""
from src.database.db_manager import db_manager
from src.database.repositories import RoleRepository, PermissionRepository, UserRepository

from src.services.auth_service import create_user


def seed():
    db_manager.initialize()
    db_manager.create_tables()
    session = db_manager.get_session()

    role_repo = RoleRepository(session)
    perm_repo = PermissionRepository(session)
    user_repo = UserRepository(session)

    # Permissions
    perms = {
        'manage_structure': 'Manage universities/UFRs/programs',
        'manage_calendar': 'Manage academic calendar',
        'generate_reports': 'Generate global reports',
        'manage_activities': 'Create and edit activities',
        'launch_scheduling': 'Launch automatic scheduling',
        'validate_schedule': 'Validate generated schedules',
        'analyze_delays': 'Analyze delays and indicators',
        'adjust_schedule': 'Perform manual schedule adjustments'
    }

    created_perms = {}
    for name, desc in perms.items():
        p = perm_repo.get_by_name(name)
        if not p:
            p = perm_repo.create(name=name, description=desc)
        created_perms[name] = p

    # Roles
    admin = role_repo.get_by_name('Admin')
    if not admin:
        admin = role_repo.create(name='Admin', description='Système administrator')
        # give admin all perms
        admin.permissions = list(created_perms.values())
        session.commit()

    pedagog = role_repo.get_by_name('Pedagogical')
    if not pedagog:
        pedagog = role_repo.create(name='Pedagogical', description='Responsable pédagogique')
        pedagog.permissions = [
            created_perms['manage_activities'],
            created_perms['launch_scheduling'],
            created_perms['validate_schedule'],
            created_perms['analyze_delays'],
            created_perms['adjust_schedule']
        ]
        session.commit()

    # Additional academic roles with tailored permissions
    teacher = role_repo.get_by_name('Teacher')
    if not teacher:
        teacher = role_repo.create(name='Teacher', description='Enseignant / Maître de conférence')
        # Teachers can create/edit activities (their own) and view/analyze simple indicators
        teacher.permissions = [
            created_perms['manage_activities']
        ]
        session.commit()

    head = role_repo.get_by_name('HeadOfDepartment')
    if not head:
        head = role_repo.create(name='HeadOfDepartment', description='Maître de discipline / Responsable de département')
        # Head of department can manage activities and validate schedules at dept. level
        head.permissions = [
            created_perms['manage_activities'],
            created_perms['validate_schedule']
        ]
        session.commit()

    accountant = role_repo.get_by_name('Accountant')
    if not accountant:
        accountant = role_repo.create(name='Accountant', description='Comptable')
        # Accountant primarily generates reports (financial/statistical)
        accountant.permissions = [
            created_perms['generate_reports']
        ]
        session.commit()

    student = role_repo.get_by_name('Student')
    if not student:
        student = role_repo.create(name='Student', description='Étudiant')
        # Students typically have no management permissions; keep empty by default
        student.permissions = []
        session.commit()

    # Example users
    admin_user = user_repo.get_by_username('admin')
    if not admin_user:
        u = create_user('admin', 'admin@example.com', 'AdminPass123', session=session)
        role_repo_obj = role_repo.get_by_name('Admin')
        user_repo.add_role(u, role_repo_obj)

    pedagog_user = user_repo.get_by_username('pedagog')
    if not pedagog_user:
        u2 = create_user('pedagog', 'pedagog@example.com', 'PedagogPass123', session=session)
        role_repo_obj = role_repo.get_by_name('Pedagogical')
        user_repo.add_role(u2, role_repo_obj)

    session.close()
    print('Seeding complete: Admin and Pedagogical users created (admin/pedagog).')


if __name__ == '__main__':
    seed()
