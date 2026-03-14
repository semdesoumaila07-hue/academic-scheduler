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

    # Permissions selon les spécifications recommandées
    perms = {
        # Permissions communes
        'view_dashboard': 'Voir le tableau de bord',
        'view_timetable': 'Consulter les emplois du temps',
        'analyze_delays': 'Consulter les retards académiques',
        
        # Permissions Admin
        'manage_structure': 'Configurer structure universitaire',
        'manage_calendar': 'Configurer calendrier académique',
        'generate_reports': 'Générer les rapports',
        
        # Permissions Responsable pédagogique
        'manage_activities': 'Gérer les activités académiques',
        'launch_scheduling': 'Lancer l\'ordonnancement Pfair',
        'approve_leave': 'Approuver une demande de congés',
        
        # Permissions Enseignant
        'declare_availability': 'Déclarer les disponibilités',
        'submit_leave': 'Soumettre une demande de congés',
        
        # Permissions supplémentaires (pour compatibilité)
        'manage_teachers': 'Gérer les enseignants',
        'manage_leaves': 'Gérer les congés (tous)',
        'validate_schedule': 'Valider les plannings générés',
        'adjust_schedule': 'Ajustements manuels du planning',
    }

    created_perms = {}
    for name, desc in perms.items():
        p = perm_repo.get_by_name(name)
        if not p:
            p = perm_repo.create(name=name, description=desc)
        created_perms[name] = p

    # Roles et permissions selon les spécifications recommandées
    
    # ADMIN : Configurer structure universitaire, configurer calendrier académique,
    #         Générer Rapport, consulter Retard Académique
    admin = role_repo.get_by_name('Admin')
    if admin:
        # Mettre à jour les permissions existantes
        admin.permissions = [
            created_perms['view_dashboard'],
            created_perms['manage_structure'],      # Configurer structure universitaire
            created_perms['manage_calendar'],      # Configurer calendrier académique
            created_perms['generate_reports'],     # Générer Rapport
            created_perms['analyze_delays'],       # Consulter Retard Académique
            created_perms['view_timetable'],       # Peut aussi consulter les EDT
        ]
        session.commit()
    else:
        admin = role_repo.create(name='Admin', description='Administrateur')
        admin.permissions = [
            created_perms['view_dashboard'],
            created_perms['manage_structure'],
            created_perms['manage_calendar'],
            created_perms['generate_reports'],
            created_perms['analyze_delays'],
            created_perms['view_timetable'],
        ]
        session.commit()

    # RESPONSABLE PÉDAGOGIQUE : Gérer les activités académiques, Lancer l'ordonnancement Pfair,
    #                           Consulter les retards académiques, Approuver une demande de congés,
    #                           Gérer les activités académiques (doublon), Consulter l'emploi du temps
    pedagog = role_repo.get_by_name('Pedagogical')
    if pedagog:
        # Mettre à jour les permissions existantes
        pedagog.permissions = [
            created_perms['view_dashboard'],
            created_perms['manage_activities'],    # Gérer les activités académiques
            created_perms['launch_scheduling'],    # Lancer l'ordonnancement Pfair
            created_perms['analyze_delays'],       # Consulter les retards académiques
            created_perms['approve_leave'],        # Approuver une demande de congés
            created_perms['view_timetable'],       # Consulter l'emploi du temps
        ]
        session.commit()
    else:
        pedagog = role_repo.create(name='Pedagogical', description='Responsable pédagogique')
        pedagog.permissions = [
            created_perms['view_dashboard'],
            created_perms['manage_activities'],
            created_perms['launch_scheduling'],
            created_perms['analyze_delays'],
            created_perms['approve_leave'],
            created_perms['view_timetable'],
        ]
        session.commit()

    # ENSEIGNANT : Consulter les emplois du temps, Déclarer les disponibilités,
    #              Soumettre une demande de congés
    teacher = role_repo.get_by_name('Teacher')
    if teacher:
        # Mettre à jour les permissions existantes
        teacher.permissions = [
            created_perms['view_dashboard'],
            created_perms['view_timetable'],       # Consulter les emplois du temps
            created_perms['declare_availability'], # Déclarer les disponibilités
            created_perms['submit_leave'],         # Soumettre une demande de congés
        ]
        session.commit()
    else:
        teacher = role_repo.create(name='Teacher', description='Enseignant')
        teacher.permissions = [
            created_perms['view_dashboard'],
            created_perms['view_timetable'],
            created_perms['declare_availability'],
            created_perms['submit_leave'],
        ]
        session.commit()

    # ÉTUDIANT : Consulter les emplois du temps, Consulter les retards académiques
    student = role_repo.get_by_name('Student')
    if student:
        # Mettre à jour les permissions existantes
        student.permissions = [
            created_perms['view_dashboard'],
            created_perms['view_timetable'],       # Consulter les emplois du temps
            created_perms['analyze_delays'],       # Consulter les retards académiques
        ]
        session.commit()
    else:
        student = role_repo.create(name='Student', description='Étudiant')
        student.permissions = [
            created_perms['view_dashboard'],
            created_perms['view_timetable'],
            created_perms['analyze_delays'],
        ]
        session.commit()

    # Utilisateurs exemple (chaque type peut se connecter avec son propre mot de passe)
    if not user_repo.get_by_username('admin'):
        u = create_user('admin', 'admin@example.com', 'AdminPass123', session=session)
        if u:
            admin_role = role_repo.get_by_name('Admin')
            if admin_role:
                user_repo.add_role(u, admin_role)
                session.commit()
                print('✅ Compte admin créé')

    if not user_repo.get_by_username('pedagog'):
        u = create_user('pedagog', 'pedagog@example.com', 'PedagogPass123', session=session)
        if u:
            pedagog_role = role_repo.get_by_name('Pedagogical')
            if pedagog_role:
                user_repo.add_role(u, pedagog_role)
                session.commit()
                print('✅ Compte responsable pédagogique créé')

    if not user_repo.get_by_username('enseignant'):
        u = create_user('enseignant', 'enseignant@example.com', 'EnseignantPass123', session=session)
        if u:
            teacher_role = role_repo.get_by_name('Teacher')
            if teacher_role:
                user_repo.add_role(u, teacher_role)
                session.commit()
                print('✅ Compte enseignant créé')

    if not user_repo.get_by_username('etudiant'):
        u = create_user('etudiant', 'etudiant@example.com', 'EtudiantPass123', session=session)
        if u:
            student_role = role_repo.get_by_name('Student')
            if student_role:
                user_repo.add_role(u, student_role)
                session.commit()
                print('✅ Compte étudiant créé')

    session.close()
    print('\n' + '='*60)
    print('✅ SEED TERMINÉ')
    print('='*60)
    print('\nComptes créés :')
    print('  👑 Admin          : admin / AdminPass123')
    print('  👨‍🏫 Responsable   : pedagog / PedagogPass123')
    print('  🎓 Enseignant     : enseignant / EnseignantPass123')
    print('  🎒 Étudiant       : etudiant / EtudiantPass123')
    print('\nVous pouvez maintenant vous connecter !')
    print('='*60)


if __name__ == '__main__':
    seed()
