import sqlite3

# Copie locale de TAB_ITEMS pour éviter l'import
TAB_ITEMS = [
    (0, 'view_dashboard', '📊', 'Dashboard'),
    (1, 'manage_structure', '🏛️', 'Structure'),
    (2, 'manage_teachers', '👨‍🏫', 'Enseignants'),
    (3, 'manage_activities', '📚', 'Activités'),
    (4, 'manage_calendar', '📅', 'Calendrier'),
    (5, 'manage_leaves', '🏖️', 'Congés'),
    (6, 'launch_scheduling', '⏰', 'Ordonnancement'),
    (7, 'analyze_delays', '⏱️', 'Retards'),
    (8, 'generate_reports', '📈', 'Rapports'),
    (9, 'view_timetable', '🗓️', 'Emplois du temps'),
]

def insert_all_permissions(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    count = 0
    for _, perm_name, _, label in TAB_ITEMS:
        cursor.execute("SELECT id FROM permissions WHERE name=?", (perm_name,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO permissions (name, description) VALUES (?, ?)",
                (perm_name, label)
            )
            count += 1
    conn.commit()
    print(f"{count} permissions insérées dans la table permissions.")
    conn.close()

if __name__ == "__main__":
    insert_all_permissions("data/ordonnancement.db")
