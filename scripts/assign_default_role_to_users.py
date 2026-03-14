"""
Script pour attribuer le rôle "Enseignant" à tous les utilisateurs sans rôle.
"""
from src.database.db_manager import db_manager
from src.database.repositories.user_repository import UserRepository
from src.database.repositories.role_repository import RoleRepository

def main():
    db_manager.initialize()
    session = db_manager.get_session()
    try:
        user_repo = UserRepository(session)
        role_repo = RoleRepository(session)
        default_role = role_repo.get_by_name("Enseignant")
        if not default_role:
            print("Rôle 'Enseignant' introuvable !")
            return
        users = user_repo.get_all()
        count = 0
        for user in users:
            if not user.roles:
                user_repo.add_role(user, default_role)
                print(f"Rôle 'Enseignant' attribué à : {user.username} ({user.email})")
                count += 1
        if count == 0:
            print("Tous les utilisateurs ont déjà un rôle.")
        else:
            print(f"{count} utilisateur(s) mis à jour.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
