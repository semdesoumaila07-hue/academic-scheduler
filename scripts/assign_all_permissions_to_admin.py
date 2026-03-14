import sqlite3

def assign_all_permissions_to_admin(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Get Admin role id
    cursor.execute("SELECT id FROM roles WHERE name=?", ("Admin",))
    role_row = cursor.fetchone()
    if not role_row:
        print("Rôle 'Admin' introuvable.")
        conn.close()
        return
    role_id = role_row[0]
    # Get all permission ids
    cursor.execute("SELECT id FROM permissions")
    perm_rows = cursor.fetchall()
    if not perm_rows:
        print("Aucune permission trouvée.")
        conn.close()
        return
    # Assign each permission to Admin role if not already assigned
    count = 0
    for (perm_id,) in perm_rows:
        cursor.execute("SELECT 1 FROM role_permissions WHERE role_id=? AND permission_id=?", (role_id, perm_id))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)", (role_id, perm_id))
            count += 1
    conn.commit()
    print(f"{count} permissions assignées au rôle 'Admin'.")
    conn.close()

if __name__ == "__main__":
    assign_all_permissions_to_admin("data/ordonnancement.db")
