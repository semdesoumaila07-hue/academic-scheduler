import sqlite3

def assign_teacher_role_to_user(db_path, username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Vérifier l'utilisateur
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user_row = cursor.fetchone()
    if not user_row:
        print(f"Utilisateur '{username}' introuvable.")
        conn.close()
        return
    user_id = user_row[0]
    # Vérifier le rôle Enseignant
    cursor.execute("SELECT id FROM roles WHERE name=?", ("Enseignant",))
    role_row = cursor.fetchone()
    if not role_row:
        print("Rôle 'Enseignant' introuvable.")
        conn.close()
        return
    role_id = role_row[0]
    # Associer le rôle à l'utilisateur
    cursor.execute("SELECT 1 FROM user_roles WHERE user_id=? AND role_id=?", (user_id, role_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
        conn.commit()
        print(f"Rôle 'Enseignant' associé à l'utilisateur '{username}'.")
    else:
        print(f"L'utilisateur '{username}' a déjà le rôle 'Enseignant'.")
    conn.close()

if __name__ == "__main__":
    assign_teacher_role_to_user("data/ordonnancement.db", "RAMDE")
