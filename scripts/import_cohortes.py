import sqlite3
import json

def import_cohortes(json_path, db_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cohortes = data.get('cohortes', [])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    count = 0
    for c in cohortes:
        # Vérifier si la cohorte existe déjà
        cursor.execute('SELECT 1 FROM cohorts WHERE name=?', (c['nom'],))
        if cursor.fetchone():
            continue
        cursor.execute(
            'INSERT INTO cohorts (name, academic_year, semester, student_count, program_id, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                c['nom'],
                c['annee_academique'],
                1,  # Semestre (conversion possible)
                c['effectif'],
                1,  # program_id (à adapter si besoin)
                c['date_debut'],
                c['date_fin']
            )
        )
        count += 1
    conn.commit()
    print(f"{count} cohortes importées.")
    conn.close()

if __name__ == '__main__':
    import_cohortes('data/structure.json', 'data/ordonnancement.db')
