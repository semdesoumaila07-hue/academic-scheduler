import os, sys
sys.path.insert(0, r'C:\Eclipse\academic-scheduler')
os.chdir(r'C:\Eclipse\academic-scheduler')

BASE = r'C:\Eclipse\academic-scheduler'

# 1. Ajouter RoomModel dans models.py
models_path = os.path.join(BASE, 'src', 'database', 'models.py')
with open(models_path, encoding='utf-8') as f:
    models = f.read()

room_model = """

class RoomModel(Base):
    __tablename__ = 'rooms'
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), unique=True, nullable=False)
    capacity   = Column(Integer, default=30)
    room_type  = Column(String(20), default='TD')
    building   = Column(String(100))
    is_active  = Column(Boolean, default=True)
    notes      = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

"""

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
inspector = inspect(db_manager._engine)
if 'rooms' not in inspector.get_table_names():
    session.execute(text("""CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        capacity INTEGER DEFAULT 30,
        room_type TEXT DEFAULT 'TD',
        building TEXT,
        is_active INTEGER DEFAULT 1,
        notes TEXT,
        created_at DATETIME,
        updated_at DATETIME)"""))
    session.commit()
    print("OK table rooms creee")
else:
    print("Table rooms existe deja")

# Migrer salles existantes
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

# 3. Creer rooms_tab.py
rooms_tab_path = os.path.join(BASE, 'src', 'ui', 'tabs', 'rooms_tab.py')
with open(rooms_tab_path, 'w', encoding='utf-8') as f:
    f.write("""# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QTextEdit, QCheckBox, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from sqlalchemy import text
from src.database.db_manager import db_manager

ROOM_TYPES = ["Amphi","Salle TD","Salle TP","Laboratoire","Informatique","Autre"]
ROOM_TYPE_DB = ["AMPHI","TD","TP","LABO","INFORMATIQUE","AUTRE"]
COLORS = {"AMPHI":"#DBEAFE","TD":"#D1FAE5","TP":"#FEF3C7","LABO":"#EDE9FE","INFORMATIQUE":"#FCE7F3","AUTRE":"#F3F4F6"}

class RoomsTab(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.session = db_manager.get_session()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(16)
        hdr = QHBoxLayout()
        title = QLabel("Gestion des Salles")
        title.setStyleSheet("font-size:24px; font-weight:700; color:#1F2937;")
        hdr.addWidget(title); hdr.addStretch()
        btn_add = QPushButton("+ Ajouter une salle")
        btn_add.setFixedHeight(40)
        btn_add.setStyleSheet("background:#1F4E79; color:white; border-radius:7px; padding:0 20px; font-size:13px; font-weight:bold;")
        btn_add.clicked.connect(self._add_room)
        hdr.addWidget(btn_add); lay.addLayout(hdr)
        self._kpi_frame = QFrame()
        self._kpi_frame.setStyleSheet("QFrame{background:white; border:1px solid #E5E7EB; border-radius:10px; padding:12px;}")
        self._kpi_lay = QHBoxLayout(self._kpi_frame)
        lay.addWidget(self._kpi_frame)
        filt = QHBoxLayout()
        self._filter_type = QComboBox()
        self._filter_type.addItems(["Tous les types"] + ROOM_TYPES)
        self._filter_type.setFixedHeight(34); self._filter_type.currentIndexChanged.connect(self._load)
        self._filter_active = QComboBox()
        self._filter_active.addItems(["Toutes","Actives","Inactives"])
        self._filter_active.setFixedHeight(34); self._filter_active.currentIndexChanged.connect(self._load)
        filt.addWidget(QLabel("Type:")); filt.addWidget(self._filter_type)
        filt.addWidget(QLabel("Statut:")); filt.addWidget(self._filter_active); filt.addStretch()
        btn_c = QPushButton("Detecter conflits")
        btn_c.setFixedHeight(34)
        btn_c.setStyleSheet("background:#EF4444; color:white; border-radius:6px; padding:0 14px;")
        btn_c.clicked.connect(self._detect_conflicts); filt.addWidget(btn_c)
        lay.addLayout(filt)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Nom","Type","Capacite","Batiment","Statut","Utilisation","Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("QTableWidget{border:1px solid #E5E7EB; border-radius:8px;} QHeaderView::section{background:#1F4E79; color:white; padding:8px; font-weight:bold;}")
        lay.addWidget(self.table)
        self._load()

    def _load(self):
        try:
            q = "SELECT id,name,capacity,room_type,building,is_active FROM rooms WHERE 1=1"
            params = {}
            fi = self._filter_type.currentIndex()
            if fi > 0: q += " AND room_type=:rt"; params['rt'] = ROOM_TYPE_DB[fi-1]
            fa = self._filter_active.currentIndex()
            if fa == 1: q += " AND is_active=1"
            elif fa == 2: q += " AND is_active=0"
            q += " ORDER BY name"
            rooms = self.session.execute(text(q), params).fetchall()
            self.table.setRowCount(len(rooms))
            total = actives = 0
            for row,(rid,name,cap,rtype,building,is_active) in enumerate(rooms):
                total += 1
                if is_active: actives += 1
                color = COLORS.get(rtype,"#F3F4F6")
                type_label = ROOM_TYPES[ROOM_TYPE_DB.index(rtype)] if rtype in ROOM_TYPE_DB else rtype or "N/A"
                usage = self.session.execute(text("SELECT COUNT(*) FROM schedule_slots WHERE room=:n AND date>=date('now')"),{'n':name}).scalar() or 0
                items = [QTableWidgetItem(name or ""),QTableWidgetItem(type_label),QTableWidgetItem(str(cap or 0)),
                         QTableWidgetItem(building or "-"),QTableWidgetItem("Actif" if is_active else "Inactif"),
                         QTableWidgetItem(f"{usage} creneau(x)")]
                for col,item in enumerate(items):
                    item.setTextAlignment(Qt.AlignCenter)
                    if col==1: item.setBackground(QColor(color))
                    if col==4: item.setForeground(QColor("#10B981") if is_active else QColor("#EF4444"))
                    self.table.setItem(row,col,item)
                btn_w = QWidget(); btn_l = QHBoxLayout(btn_w); btn_l.setContentsMargins(2,2,2,2); btn_l.setSpacing(4)
                for label,color_btn,cb in [("Dispo","#3B82F6",lambda r=rid,n=name:self._show_avail(r,n)),
                                            ("Modifier","#F59E0B",lambda r=rid:self._edit_room(r)),
                                            ("Supprimer","#EF4444",lambda r=rid,n=name:self._delete_room(r,n))]:
                    b = QPushButton(label); b.setFixedHeight(26)
                    b.setStyleSheet(f"background:{color_btn}; color:white; border-radius:4px; padding:0 6px; font-size:10px;")
                    b.clicked.connect(cb); btn_l.addWidget(b)
                self.table.setCellWidget(row,6,btn_w)
            self._update_kpis(total,actives)
        except Exception as e:
            print(f"RoomsTab load error: {e}")

    def _update_kpis(self,total,actives):
        while self._kpi_lay.count():
            item=self._kpi_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        try:
            today=self.session.execute(text("SELECT COUNT(DISTINCT room) FROM schedule_slots WHERE date=date('now')")).scalar() or 0
            conflicts=self.session.execute(text("SELECT COUNT(*) FROM (SELECT date,start_time,room FROM schedule_slots WHERE room IS NOT NULL GROUP BY date,start_time,room HAVING COUNT(*)>1)")).scalar() or 0
        except: today=conflicts=0
        for label,val,color in [("Total salles",str(total),"#3B82F6"),("Actives",str(actives),"#10B981"),
                                  ("Occupees auj.",str(today),"#F59E0B"),("Conflits",str(conflicts),"#EF4444" if conflicts>0 else "#10B981")]:
            f=QFrame(); f.setStyleSheet(f"QFrame{{background:{color}; border-radius:8px; padding:10px;}}")
            v=QVBoxLayout(f)
            lv=QLabel(val); lv.setStyleSheet("font-size:22px; font-weight:bold; color:white;"); lv.setAlignment(Qt.AlignCenter)
            ll=QLabel(label); ll.setStyleSheet("font-size:11px; color:white;"); ll.setAlignment(Qt.AlignCenter)
            v.addWidget(lv); v.addWidget(ll); self._kpi_lay.addWidget(f)

    def _add_room(self):
        dlg=RoomDialog(self.session,parent=self)
        if dlg.exec_()==QDialog.Accepted: self._load()

    def _edit_room(self,room_id):
        dlg=RoomDialog(self.session,room_id=room_id,parent=self)
        if dlg.exec_()==QDialog.Accepted: self._load()

    def _delete_room(self,room_id,name):
        usage=self.session.execute(text("SELECT COUNT(*) FROM schedule_slots WHERE room=:n"),{'n':name}).scalar() or 0
        msg=f"Supprimer '{name}' ?"
        if usage>0: msg+=f"\\n\\nAttention: {usage} creneau(x) utilisent cette salle!"
        if QMessageBox.question(self,"Confirmation",msg)==QMessageBox.Yes:
            try:
                self.session.execute(text("DELETE FROM rooms WHERE id=:id"),{'id':room_id})
                self.session.commit(); self._load()
            except Exception as e: QMessageBox.critical(self,"Erreur",str(e))

    def _show_avail(self,room_id,name):
        RoomAvailDialog(self.session,name,parent=self).exec_()

    def _detect_conflicts(self):
        try:
            rows=self.session.execute(text("""SELECT s.date,s.start_time,s.end_time,s.room,COUNT(*) as nb
                FROM schedule_slots s WHERE s.room IS NOT NULL AND s.room!=''
                GROUP BY s.date,s.start_time,s.room HAVING COUNT(*)>1 ORDER BY s.date DESC LIMIT 20""")).fetchall()
            if not rows: QMessageBox.information(self,"Conflits","Aucun conflit detecte!"); return
            msg=f"{len(rows)} conflit(s):\\n\\n"
            for d,st,et,room,nb in rows: msg+=f"Salle {room} | {d} {str(st)[:5]}-{str(et)[:5]} | {nb} cours\\n"
            QMessageBox.warning(self,f"{len(rows)} Conflit(s)",msg)
        except Exception as e: QMessageBox.critical(self,"Erreur",str(e))

    def showEvent(self,event):
        super().showEvent(event); self._load()


class RoomDialog(QDialog):
    def __init__(self,session,room_id=None,parent=None):
        super().__init__(parent)
        self.session=session; self.room_id=room_id
        self.setWindowTitle("Modifier" if room_id else "Ajouter une salle")
        self.setFixedWidth(400); self._build()
        if room_id: self._load_room()

    def _build(self):
        lay=QVBoxLayout(self); lay.setSpacing(12); lay.setContentsMargins(20,20,20,20)
        title=QLabel("Modifier salle" if self.room_id else "Nouvelle salle")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#1F2937;"); lay.addWidget(title)
        form=QFormLayout(); form.setSpacing(8)
        st="border:1px solid #D1D5DB; border-radius:5px; padding:0 8px;"
        self.inp_name=QLineEdit(); self.inp_name.setFixedHeight(34); self.inp_name.setStyleSheet(st)
        self.inp_cap=QSpinBox(); self.inp_cap.setRange(1,1000); self.inp_cap.setValue(30); self.inp_cap.setFixedHeight(34)
        self.inp_type=QComboBox(); self.inp_type.addItems(ROOM_TYPES); self.inp_type.setFixedHeight(34); self.inp_type.setStyleSheet(st)
        self.inp_building=QLineEdit(); self.inp_building.setFixedHeight(34); self.inp_building.setStyleSheet(st)
        self.chk_active=QCheckBox("Salle active"); self.chk_active.setChecked(True)
        form.addRow("Nom *",self.inp_name); form.addRow("Type *",self.inp_type)
        form.addRow("Capacite",self.inp_cap); form.addRow("Batiment",self.inp_building)
        form.addRow("",self.chk_active); lay.addLayout(form)
        btns=QHBoxLayout(); btns.addStretch()
        bc=QPushButton("Annuler"); bc.setFixedHeight(36); bc.setStyleSheet("border:1px solid #D1D5DB; border-radius:5px; padding:0 14px;"); bc.clicked.connect(self.reject)
        bs=QPushButton("Enregistrer"); bs.setFixedHeight(36); bs.setStyleSheet("background:#1F4E79; color:white; border-radius:5px; padding:0 18px; font-weight:bold;"); bs.clicked.connect(self._save)
        btns.addWidget(bc); btns.addWidget(bs); lay.addLayout(btns)

    def _load_room(self):
        r=self.session.execute(text("SELECT name,capacity,room_type,building,is_active FROM rooms WHERE id=:id"),{'id':self.room_id}).fetchone()
        if r:
            self.inp_name.setText(r[0] or ""); self.inp_cap.setValue(r[1] or 30)
            if r[2] in ROOM_TYPE_DB: self.inp_type.setCurrentIndex(ROOM_TYPE_DB.index(r[2]))
            self.inp_building.setText(r[3] or ""); self.chk_active.setChecked(bool(r[4]))

    def _save(self):
        name=self.inp_name.text().strip()
        if not name: QMessageBox.warning(self,"Erreur","Nom obligatoire."); return
        cap=self.inp_cap.value(); rtype=ROOM_TYPE_DB[self.inp_type.currentIndex()]
        building=self.inp_building.text().strip(); active=1 if self.chk_active.isChecked() else 0
        try:
            if self.room_id:
                self.session.execute(text("UPDATE rooms SET name=:n,capacity=:c,room_type=:rt,building=:b,is_active=:a,updated_at=datetime('now') WHERE id=:id"),
                    {'n':name,'c':cap,'rt':rtype,'b':building,'a':active,'id':self.room_id})
            else:
                self.session.execute(text("INSERT INTO rooms (name,capacity,room_type,building,is_active,created_at,updated_at) VALUES (:n,:c,:rt,:b,:a,datetime('now'),datetime('now'))"),
                    {'n':name,'c':cap,'rt':rtype,'b':building,'a':active})
            self.session.commit(); self.accept()
        except Exception as e: QMessageBox.critical(self,"Erreur",str(e))


class RoomAvailDialog(QDialog):
    def __init__(self,session,room_name,parent=None):
        super().__init__(parent)
        self.session=session; self.room_name=room_name
        self.setWindowTitle(f"Disponibilite - {room_name}"); self.setFixedSize(580,460); self._build()

    def _build(self):
        lay=QVBoxLayout(self); lay.setContentsMargins(16,16,16,16); lay.setSpacing(10)
        lay.addWidget(QLabel(f"Creneaux a venir - {self.room_name}"))
        slots=self.session.execute(text("""SELECT s.date,s.start_time,s.end_time,a.name,t.full_name
            FROM schedule_slots s LEFT JOIN academic_activities a ON a.id=s.activity_id
            LEFT JOIN teachers t ON t.id=s.teacher_id
            WHERE s.room=:r AND s.date>=date('now') ORDER BY s.date,s.start_time LIMIT 50"""),{'r':self.room_name}).fetchall()
        table=QTableWidget(len(slots),5)
        table.setHorizontalHeaderLabels(["Date","Debut","Fin","Activite","Enseignant"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setStyleSheet("QHeaderView::section{background:#1F4E79; color:white; padding:6px;}")
        for row,(d,st,et,act,teacher) in enumerate(slots):
            for col,val in enumerate([str(d),str(st)[:5],str(et)[:5],act or "?",teacher or "?"]):
                item=QTableWidgetItem(val); item.setTextAlignment(Qt.AlignCenter); table.setItem(row,col,item)
        lay.addWidget(table)
        btn=QPushButton("Fermer"); btn.setFixedHeight(34)
        btn.setStyleSheet("background:#1F4E79; color:white; border-radius:5px; padding:0 18px;"); btn.clicked.connect(self.accept)
        hl=QHBoxLayout(); hl.addStretch(); hl.addWidget(btn); lay.addLayout(hl)
""")
print("OK rooms_tab.py cree!")

# 4. __init__.py
init_path = os.path.join(BASE, 'src', 'ui', 'tabs', '__init__.py')
with open(init_path, encoding='utf-8') as f:
    init = f.read()
if 'RoomsTab' not in init:
    with open(init_path, 'a', encoding='utf-8') as f:
        f.write('\nfrom .rooms_tab import RoomsTab\n')
    print("OK __init__.py mis a jour")

# 5. main_window.py
main_path = os.path.join(BASE, 'src', 'ui', 'main_window.py')
with open(main_path, encoding='utf-8') as f:
    mw = f.read()
if 'RoomsTab' not in mw:
    mw = mw.replace('from src.ui.tabs.reports_tab import ReportsTab',
                     'from src.ui.tabs.reports_tab import ReportsTab\nfrom src.ui.tabs.rooms_tab import RoomsTab')
    mw = mw.replace("self.tabs.addTab(self.reports_tab",
                     "self.rooms_tab = RoomsTab(current_user=self.current_user)\n        self.tabs.addTab(self.rooms_tab, 'Salles')\n        self.tabs.addTab(self.reports_tab")
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(mw)
    print("OK main_window.py mis a jour")

print("\n=== INSTALLATION TERMINEE ===")
print("Lancez: python main.py")