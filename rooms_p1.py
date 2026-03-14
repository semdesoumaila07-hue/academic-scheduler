import os, sys
sys.path.insert(0, r'C:\Eclipse\academic-scheduler')
os.chdir(r'C:\Eclipse\academic-scheduler')
BASE = r'C:\Eclipse\academic-scheduler'

# 1. RoomModel dans models.py
models_path = os.path.join(BASE, 'src', 'database', 'models.py')
with open(models_path, encoding='utf-8') as f:
    models = f.read()

room_model = "\n\nclass RoomModel(Base):\n    __tablename__ = 'rooms'\n    id = Column(Integer, primary_key=True, autoincrement=True)\n    name = Column(String(100), unique=True, nullable=False)\n    capacity = Column(Integer, default=30)\n    room_type = Column(String(20), default='TD')\n    building = Column(String(100))\n    is_active = Column(Boolean, default=True)\n    notes = Column(Text)\n    created_at = Column(DateTime, default=datetime.now)\n    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)\n\n"

if 'class RoomModel' not in models:
    models = models.replace('class LeaveRequestModel(Base):', room_model + 'class LeaveRequestModel(Base):')
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(models)
    print("OK RoomModel ajoute")
else:
    print("RoomModel existe deja")

# 2. Creer table rooms
from src.database.db_manager import db_manager
db_manager.initialize()
session = db_manager.get_session()
from sqlalchemy import text, inspect
inspector = inspect(db_manager.engine)
if 'rooms' not in inspector.get_table_names():
    session.execute(text("CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, capacity INTEGER DEFAULT 30, room_type TEXT DEFAULT 'TD', building TEXT, is_active INTEGER DEFAULT 1, notes TEXT, created_at DATETIME, updated_at DATETIME)"))
    session.commit()
    print("OK table rooms creee")
else:
    print("Table rooms existe deja")

try:
    existing = session.execute(text("SELECT DISTINCT room FROM schedule_slots WHERE room IS NOT NULL AND room != ''")).fetchall()
    in_table = {r[0] for r in session.execute(text("SELECT name FROM rooms")).fetchall()}
    added = 0
    for (rname,) in existing:
        if rname and rname not in in_table:
            session.execute(text("INSERT INTO rooms (name,capacity,room_type,is_active,created_at,updated_at) VALUES (:n,30,'TD',1,datetime('now'),datetime('now'))"), {'n': rname})
            added += 1
    session.commit()
    print(f"OK {added} salles migrees")
except Exception as e:
    print(f"Migration: {e}")

print("Partie 1 OK - lancez rooms_p2.py")