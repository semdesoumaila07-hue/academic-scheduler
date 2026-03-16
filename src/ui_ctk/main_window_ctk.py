"""
Fenêtre principale CustomTkinter - conforme à la conception.

Interface organisée en onglets thématiques :
Structure, Calendrier, Activités, Ordonnancement, Analyse
"""
import customtkinter as ctk
from ..data.data_manager import data_manager
<<<<<<< HEAD
from ..database.db_manager import db_manager
from ..services.dashboard_service import DashboardService
from ..managers.structure_manager import StructureManager
from ..managers.activity_manager import ActivityManager
from .pages import StructurePage, TeachersPage, ActivitiesPage


class MainWindowCTK(ctk.CTkFrame):
    """Fenêtre principale conforme à la conception (DB + CustomTkinter)."""
=======


class MainWindowCTK(ctk.CTkFrame):
    """Fenêtre principale conforme à la conception (CustomTkinter + JSON/CSV)."""
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
<<<<<<< HEAD
        
        # Initialiser la base de données
        try:
            db_manager.initialize()
            db_manager.create_tables()
            self.session = db_manager.get_session()
            self.dashboard_service = DashboardService(self.session)
            self.structure_manager = StructureManager(self.session)
            self.activity_manager = ActivityManager(self.session)
        except Exception as e:
            print(f"⚠️ Erreur initialisation BD: {e}")
            self.session = None
            self.dashboard_service = None
            self.structure_manager = None
            self.activity_manager = None
        
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        self.init_ui()

    def init_ui(self):
        # Layout principal
        self.grid_columnconfigure(1, weight=1)
<<<<<<< HEAD
        self.grid_rowconfigure(2, weight=1)

        # Sidebar gauche
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("#f5f5f5", "#2b2b2b"))
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Branding amélioré
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=12, pady=16)
        
        # Logo coloré
        logo_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_frame.pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="📚", font=ctk.CTkFont(size=32)).pack(side="left", padx=(4, 8))
        branding = ctk.CTkFrame(logo_frame, fg_color="transparent")
        branding.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(branding, text="Pfair Scheduler", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(branding, text="Ordonnancement", font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")
        
        # Séparateur
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=("gray80", "gray30"))
        sep.pack(fill="x", padx=8, pady=12)
=======
        self.grid_rowconfigure(1, weight=1)

        # Sidebar gauche
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#e9ecef", "#2b2b2b"))
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Branding
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=20)
        ctk.CTkLabel(brand_frame, text="📘", font=ctk.CTkFont(size=28)).pack(anchor="w")
        ctk.CTkLabel(brand_frame, text="Pfair Scheduler", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(brand_frame, text="Ordonnancement académique", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f

        # Navigation
        self.nav_buttons = []
        nav_items = [
            ("📊 Dashboard", 0),
            ("🏛️ Structure", 1),
            ("👨‍🏫 Enseignants", 2),
            ("📚 Activités", 3),
            ("📅 Calendrier", 4),
            ("🏖️ Congés", 5),
            ("🔄 Ordonnancement", 6),
<<<<<<< HEAD
            ("📈 Retards", 7),
            ("📋 Rapports", 8),
            ("⏱️ Emplois du temps", 9),
=======
            ("📈 Analyse / Retards", 7),
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        ]
        for text, idx in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=text, anchor="w",
<<<<<<< HEAD
                fg_color="transparent", hover_color=("#E8F0FF", "#1a3a52"),
                text_color=("black", "white"),
                command=lambda i=idx: self.show_page(i)
            )
            btn.pack(fill="x", padx=8, pady=3, ipady=8)
            self.nav_buttons.append(btn)

        # Top Header avec Logo et Infos utilisateur
        self.top_header = ctk.CTkFrame(self, height=70, fg_color=("white", "#1a1a1a"), corner_radius=0)
        self.top_header.grid(row=0, column=1, sticky="ew", padx=0, pady=0)
        self.top_header.grid_propagate(False)
        self.top_header.grid_columnconfigure(0, weight=1)
        
        # Contenu du header
        header_content = ctk.CTkFrame(self.top_header, fg_color="transparent")
        header_content.grid(row=0, column=0, sticky="ew", padx=24, pady=12)
        header_content.grid_columnconfigure(0, weight=1)
        
        left_header = ctk.CTkFrame(header_content, fg_color="transparent")
        left_header.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left_header, text="📘 Pfair Scheduler", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=(0, 16))
        ctk.CTkLabel(left_header, text="Ordonnancement des activités académique", font=ctk.CTkFont(size=12), text_color="gray").pack(side="left")
        
        right_header = ctk.CTkFrame(header_content, fg_color="transparent")
        right_header.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(right_header, text="🔵", font=ctk.CTkFont(size=20)).pack(side="left", padx=8)
        ctk.CTkLabel(right_header, text="SOUMAILA SEMDE", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))

        # Barre de navigation horizontale sous le header
        self.nav_bar = ctk.CTkFrame(self, height=50, fg_color=("white", "#1a1a1a"), corner_radius=0)
        self.nav_bar.grid(row=1, column=1, sticky="ew", padx=0, pady=0)
        self.nav_bar.grid_propagate(False)
        
        nav_content = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        nav_content.pack(fill="both", expand=True, padx=24, pady=0)
        
        self.tab_buttons = []
        tab_items = [
            ("Dashboard", 0),
            ("Structure", 1),
            ("Enseignants", 2),
            ("Activités", 3),
            ("Calendrier", 4),
            ("Congés", 5),
            ("Ordonnancement", 6),
            ("Retards", 7),
            ("Rapports", 8),
            ("Emplois du temps", 9),
        ]
        for text, idx in tab_items:
            btn = ctk.CTkButton(
                nav_content, text=text, font=ctk.CTkFont(size=11),
                fg_color="transparent", hover_color=("gray90", "gray20"),
                text_color=("black", "white"),
                corner_radius=0, border_width=0,
                command=lambda i=idx: self.show_page(i)
            )
            btn.pack(side="left", padx=12, pady=12)
            self.tab_buttons.append(btn)

        # Zone contenu
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
=======
                fg_color="transparent", hover_color=("#E3F2FD", "#1a3a52"),
                command=lambda i=idx: self.show_page(i)
            )
            btn.pack(fill="x", padx=8, pady=4)
            self.nav_buttons.append(btn)

        # Zone contenu
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self.content_frame, height=60, fg_color=("white", "#1a1a1a"), corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)
        self.page_title = ctk.CTkLabel(self.header, text="Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
        self.page_title.grid(row=0, column=0, sticky="w", padx=24, pady=16)
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f

        # Pages (stacked)
        self.pages = []
        self.pages.append(self._create_dashboard_page())
<<<<<<< HEAD
        # Utiliser les pages améliorées avec CRUD complet
        if self.session and self.structure_manager:
            self.pages.append(StructurePage(self.content_frame, self.session, self.structure_manager))
            self.pages.append(TeachersPage(self.content_frame, self.session, self.structure_manager))
            if self.activity_manager:
                self.pages.append(ActivitiesPage(self.content_frame, self.session, self.activity_manager, self.structure_manager))
            else:
                self.pages.append(self._create_activities_page())
        else:
            self.pages.append(self._create_structure_page())
            self.pages.append(self._create_teachers_page())
            self.pages.append(self._create_activities_page())
=======
        self.pages.append(self._create_structure_page())
        self.pages.append(self._create_teachers_page())
        self.pages.append(self._create_activities_page())
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        self.pages.append(self._create_calendar_page())
        self.pages.append(self._create_leaves_page())
        self.pages.append(self._create_scheduling_page())
        self.pages.append(self._create_analysis_page())
<<<<<<< HEAD
        self.pages.append(self._create_reports_page())
        self.pages.append(self._create_timetable_page())

        for i, p in enumerate(self.pages):
            p.grid(row=0, column=0, sticky="nsew", padx=24, pady=16)
=======

        for i, p in enumerate(self.pages):
            p.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
            p.grid_columnconfigure(0, weight=1)
            p.grid_rowconfigure(1, weight=1)
            if i > 0:
                p.grid_remove()

        self.current_page = 0
<<<<<<< HEAD
        self._update_button_states()

    def show_page(self, index: int):
        self.pages[self.current_page].grid_remove()
        self.current_page = index
        self.pages[index].grid()
        self._update_button_states()

    def _update_button_states(self):
        """Highlight le bouton actif dans la navigation."""
        for i, btn in enumerate(self.nav_buttons):
            if i == self.current_page:
                btn.configure(fg_color=("#E8F0FF", "#1a3a52"), text_color=("#0052CC", "lightblue"))
            else:
                btn.configure(fg_color="transparent", text_color=("black", "white"))
        for i, btn in enumerate(self.tab_buttons):
            if i == self.current_page:
                btn.configure(text_color=("#0052CC", "white"), 
                            border_width=2, border_color=("#0052CC", "lightblue"))
            else:
                btn.configure(text_color=("black", "gray"), border_width=0)

    def _create_dashboard_page(self) -> ctk.CTkFrame:
        """Tableau de bord professionnel - données depuis BD."""
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)

        # Titre et sous-titre
        ctk.CTkLabel(f, text="Tableau de bord", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(f, text="Système d'Ordonnancement Académique P-équitable", font=ctk.CTkFont(size=13), text_color="gray").pack(anchor="w", pady=(0, 24))

        # Obtenir les données du Dashboard Service
        if self.dashboard_service:
            try:
                dashboard_data = self.dashboard_service.get_dashboard_data()
                kpis = dashboard_data['kpis']
                recent_activities = dashboard_data['recent_activities']
                completion_info = dashboard_data['completion_percentage']
            except Exception as e:
                print(f"⚠️ Erreur Dashboard: {e}")
                kpis = []
                recent_activities = []
                completion_info = 0
        else:
            kpis = []
            recent_activities = []
            completion_info = 0

        # Cartes de statistiques (KPIs)
        kpi_frame = ctk.CTkFrame(f, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 24))
        
        for i, kpi in enumerate(kpis):
            col = i % 4
            if col == 0 and i > 0:
                kpi_frame = ctk.CTkFrame(f, fg_color="transparent")
                kpi_frame.pack(fill="x", pady=(0, 24))
            
            card = ctk.CTkFrame(kpi_frame, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
            if col == 0:
                card.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=0)
            elif col == 3:
                card.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=0)
            else:
                card.pack(side="left", fill="both", expand=True, padx=12, pady=0)
            
            card.grid_columnconfigure(0, weight=1)
            value_label = ctk.CTkLabel(card, text=str(kpi['value']), font=ctk.CTkFont(size=22, weight="bold"))
            value_label.pack(anchor="w", padx=16, pady=(12, 2))
            label_label = ctk.CTkLabel(card, text=f"{kpi['icon']} {kpi['label']}", text_color="gray", font=ctk.CTkFont(size=11))
            label_label.pack(anchor="w", padx=16, pady=(0, 12))

        # Barre de progression
        ctk.CTkLabel(f, text="Progression globale", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(24, 8))
        
        progress_frame = ctk.CTkFrame(f, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
        progress_frame.pack(fill="x", pady=(0, 24))
        
        progress_content = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_content.pack(fill="both", expand=True, padx=16, pady=12)
        
        info_label = ctk.CTkLabel(progress_content, text=f"Progression: {completion_info}%", font=ctk.CTkFont(weight="bold"))
        info_label.pack(anchor="w", pady=(0, 10))
        
        progress_bar = ctk.CTkProgressBar(progress_content, value=completion_info/100 if completion_info else 0)
        progress_bar.pack(fill="x", padx=0, pady=(0, 10))

        # Section activités récentes
        ctk.CTkLabel(f, text="Activités récentes", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(8, 16))
        
        if recent_activities:
            for a in recent_activities:
                activity_card = ctk.CTkFrame(f, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
                activity_card.pack(fill="x", pady=8)
                activity_card.grid_columnconfigure(0, weight=1)
                
                top = ctk.CTkFrame(activity_card, fg_color="transparent")
                top.pack(fill="x", padx=16, pady=(12, 4))
                top.grid_columnconfigure(0, weight=1)
                
                ctk.CTkLabel(top, text=a['name'], font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
                
                status_color = "lightgreen" if a['status'] == "Terminé" else "lightblue"
                ctk.CTkLabel(top, text=f"📌 {a['status']}", text_color=status_color, font=ctk.CTkFont(size=10)).grid(row=0, column=1, sticky="e")
                
                details = f"{a['type']} • {a['hours_done']}/{a['volume_hours']}h ({a['completion_percentage']}%)"
                ctk.CTkLabel(activity_card, text=details, text_color="gray", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=16, pady=(0, 12))
        else:
            ctk.CTkLabel(f, text="Aucune activité enregistrée.", text_color="gray").pack(anchor="w")
        
        # Footer avec logos universitaires
        f.pack_propagate(False)
        footer = ctk.CTkFrame(f, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=30)
        
        univ_logos = ["🎓 MESRSI", "📚 UNF2", "🏫 UJRZ", "🏛️ UNB", "🎒 UPS", "📖 UBDG"]
        for logo in univ_logos:
            ctk.CTkLabel(footer, text=logo, font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=8)
=======

    def show_page(self, index: int):
        titles = ["Dashboard", "Structure", "Enseignants", "Activités", "Calendrier", "Congés", "Ordonnancement", "Analyse"]
        self.page_title.configure(text=titles[index] if index < len(titles) else "Dashboard")
        self.pages[self.current_page].grid_remove()
        self.current_page = index
        self.pages[index].grid()

    def _create_dashboard_page(self) -> ctk.CTkFrame:
        """Tableau de bord avec KPIs."""
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f, text="Tableau de bord", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctk.CTkLabel(f, text="Système d'Ordonnancement Académique P-équitable", text_color="gray").grid(row=1, column=0, sticky="w", pady=(0, 20))

        # KPIs
        univs = data_manager.get_universities()
        teachers = data_manager.get_teachers()
        activities = data_manager.get_activities()
        n_ufr = sum(len(getattr(u, "ufrs", [])) for u in univs)
        n_classes = 0
        n_students = 0
        for u in univs:
            for ufr in getattr(u, "ufrs", []):
                for p in getattr(ufr, "parcours", []):
                    cls = getattr(p, "classes", [])
                    n_classes += len(cls)
                    for c in cls:
                        n_students += getattr(c, "effectif", 0)
        vol = sum(getattr(a, "volume_hours", 0) for a in activities)
        done = sum(getattr(a, "hours_done", 0) for a in activities)

        kpis = [
            ("Universités", str(len(univs)), "#4A90E2"),
            ("UFR", str(n_ufr), "#7ED321"),
            ("Enseignants", str(len(teachers)), "#BD10E0"),
            ("Activités", str(len(activities)), "#F5A623"),
            ("Classes", str(n_classes), "#BD10E0"),
            ("Étudiants", str(n_students), "#F8E71C"),
            ("Heures planifiées", f"{int(done)}h", "#50E3C2"),
            ("Volume total", f"{int(vol)}h", "#F5A623"),
        ]
        kpi_frame = ctk.CTkFrame(f, fg_color="transparent")
        kpi_frame.grid(row=2, column=0, sticky="ew", pady=10)
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for i, (label, val, _) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
            card.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(card, text=label, text_color="gray", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f

        return f

    def _create_structure_page(self) -> ctk.CTkFrame:
        """Structure universitaire (onglet Structure)."""
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f, text="Structure Universitaire", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 16))
        text = ctk.CTkTextbox(f, height=400, font=ctk.CTkFont(family="Consolas", size=12))
        text.grid(row=1, column=0, sticky="nsew", pady=10)

        lines = []
        for u in data_manager.get_universities():
            lines.append(f"📌 {u.name} ({u.code})")
            for ufr in getattr(u, "ufrs", []):
                lines.append(f"   └── {ufr.nom} ({ufr.code})")
                for p in getattr(ufr, "parcours", []):
                    lines.append(f"        └── {p.nom} ({p.code})")
                    for c in getattr(p, "classes", []):
                        lines.append(f"             └── {c.nom} ({getattr(c, 'effectif', 0)} étudiants)")
        text.insert("1.0", "\n".join(lines) if lines else "Aucune structure. Utilisez les boutons pour ajouter.")
        text.configure(state="disabled")

        return f

    def _create_teachers_page(self) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        ctk.CTkLabel(f, text="Enseignants", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 16))
        for t in data_manager.get_teachers():
            card = ctk.CTkFrame(f, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=t.full_name, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(card, text=f"{t.email} • {t.speciality}", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(0, 12))
        if not data_manager.get_teachers():
            ctk.CTkLabel(f, text="Aucun enseignant enregistré.", text_color="gray").pack(anchor="w")
        return f

    def _create_activities_page(self) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        ctk.CTkLabel(f, text="Activités académiques", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 16))
        for a in data_manager.get_activities():
            card = ctk.CTkFrame(f, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=a.name, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(card, text=f"{a.type} - {a.volume_hours}h ({a.status})", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(0, 12))
        if not data_manager.get_activities():
            ctk.CTkLabel(f, text="Aucune activité enregistrée.", text_color="gray").pack(anchor="w")
        return f

    def _create_calendar_page(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        ctk.CTkLabel(f, text="Calendrier académique", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 16))
        ctk.CTkLabel(f, text="Module calendrier - Import/Export calendrier.xml conforme à la conception", text_color="gray").grid(row=1, column=0, sticky="w")
        return f

    def _create_leaves_page(self) -> ctk.CTkFrame:
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        ctk.CTkLabel(f, text="Congés enseignants", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 16))
        for lv in data_manager.get_leaves():
            card = ctk.CTkFrame(f, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=f"{lv.start_date} → {lv.end_date}", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(card, text=f"{lv.type} - {getattr(lv, 'reason', '')} ({getattr(lv, 'status', '')})", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(0, 12))
        if not data_manager.get_leaves():
            ctk.CTkLabel(f, text="Aucune demande de congé.", text_color="gray").pack(anchor="w")
        return f

    def _create_scheduling_page(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        ctk.CTkLabel(f, text="Ordonnancement Pfair", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 16))
        ctk.CTkLabel(f, text="Lancement de l'ordonnancement automatique selon l'algorithme P-équitable.", text_color="gray").grid(row=1, column=0, sticky="w")
        btn = ctk.CTkButton(f, text="🔄 Lancer l'ordonnancement", width=200, height=40)
        btn.grid(row=2, column=0, sticky="w", pady=20)
        return f

    def _create_analysis_page(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self.content_frame, fg_color="transparent")
<<<<<<< HEAD
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text="Analyse des retards académiques", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 16))
        ctk.CTkLabel(f, text="Indicateurs de retard par activité, classe, parcours, UFR et université.", text_color="gray").grid(row=1, column=0, sticky="w")
        return f

    def _create_reports_page(self) -> ctk.CTkFrame:
        """Page de génération de rapports."""
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(f, text="Rapports", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 16))
        
        reports = [
            ("📊 Rapport de synthèse", "Vue globale des activités et des ordonnancement"),
            ("📈 Rapport d'analyse", "Analyse détaillée des retards et des délais"),
            ("📋 Rapport d'ordonnancement", "Détails complets de l'ordonnancement"),
            ("🎓 Rapport étudiant", "Données par classe et parcours"),
            ("👨‍🏫 Rapport enseignant", "Charge de travail et disponibilités"),
        ]
        
        for title, desc in reports:
            card = ctk.CTkFrame(f, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
            card.pack(fill="x", pady=8)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=16, pady=12)
            content.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(content, text=title, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
            btn = ctk.CTkButton(content, text="Générer", width=80, height=28, font=ctk.CTkFont(size=11))
            btn.grid(row=0, column=1, sticky="e")
            
            ctk.CTkLabel(content, text=desc, text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        
        return f

    def _create_timetable_page(self) -> ctk.CTkFrame:
        """Page des emplois du temps."""
        f = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(f, text="Emplois du temps", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 16))
        
        timetable_options = [
            ("👨‍🏫 Emploi du temps enseignant", "Vue détaillée par enseignant"),
            ("🎓 Emploi du temps étudiant", "Vue détaillée par classe ou parcours"),
            ("📅 Calendrier académique", "Vue générale du calendrier"),
            ("⏱️ Créneau horaires", "Gestion des créneaux et salles"),
        ]
        
        for title, desc in timetable_options:
            card = ctk.CTkFrame(f, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=8)
            card.pack(fill="x", pady=8)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=16, pady=12)
            content.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(content, text=title, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
            btn = ctk.CTkButton(content, text="Afficher", width=80, height=28, font=ctk.CTkFont(size=11))
            btn.grid(row=0, column=1, sticky="e")
            
            ctk.CTkLabel(content, text=desc, text_color="gray", font=ctk.CTkFont(size=11)).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        
        return f
=======
        ctk.CTkLabel(f, text="Analyse des retards académiques", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 16))
        ctk.CTkLabel(f, text="Indicateurs de retard par activité, classe, parcours, UFR et université.", text_color="gray").grid(row=1, column=0, sticky="w")
        return f
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
