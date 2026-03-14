path = r'src\ui\tabs\scheduling_tab.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

old = '''                                    rows = _s2.execute(_t2(
                                        "SELECT name FROM rooms WHERE room_type=:rt AND is_active=1 AND name IN :names"
                                    ), {'rt': ptype, 'names': names}).fetchall()'''

new = '''                                    placeholders = ','.join([f':n{i}' for i in range(len(free_rooms))])
                                    params = {'rt': ptype}
                                    for i,n in enumerate(free_rooms): params[f'n{i}'] = n
                                    rows = _s2.execute(_t2(
                                        f"SELECT name FROM rooms WHERE room_type=:rt AND is_active=1 AND name IN ({placeholders})"
                                    ), params).fetchall()'''

if old in content:
    content = content.replace(old, new)
    print("OK remplacement effectue!")
else:
    print("Bloc non trouve!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

import py_compile
try:
    py_compile.compile(path, doraise=True)
    print("Syntaxe OK!")
except py_compile.PyCompileError as e:
    print(f"Erreur: {e}")