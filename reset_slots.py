import sys; sys.path.insert(0,'.')
from src.database.db_manager import db_manager
db_manager.initialize()
s = db_manager.get_session()
from sqlalchemy import text
s.execute(text("DELETE FROM schedule_slots"))
s.commit()
print("OK tous les creneaux supprimes!")