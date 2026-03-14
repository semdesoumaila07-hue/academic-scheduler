import sys; sys.path.insert(0,'.')
path = r'src\ui\tabs\scheduling_tab.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
for i in range(220, 295):
    print(f"{i+1}: {repr(lines[i])}")