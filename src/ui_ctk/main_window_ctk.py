"""
Fenêtre principale CustomTkinter - conforme à la conception.

Interface organisée en onglets thématiques :
Structure, Calendrier, Activités, Ordonnancement, Analyse
"""
import customtkinter as ctk
from ..data.data_manager import data_manager


class MainWindowCTK(ctk.CTkFrame):
    """Fenêtre principale conforme à la conception (CustomTkinter + JSON/CSV)."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.init_ui()

    def init_ui(self):
        # Layout principal
        self.grid_columnconfigure(1, weight=1)
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
            ("📈 Analyse / Retards", 7),
        ]
        for text, idx in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=text, anchor="w",
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

        # Pages (stacked)
        self.pages = []
        self.pages.append(self._create_dashboard_page())
        self.pages.append(self._create_structure_page())
        self.pages.append(self._create_teachers_page())
        self.pages.append(self._create_activities_page())
        self.pages.append(self._create_calendar_page())
        self.pages.append(self._create_leaves_page())
        self.pages.append(self._create_scheduling_page())
        self.pages.append(self._create_analysis_page())

        for i, p in enumerate(self.pages):
            p.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
            p.grid_columnconfigure(0, weight=1)
            p.grid_rowconfigure(1, weight=1)
            if i > 0:
                p.grid_remove()

        self.current_page = 0

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
        ctk.CTkLabel(f, text="Analyse des retards académiques", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 16))
        ctk.CTkLabel(f, text="Indicateurs de retard par activité, classe, parcours, UFR et université.", text_color="gray").grid(row=1, column=0, sticky="w")
        return f
