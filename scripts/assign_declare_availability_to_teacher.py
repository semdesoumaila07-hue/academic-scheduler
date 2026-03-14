import sqlite3

# Ajoute la permission 'declare_availability' au rôle Enseignant

def assign_declare_availability_to_teacher(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Récupérer l'id du rôle Enseignant
    cursor.execute("SELECT id FROM roles WHERE name=?", ("Enseignant",))
    role_row = cursor.fetchone()
    if not role_row:
        print("Rôle 'Enseignant' introuvable.")
        conn.close()
        return
    role_id = role_row[0]
    # Récupérer l'id de la permission
    cursor.execute("SELECT id FROM permissions WHERE name=?", ("declare_availability",))
    perm_row = cursor.fetchone()
    if not perm_row:
        print("Permission 'declare_availability' introuvable.")
        conn.close()
        return
    perm_id = perm_row[0]
    # Associer la permission si pas déjà fait
    cursor.execute("SELECT 1 FROM role_permissions WHERE role_id=? AND permission_id=?", (role_id, perm_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, perm_id))
        conn.commit()
        print("Permission 'declare_availability' assignée au rôle Enseignant.")
    else:
        print("Permission déjà présente pour Enseignant.")
    conn.close()

if __name__ == "__main__":
    assign_declare_availability_to_teacher("data/ordonnancement.db")
