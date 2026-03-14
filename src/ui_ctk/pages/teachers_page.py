"""
Page de gestion des enseignants avec CRUD complet.
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import List, Dict
from ...managers.structure_manager import StructureManager
from ...database.repositories import TeacherRepository
from ...database.models import TeacherModel, TeacherStatusEnum
from ..components import FormDialog, DataTable


class TeachersPage(ctk.CTkScrollableFrame):
    """Page de gestion des enseignants."""
    
    def __init__(self, parent, session, structure_manager: StructureManager):
        super().__init__(parent, fg_color="transparent")
        self.session = session
        self.structure_manager = structure_manager
        self.teacher_repo = TeacherRepository(session)
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialise l'interface."""
        # En-tête
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header, text="Enseignants", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left")
        
        ctk.CTkButton(header, text="➕ Ajouter", command=self.add_teacher, width=120).pack(side="right")
        
        # Tableau des enseignants
        columns = [
            {'name': 'full_name', 'label': 'Nom complet', 'width': 200},
            {'name': 'email', 'label': 'Email', 'width': 200},
            {'name': 'speciality', 'label': 'Spécialité', 'width': 150},
            {'name': 'status', 'label': 'Statut', 'width': 100},
        ]
        
        self.table = DataTable(
            self, columns, [],
            on_edit=self.edit_teacher,
            on_delete=self.delete_teacher,
            on_add=self.add_teacher
        )
        self.table.pack(fill="both", expand=True)
    
    def refresh_data(self):
        """Rafraîchit les données."""
        teachers = self.teacher_repo.get_all()
        data = []
        for t in teachers:
            data.append({
                'id': t.id,
                'full_name': t.full_name,
                'email': t.email,
                'speciality': t.speciality,
                'status': t.status.value if hasattr(t.status, 'value') else str(t.status),
            })
        self.table.refresh(data)
    
    def add_teacher(self):
        """Ajoute un enseignant."""
        # Récupérer les UFRs pour le select
        ufrs = []
        for u in self.structure_manager.get_all_universities():
            for ufr in self.structure_manager.get_ufrs_by_university(u.id):
                ufrs.append(ufr)
        
        ufr_options = ["Aucun"] + [f"{ufr.name} ({ufr.code})" for ufr in ufrs]
        status_options = ["Permanent", "Vacataire", "Invité"]
        
        fields = [
            {'name': 'full_name', 'label': 'Nom complet', 'type': 'text', 'required': True},
            {'name': 'email', 'label': 'Email', 'type': 'text', 'required': True},
            {'name': 'phone', 'label': 'Téléphone', 'type': 'text', 'required': False},
            {'name': 'speciality', 'label': 'Spécialité', 'type': 'text', 'required': True},
            {'name': 'ufr', 'label': 'UFR', 'type': 'select', 'options': ufr_options, 'required': False},
            {'name': 'status', 'label': 'Statut', 'type': 'select', 'options': status_options, 'required': True},
            {'name': 'max_hours_week', 'label': 'Max heures/semaine', 'type': 'number', 'default': '40'},
            {'name': 'max_hours_day', 'label': 'Max heures/jour', 'type': 'number', 'default': '8'},
        ]
        
        def on_submit(values):
            # Trouver l'ID de l'UFR si sélectionnée
            ufr_id = None
            if values.get('ufr') and values['ufr'] != "Aucun":
                selected = values['ufr']
                for ufr in ufrs:
                    if f"{ufr.name} ({ufr.code})" == selected:
                        ufr_id = ufr.id
                        break
            
            # Convertir le statut
            status_map = {
                "Permanent": TeacherStatusEnum.PERMANENT,
                "Vacataire": TeacherStatusEnum.VACATAIRE,
                "Invité": TeacherStatusEnum.INVITE,
            }
            status = status_map.get(values['status'], TeacherStatusEnum.VACATAIRE)
            
            try:
                teacher = self.teacher_repo.create(
                    full_name=values['full_name'],
                    email=values['email'],
                    phone=values.get('phone', ''),
                    speciality=values['speciality'],
                    ufr_id=ufr_id,
                    status=status,
                    max_hours_per_week=int(values.get('max_hours_week', 40)),
                    max_hours_per_day=int(values.get('max_hours_day', 8))
                )
                messagebox.showinfo("Succès", f"Enseignant {teacher.full_name} créé")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        
        dialog = FormDialog(self, "Nouvel Enseignant", fields, on_submit)
        dialog.focus()
    
    def edit_teacher(self, idx: int, data: Dict):
        """Édite un enseignant."""
        messagebox.showinfo("Info", "Fonctionnalité d'édition à implémenter")
    
    def delete_teacher(self, idx: int, data: Dict):
        """Supprime un enseignant."""
        try:
            self.teacher_repo.delete(data['id'])
            messagebox.showinfo("Succès", "Enseignant supprimé")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
