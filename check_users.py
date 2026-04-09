from src.database.db_manager import db_manager
from src.config.settings import DATABASE_URL
from sqlalchemy import text

db_manager.initialize(DATABASE_URL)
s = db_manager.get_session()
rows = s.execute(text('SELECT username, email FROM users LIMIT 10')).fetchall()
for r in rows:
    print(r)