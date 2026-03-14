import sqlite3

# Ajoute la permission 'declare_availability' dans la table permissions

def insert_declare_availability_permission(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    perm_name = 'declare_availability'
    label = 'Disponibilités'
    cursor.execute("SELECT id FROM permissions WHERE name=?", (perm_name,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO permissions (name, description) VALUES (?, ?)",
            (perm_name, label)
        )
        conn.commit()
        print(f"Permission '{perm_name}' insérée.")
    else:
        print(f"Permission '{perm_name}' déjà présente.")
    conn.close()

if __name__ == "__main__":
    insert_declare_availability_permission("data/ordonnancement.db")
