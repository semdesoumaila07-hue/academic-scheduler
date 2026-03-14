def assign_admin_role(db_path, username):
def assign_admin_role(db_path, email):
import sqlite3
import os
def assign_admin_role(db_path, email):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Vérifier l'utilisateur par email
    cursor.execute("SELECT id, username FROM users WHERE email=?", (email,))
    user_row = cursor.fetchone()
    if not user_row:
        print(f"Utilisateur avec l'email '{email}' introuvable.")
        conn.close()
        return
    user_id = user_row[0]
    username = user_row[1]
    # Vérifier le rôle Admin
    cursor.execute("SELECT id FROM roles WHERE name=?", ("Admin",))
    role_row = cursor.fetchone()
    if not role_row:
        print("Rôle 'Admin' introuvable. Création...")
        cursor.execute("INSERT INTO roles (name) VALUES (?)", ("Admin",))
        conn.commit()
        cursor.execute("SELECT id FROM roles WHERE name=?", ("Admin",))
        role_row = cursor.fetchone()
    role_id = role_row[0]
    # Associer le rôle à l'utilisateur
    cursor.execute("SELECT 1 FROM user_roles WHERE user_id=? AND role_id=?", (user_id, role_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
        conn.commit()
        print(f"Rôle 'Admin' associé à l'utilisateur '{username}' ({email}).")
    else:
        print(f"L'utilisateur '{username}' ({email}) a déjà le rôle 'Admin'.")
    conn.close()

if __name__ == "__main__":
    # Chemin robuste pour la base de données
    db_path = os.path.join("data", "ordonnancement.db")
    assign_admin_role(db_path, "semde@gmail.com")
