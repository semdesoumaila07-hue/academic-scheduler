path = r'src\ui\tabs\dashboard_tab.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
print(f"Total lignes: {len(lines)}")
for i,l in enumerate(lines):
    print(f"{i+1}: {repr(l)}")