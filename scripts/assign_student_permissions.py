import sqlite3

# Permissions à accorder à l'étudiant
PERMISSIONS = [
    'view_timetable',
    'analyze_delays',
]

def assign_permissions_to_student(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Vérifier le rôle Étudiant
    cursor.execute("SELECT id FROM roles WHERE name=?", ("Étudiant",))
    role_row = cursor.fetchone()
    if not role_row:
        print("Rôle 'Étudiant' introuvable. Création...")
        cursor.execute("INSERT INTO roles (name) VALUES (?)", ("Étudiant",))
        conn.commit()
        cursor.execute("SELECT id FROM roles WHERE name=?", ("Étudiant",))
        role_row = cursor.fetchone()
    role_id = role_row[0]
    # Associer les permissions
    count = 0
    for perm_name in PERMISSIONS:
        cursor.execute("SELECT id FROM permissions WHERE name=?", (perm_name,))
        perm_row = cursor.fetchone()
        if perm_row:
            perm_id = perm_row[0]
            cursor.execute("SELECT 1 FROM role_permissions WHERE role_id=? AND permission_id=?", (role_id, perm_id))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, perm_id))
                count += 1
    conn.commit()
    print(f"{count} permissions assignées au rôle 'Étudiant'.")
    conn.close()

if __name__ == "__main__":
    assign_permissions_to_student("data/ordonnancement.db")
