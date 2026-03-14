import sqlite3

def check_permissions(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print('--- Permissions ---')
    cursor.execute('SELECT id, name, description FROM permissions')
    for row in cursor.fetchall():
        print(row)
    print('\n--- Roles ---')
    cursor.execute('SELECT id, name FROM roles')
    for row in cursor.fetchall():
        print(row)
    print('\n--- Admin Permissions ---')
    cursor.execute("SELECT p.name FROM permissions p JOIN role_permissions rp ON p.id = rp.permission_id JOIN roles r ON rp.role_id = r.id WHERE r.name = 'Admin'")
    for row in cursor.fetchall():
        print(row)
    conn.close()

if __name__ == '__main__':
    check_permissions('data/ordonnancement.db')
