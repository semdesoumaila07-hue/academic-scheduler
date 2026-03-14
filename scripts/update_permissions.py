"""
Script pour mettre à jour les permissions selon les nouvelles spécifications.

Ce script met à jour les rôles existants avec les nouvelles permissions.
"""
from src.database.db_manager import db_manager
from src.database.repositories import RoleRepository, PermissionRepository


def update_permissions():
    """Met à jour les permissions des rôles selon les spécifications."""
    db_manager.initialize()
    session = db_manager.get_session()
    
    role_repo = RoleRepository(session)
    perm_repo = PermissionRepository(session)
    
    print("=" * 80)
    print("🔄 MISE À JOUR DES PERMISSIONS")
    print("=" * 80)
    print()
    
    # Créer les permissions si elles n'existent pas
    perms_to_create = {
        'submit_leave': 'Soumettre une demande de congés',
        'approve_leave': 'Approuver une demande de congés',
    }
    
    created_perms = {}
    for name, desc in perms_to_create.items():
        perm = perm_repo.get_by_name(name)
        if not perm:
            perm = perm_repo.create(name=name, description=desc)
            print(f"✅ Permission créée: {name}")
        created_perms[name] = perm
    
    # Récupérer toutes les permissions nécessaires
    all_perms = {}
    perm_names = [
        'view_dashboard', 'manage_structure', 'manage_calendar', 
        'generate_reports', 'analyze_delays', 'manage_activities',
        'launch_scheduling', 'view_timetable', 'declare_availability',
        'submit_leave', 'approve_leave'
    ]
    
    for name in perm_names:
        perm = perm_repo.get_by_name(name)
        if perm:
            all_perms[name] = perm
        else:
            print(f"⚠️  Permission non trouvée: {name}")
    
    # Mettre à jour ADMIN
    admin = role_repo.get_by_name('Admin')
    if admin:
        admin.permissions = [
            all_perms.get('view_dashboard'),
            all_perms.get('manage_structure'),
            all_perms.get('manage_calendar'),
            all_perms.get('generate_reports'),
            all_perms.get('analyze_delays'),
            all_perms.get('view_timetable'),
        ]
        admin.permissions = [p for p in admin.permissions if p is not None]
        session.commit()
        print("✅ Admin mis à jour")
    else:
        print("⚠️  Rôle Admin non trouvé")
    
    # Mettre à jour PEDAGOGICAL
    pedagog = role_repo.get_by_name('Pedagogical')
    if pedagog:
        pedagog.permissions = [
            all_perms.get('view_dashboard'),
            all_perms.get('manage_activities'),
            all_perms.get('launch_scheduling'),
            all_perms.get('analyze_delays'),
            all_perms.get('approve_leave'),
            all_perms.get('view_timetable'),
        ]
        pedagog.permissions = [p for p in pedagog.permissions if p is not None]
        session.commit()
        print("✅ Responsable pédagogique mis à jour")
    else:
        print("⚠️  Rôle Pedagogical non trouvé")
    
    # Mettre à jour TEACHER
    teacher = role_repo.get_by_name('Teacher')
    if teacher:
        teacher.permissions = [
            all_perms.get('view_dashboard'),
            all_perms.get('view_timetable'),
            all_perms.get('declare_availability'),
            all_perms.get('submit_leave'),
        ]
        teacher.permissions = [p for p in teacher.permissions if p is not None]
        session.commit()
        print("✅ Enseignant mis à jour")
    else:
        print("⚠️  Rôle Teacher non trouvé")
    
    # Mettre à jour STUDENT
    student = role_repo.get_by_name('Student')
    if student:
        student.permissions = [
            all_perms.get('view_dashboard'),
            all_perms.get('view_timetable'),
            all_perms.get('analyze_delays'),
        ]
        student.permissions = [p for p in student.permissions if p is not None]
        session.commit()
        print("✅ Étudiant mis à jour")
    else:
        print("⚠️  Rôle Student non trouvé")
    
    print()
    print("=" * 80)
    print("✅ Mise à jour terminée!")
    print("=" * 80)
    print()
    print("💡 Exécutez 'python scripts/verify_roles_permissions.py' pour vérifier")
    
    session.close()


if __name__ == '__main__':
    update_permissions()
