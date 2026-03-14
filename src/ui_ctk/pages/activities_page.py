"""
Page de gestion des activités académiques avec CRUD complet.
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime
from typing import List, Dict
from ...managers.activity_manager import ActivityManager
from ...managers.structure_manager import StructureManager
from ...database.models import ActivityTypeEnum, PriorityEnum
from ..components import FormDialog, DataTable


class ActivitiesPage(ctk.CTkScrollableFrame):
    """Page de gestion des activités académiques."""
    
    def __init__(self, parent, session, activity_manager: ActivityManager, structure_manager: StructureManager):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.activity_manager = activity_manager
        self.structure_manager = structure_manager
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialise l'interface."""
        # En-tête
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header, text="Activités Académiques", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left")
        
        ctk.CTkButton(header, text="➕ Ajouter", command=self.add_activity, width=120).pack(side="right")
        
        # Tableau des activités
        columns = [
            {'name': 'code', 'label': 'Code', 'width': 100},
            {'name': 'name', 'label': 'Nom', 'width': 200},
            {'name': 'type', 'label': 'Type', 'width': 100},
            {'name': 'volume_hours', 'label': 'Volume (h)', 'width': 100},
            {'name': 'hours_done', 'label': 'Réalisé (h)', 'width': 100},
            {'name': 'cohort', 'label': 'Cohorte', 'width': 150},
            {'name': 'teacher', 'label': 'Enseignant', 'width': 150},
            {'name': 'priority', 'label': 'Priorité', 'width': 100},
        ]
        
        self.table = DataTable(
            self, columns, [],
            on_edit=self.edit_activity,
            on_delete=self.delete_activity,
            on_add=self.add_activity
        )
        self.table.pack(fill="both", expand=True)
    
    def refresh_data(self):
        """Rafraîchit les données."""
        activities = self.activity_manager.activity_repo.get_all()
        data = []
        for a in activities:
            # Récupérer les noms
            cohort_name = ""
            if a.cohort_id:
                cohort = self.structure_manager.cohort_repo.get_by_id(a.cohort_id)
                if cohort:
                    cohort_name = cohort.name
            
            teacher_name = ""
            if a.teacher_id:
                teacher = self.activity_manager.teacher_repo.get_by_id(a.teacher_id)
                if teacher:
                    teacher_name = teacher.full_name
            
            data.append({
                'id': a.id,
                'code': a.code,
                'name': a.name,
                'type': a.type.value if hasattr(a.type, 'value') else str(a.type),
                'volume_hours': str(a.volume_hours),
                'hours_done': str(a.hours_done),
                'cohort': cohort_name,
                'teacher': teacher_name,
                'priority': a.priority.value if hasattr(a.priority, 'value') else str(a.priority),
            })
        self.table.refresh(data)
    
    def add_activity(self):
        """Ajoute une activité."""
        # Récupérer les cohortes et enseignants
        cohorts = []
        for u in self.structure_manager.get_all_universities():
            for ufr in self.structure_manager.get_ufrs_by_university(u.id):
                for p in self.structure_manager.get_programs_by_ufr(ufr.id):
                    for c in self.structure_manager.get_cohorts_by_program(p.id):
                        cohorts.append(c)
        
        teachers = self.activity_manager.teacher_repo.get_all()
        
        cohort_options = [f"{c.name} ({c.academic_year})" for c in cohorts]
        teacher_options = ["Aucun"] + [t.full_name for t in teachers]
        
        type_options = ["Cours Magistral", "Travaux Dirigés", "Travaux Pratiques", "Examen", "Soutenance"]
        priority_options = ["Basse", "Normale", "Haute", "Urgente"]
        
        fields = [
            {'name': 'code', 'label': 'Code', 'type': 'text', 'required': True},
            {'name': 'name', 'label': 'Nom', 'type': 'text', 'required': True},
            {'name': 'type', 'label': 'Type', 'type': 'select', 'options': type_options, 'required': True},
            {'name': 'volume_hours', 'label': 'Volume horaire', 'type': 'number', 'required': True},
            {'name': 'cohort', 'label': 'Cohorte', 'type': 'select', 'options': cohort_options, 'required': True},
            {'name': 'teacher', 'label': 'Enseignant', 'type': 'select', 'options': teacher_options, 'required': False},
            {'name': 'priority', 'label': 'Priorité', 'type': 'select', 'options': priority_options, 'required': True},
            {'name': 'activation_date', 'label': 'Date d\'activation', 'type': 'date', 'required': False},
            {'name': 'deadline', 'label': 'Échéance', 'type': 'date', 'required': False},
        ]
        
        def on_submit(values):
            # Trouver l'ID de la cohorte
            selected_cohort = values['cohort']
            cohort_id = None
            for c in cohorts:
                if f"{c.name} ({c.academic_year})" == selected_cohort:
                    cohort_id = c.id
                    break
            
            if not cohort_id:
                messagebox.showerror("Erreur", "Cohorte introuvable")
                return
            
            # Trouver l'ID de l'enseignant si sélectionné
            teacher_id = None
            if values.get('teacher') and values['teacher'] != "Aucun":
                selected_teacher = values['teacher']
                for t in teachers:
                    if t.full_name == selected_teacher:
                        teacher_id = t.id
                        break
            
            # Convertir le type
            type_map = {
                "Cours Magistral": ActivityTypeEnum.COURS_MAGISTRAL,
                "Travaux Dirigés": ActivityTypeEnum.TD,
                "Travaux Pratiques": ActivityTypeEnum.TP,
                "Examen": ActivityTypeEnum.EXAMEN,
                "Soutenance": ActivityTypeEnum.SOUTENANCE,
            }
            activity_type = type_map.get(values['type'])
            
            # Convertir la priorité
            priority_map = {
                "Basse": PriorityEnum.BASSE,
                "Normale": PriorityEnum.NORMALE,
                "Haute": PriorityEnum.HAUTE,
                "Urgente": PriorityEnum.URGENTE,
            }
            priority = priority_map.get(values.get('priority', 'Normale'), PriorityEnum.NORMALE)
            
            # Parser les dates
            activation_date = None
            deadline = None
            try:
                if values.get('activation_date'):
                    activation_date = datetime.strptime(values['activation_date'], "%d/%m/%Y").date()
                if values.get('deadline'):
                    deadline = datetime.strptime(values['deadline'], "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Erreur", "Format de date invalide (JJ/MM/AAAA)")
                return
            
            result = self.activity_manager.create_activity(
                name=values['name'],
                code=values['code'],
                activity_type=activity_type,
                volume_hours=float(values['volume_hours']),
                cohort_id=cohort_id,
                teacher_id=teacher_id,
                activation_date=activation_date,
                deadline=deadline,
                priority=priority
            )
            
            if result.get('success'):
                messagebox.showinfo("Succès", result.get('message', 'Activité créée'))
                self.refresh_data()
            else:
                messagebox.showerror("Erreur", result.get('error', 'Erreur inconnue'))
        
        dialog = FormDialog(self, "Nouvelle Activité", fields, on_submit)
        dialog.focus()
    
    def edit_activity(self, idx: int, data: Dict):
        """Édite une activité."""
        messagebox.showinfo("Info", "Fonctionnalité d'édition à implémenter")
    
    def delete_activity(self, idx: int, data: Dict):
        """Supprime une activité."""
        try:
            self.activity_manager.activity_repo.delete(data['id'])
            messagebox.showinfo("Succès", "Activité supprimée")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
