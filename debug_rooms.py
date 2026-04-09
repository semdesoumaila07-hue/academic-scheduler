import sys, os 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) 
from src.config.settings import DATABASE_URL 
from src.database.db_manager import db_manager 
from sqlalchemy import text 
db_manager.initialize(DATABASE_URL) 
s = db_manager.get_session() 
rows = s.execute(text('SELECT name, capacity FROM rooms')).fetchall() 
print("ROOMS:", rows) 
rows2 = s.execute(text('SELECT DISTINCT room FROM schedule_slots')).fetchall() 
print("SLOTS ROOMS:", rows2) 
rows3 = s.execute(text('SELECT name, student_count FROM cohorts')).fetchall() 
print("COHORTS:", rows3) 
