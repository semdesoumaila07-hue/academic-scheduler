"""
Script de vérification des rôles et permissions.

Affiche un rapport détaillé de tous les rôles, permissions et leurs associations.
"""
from src.database.db_manager import db_manager
from src.database.repositories import RoleRepository, PermissionRepository, UserRepository
from src.services.permissions_config import TAB_ITEMS


def verify_roles_permissions():
    """Vérifie et affiche tous les rôles et permissions."""
    db_manager.initialize()
    session = db_manager.get_session()
    
    role_repo = RoleRepository(session)
    perm_repo = PermissionRepository(session)
    user_repo = UserRepository(session)
    
    print("=" * 80)
    print("🔐 VÉRIFICATION DES RÔLES ET PERMISSIONS")
    print("=" * 80)
    print()
    
    # 1. Liste des permissions
    print("📋 PERMISSIONS DISPONIBLES")
    print("-" * 80)
    all_permissions = perm_repo.get_all()
    if not all_permissions:
        print("❌ Aucune permission trouvée dans la base de données")
        print("   Exécutez: python src/scripts/seed_auth.py")
    else:
        for perm in all_permissions:
            print(f"  ✅ {perm.name:30} - {perm.description}")
    print()
    
    # 2. Liste des rôles avec leurs permissions
    print("👥 RÔLES ET LEURS PERMISSIONS")
    print("-" * 80)
    all_roles = role_repo.get_all()
    if not all_roles:
        print("❌ Aucun rôle trouvé dans la base de données")
        print("   Exécutez: python src/scripts/seed_auth.py")
    else:
        for role in all_roles:
            print(f"\n  🎭 {role.name} ({role.description})")
            role_perms = getattr(role, 'permissions', [])
            if role_perms:
                for perm in role_perms:
                    print(f"     ✅ {perm.name}")
            else:
                print(f"     ⚠️  Aucune permission assignée")
    print()
    
    # 3. Matrice des permissions par rôle
    print("📊 MATRICE DES PERMISSIONS PAR RÔLE")
    print("-" * 80)
    if all_permissions and all_roles:
        # En-tête
        header = f"{'Permission':<30}"
        for role in all_roles:
            header += f" {role.name[:10]:<12}"
        print(header)
        print("-" * 80)
        
        # Lignes
        for perm in all_permissions:
            row = f"{perm.name:<30}"
            for role in all_roles:
                role_perms = [p.name for p in getattr(role, 'permissions', [])]
                if perm.name in role_perms:
                    row += " ✅         "
                else:
                    row += " ❌         "
            print(row)
    print()
    
    # 4. Permissions par onglet
    print("📑 PERMISSIONS PAR ONGLET")
    print("-" * 80)
    for idx, perm_name, icon, label in TAB_ITEMS:
        perm = perm_repo.get_by_name(perm_name)
        if perm:
            roles_with_perm = [r.name for r in all_roles 
                              if perm_name in [p.name for p in getattr(r, 'permissions', [])]]
            roles_str = ", ".join(roles_with_perm) if roles_with_perm else "Aucun"
            print(f"  {icon} {label:<25} ({perm_name:<25}) → {roles_str}")
        else:
            print(f"  {icon} {label:<25} ({perm_name:<25}) → ⚠️  Permission non trouvée")
    print()
    
    # 5. Utilisateurs et leurs rôles
    print("👤 UTILISATEURS ET LEURS RÔLES")
    print("-" * 80)
    all_users = user_repo.get_all()
    if not all_users:
        print("❌ Aucun utilisateur trouvé dans la base de données")
    else:
        for user in all_users:
            user_roles = getattr(user, 'roles', [])
            roles_str = ", ".join([r.name for r in user_roles]) if user_roles else "Aucun rôle"
            print(f"  👤 {user.username:<20} ({user.email:<30}) → {roles_str}")
            
            # Afficher les permissions de l'utilisateur
            if user_roles:
                user_perms = set()
                for role in user_roles:
                    for perm in getattr(role, 'permissions', []):
                        user_perms.add(perm.name)
                if user_perms:
                    print(f"     Permissions: {', '.join(sorted(user_perms))}")
    print()
    
    # 6. Vérification des méthodes protégées
    print("🔒 MÉTHODES PROTÉGÉES PAR PERMISSION")
    print("-" * 80)
    protected_methods = {
        'manage_structure': [
            'StructureManager.create_university()',
            'StructureManager.create_ufr()',
            'StructureManager.create_program()',
            'StructureManager.create_cohort()',
            'StructureManager.create_student()',
        ],
        'manage_activities': [
            'ActivityManager.create_activity()',
            'ActivityManager.update_activity()',
        ],
        'launch_scheduling': [
            'ScheduleGenerator.generate_schedule()',
        ],
        'adjust_schedule': [
            'ScheduleGenerator.adjust_schedule()',
        ],
    }
    
    for perm_name, methods in protected_methods.items():
        perm = perm_repo.get_by_name(perm_name)
        if perm:
            print(f"\n  🔐 {perm_name}")
            for method in methods:
                print(f"     • {method}")
        else:
            print(f"\n  ⚠️  {perm_name} (permission non trouvée)")
    print()
    
    # 7. Résumé et recommandations
    print("📝 RÉSUMÉ ET RECOMMANDATIONS")
    print("-" * 80)
    
    issues = []
    
    # Vérifier que toutes les permissions TAB_ITEMS existent
    for _, perm_name, _, _ in TAB_ITEMS:
        if not perm_repo.get_by_name(perm_name):
            issues.append(f"Permission manquante: {perm_name}")
    
    # Vérifier que les rôles standards existent
    standard_roles = ['Admin', 'Pedagogical', 'Teacher', 'Student']
    for role_name in standard_roles:
        if not role_repo.get_by_name(role_name):
            issues.append(f"Rôle manquant: {role_name}")
    
    if issues:
        print("⚠️  PROBLÈMES DÉTECTÉS:")
        for issue in issues:
            print(f"  • {issue}")
        print("\n💡 SOLUTION: Exécutez 'python src/scripts/seed_auth.py'")
    else:
        print("✅ Tous les rôles et permissions sont correctement configurés")
    
    print()
    print("=" * 80)
    
    session.close()


if __name__ == '__main__':
    verify_roles_permissions()
