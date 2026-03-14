import sqlite3

def add_missing_columns(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Ajoute les colonnes si elles n'existent pas déjà
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN ufr_id INTEGER")
    except sqlite3.OperationalError:
        pass  # colonne déjà existante
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN program_id INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN teacher_id INTEGER")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()
    print("Colonnes ajoutées ou déjà présentes.")

if __name__ == "__main__":
    add_missing_columns("data/ordonnancement.db")
