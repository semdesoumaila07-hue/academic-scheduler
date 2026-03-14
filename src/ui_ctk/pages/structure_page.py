"""
Page de gestion de la structure universitaire avec CRUD complet.
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime
from typing import List, Dict
from ...managers.structure_manager import StructureManager
from ...database.models import UniversityModel, UFRModel, ProgramModel, CohortModel
from ..components import FormDialog, DataTable


class StructurePage(ctk.CTkScrollableFrame):
    """Page de gestion de la structure universitaire."""
    
    def __init__(self, parent, session, structure_manager: StructureManager):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.structure_manager = structure_manager
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialise l'interface."""
        # En-tête
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header, text="Structure Universitaire", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left")
        
        # Boutons d'action
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(btn_frame, text="➕ Université", command=self.add_university, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="➕ UFR", command=self.add_ufr, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="➕ Programme", command=self.add_program, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="➕ Cohorte", command=self.add_cohort, width=120).pack(side="left", padx=5)
        
        # Vue arborescente de la structure
        self.tree_frame = ctk.CTkFrame(self, fg_color=("#F8F8F8", "#1E1E1E"))
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.tree_text = ctk.CTkTextbox(self.tree_frame, font=ctk.CTkFont(family="Consolas", size=11))
        self.tree_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def refresh_data(self):
        """Rafraîchit les données affichées."""
        universities = self.structure_manager.get_all_universities()
        
        lines = []
        for u in universities:
            lines.append(f"📌 {u.name} ({u.code})")
            ufrs = self.structure_manager.get_ufrs_by_university(u.id)
            for ufr in ufrs:
                lines.append(f"   └── {ufr.name} ({ufr.code})")
                programs = self.structure_manager.get_programs_by_ufr(ufr.id)
                for p in programs:
                    lines.append(f"        └── {p.name} ({p.code}) - {p.level.value}")
                    cohorts = self.structure_manager.get_cohorts_by_program(p.id)
                    for c in cohorts:
                        lines.append(f"             └── {c.name} ({c.academic_year}, S{c.semester}) - {c.student_count} étudiants")
        
        self.tree_text.delete("1.0", "end")
        content = "\n".join(lines) if lines else "Aucune structure. Utilisez les boutons pour ajouter."
        self.tree_text.insert("1.0", content)
        self.tree_text.configure(state="disabled")
    
    def add_university(self):
        """Ajoute une université."""
        fields = [
            {'name': 'name', 'label': 'Nom', 'type': 'text', 'required': True},
            {'name': 'code', 'label': 'Code', 'type': 'text', 'required': True},
            {'name': 'address', 'label': 'Adresse', 'type': 'text', 'required': True},
            {'name': 'city', 'label': 'Ville', 'type': 'text', 'required': True},
            {'name': 'country', 'label': 'Pays', 'type': 'text', 'default': 'Burkina Faso'},
        ]
        
        def on_submit(values):
            result = self.structure_manager.create_university(
                name=values['name'],
                code=values['code'],
                address=values['address'],
                city=values['city'],
                country=values.get('country', 'Burkina Faso')
            )
            if result.get('success'):
                messagebox.showinfo("Succès", result.get('message', 'Université créée'))
                self.refresh_data()
            else:
                messagebox.showerror("Erreur", result.get('error', 'Erreur inconnue'))
        
        dialog = FormDialog(self, "Nouvelle Université", fields, on_submit)
        dialog.focus()
    
    def add_ufr(self):
        """Ajoute une UFR."""
        universities = self.structure_manager.get_all_universities()
        if not universities:
            messagebox.showwarning("Avertissement", "Créez d'abord une université")
            return
        
        ufr_options = [f"{u.name} ({u.code})" for u in universities]
        
        fields = [
            {'name': 'university', 'label': 'Université', 'type': 'select', 'options': ufr_options, 'required': True},
            {'name': 'name', 'label': 'Nom', 'type': 'text', 'required': True},
            {'name': 'code', 'label': 'Code', 'type': 'text', 'required': True},
            {'name': 'director', 'label': 'Directeur', 'type': 'text', 'required': False},
        ]
        
        def on_submit(values):
            # Trouver l'ID de l'université sélectionnée
            selected = values['university']
            university_id = None
            for u in universities:
                if f"{u.name} ({u.code})" == selected:
                    university_id = u.id
                    break
            
            if not university_id:
                messagebox.showerror("Erreur", "Université introuvable")
                return
            
            result = self.structure_manager.create_ufr(
                name=values['name'],
                code=values['code'],
                director=values.get('director', ''),
                university_id=university_id
            )
            if result.get('success'):
                ctk.CTkMessageBox.show_info("Succès", result.get('message', 'UFR créée'))
                self.refresh_data()
            else:
                ctk.CTkMessageBox.show_error("Erreur", result.get('error', 'Erreur inconnue'))
        
        dialog = FormDialog(self, "Nouvelle UFR", fields, on_submit)
        dialog.focus()
    
    def add_program(self):
        """Ajoute un programme."""
        ufrs = []
        for u in self.structure_manager.get_all_universities():
            for ufr in self.structure_manager.get_ufrs_by_university(u.id):
                ufrs.append(ufr)
        
        if not ufrs:
            messagebox.showwarning("Avertissement", "Créez d'abord une UFR")
            return
        
        program_options = [f"{ufr.name} ({ufr.code})" for ufr in ufrs]
        level_options = ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
        
        fields = [
            {'name': 'ufr', 'label': 'UFR', 'type': 'select', 'options': program_options, 'required': True},
            {'name': 'name', 'label': 'Nom', 'type': 'text', 'required': True},
            {'name': 'code', 'label': 'Code', 'type': 'text', 'required': True},
            {'name': 'level', 'label': 'Niveau', 'type': 'select', 'options': level_options, 'required': True},
            {'name': 'duration', 'label': 'Durée (années)', 'type': 'number', 'required': True},
        ]
        
        def on_submit(values):
            from ...database.models import ProgramLevelEnum
            
            # Trouver l'ID de l'UFR sélectionnée
            selected = values['ufr']
            ufr_id = None
            for ufr in ufrs:
                if f"{ufr.name} ({ufr.code})" == selected:
                    ufr_id = ufr.id
                    break
            
            if not ufr_id:
                messagebox.showerror("Erreur", "UFR introuvable")
                return
            
            # Convertir le niveau
            level_map = {
                "Licence 1": ProgramLevelEnum.LICENCE_1,
                "Licence 2": ProgramLevelEnum.LICENCE_2,
                "Licence 3": ProgramLevelEnum.LICENCE_3,
                "Master 1": ProgramLevelEnum.MASTER_1,
                "Master 2": ProgramLevelEnum.MASTER_2,
                "Doctorat": ProgramLevelEnum.DOCTORAT,
            }
            level = level_map.get(values['level'])
            
            result = self.structure_manager.create_program(
                name=values['name'],
                code=values['code'],
                level=level,
                duration_years=int(values['duration']),
                ufr_id=ufr_id
            )
            if result.get('success'):
                ctk.CTkMessageBox.show_info("Succès", result.get('message', 'Programme créé'))
                self.refresh_data()
            else:
                ctk.CTkMessageBox.show_error("Erreur", result.get('error', 'Erreur inconnue'))
        
        dialog = FormDialog(self, "Nouveau Programme", fields, on_submit)
        dialog.focus()
    
    def add_cohort(self):
        """Ajoute une cohorte."""
        programs = []
        for u in self.structure_manager.get_all_universities():
            for ufr in self.structure_manager.get_ufrs_by_university(u.id):
                for p in self.structure_manager.get_programs_by_ufr(ufr.id):
                    programs.append(p)
        
        if not programs:
            messagebox.showwarning("Avertissement", "Créez d'abord un programme")
            return
        
        program_options = [f"{p.name} ({p.code})" for p in programs]
        
        fields = [
            {'name': 'program', 'label': 'Programme', 'type': 'select', 'options': program_options, 'required': True},
            {'name': 'name', 'label': 'Nom', 'type': 'text', 'required': True},
            {'name': 'academic_year', 'label': 'Année académique', 'type': 'text', 'placeholder': '2025-2026', 'required': True},
            {'name': 'semester', 'label': 'Semestre', 'type': 'select', 'options': ['1', '2'], 'required': True},
            {'name': 'student_count', 'label': 'Nombre d\'étudiants', 'type': 'number', 'required': True},
            {'name': 'start_date', 'label': 'Date de début', 'type': 'date', 'required': True},
            {'name': 'end_date', 'label': 'Date de fin', 'type': 'date', 'required': True},
        ]
        
        def on_submit(values):
            from datetime import datetime
            
            # Trouver l'ID du programme sélectionné
            selected = values['program']
            program_id = None
            for p in programs:
                if f"{p.name} ({p.code})" == selected:
                    program_id = p.id
                    break
            
            if not program_id:
                messagebox.showerror("Erreur", "Programme introuvable")
                return
            
            # Parser les dates
            try:
                start_date = datetime.strptime(values['start_date'], "%d/%m/%Y").date()
                end_date = datetime.strptime(values['end_date'], "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Erreur", "Format de date invalide (JJ/MM/AAAA)")
                return
            
            result = self.structure_manager.create_cohort(
                name=values['name'],
                academic_year=values['academic_year'],
                semester=int(values['semester']),
                student_count=int(values['student_count']),
                program_id=program_id,
                start_date=start_date,
                end_date=end_date
            )
            if result.get('success'):
                ctk.CTkMessageBox.show_info("Succès", result.get('message', 'Cohorte créée'))
                self.refresh_data()
            else:
                ctk.CTkMessageBox.show_error("Erreur", result.get('error', 'Erreur inconnue'))
        
        dialog = FormDialog(self, "Nouvelle Cohorte", fields, on_submit)
        dialog.focus()
