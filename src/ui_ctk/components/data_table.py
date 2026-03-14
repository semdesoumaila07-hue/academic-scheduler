"""
Composant de tableau de données réutilisable pour CustomTkinter.
"""
import customtkinter as ctk
from typing import List, Dict, Optional, Callable


class DataTable(ctk.CTkFrame):
    """Tableau de données avec actions."""
    
    def __init__(self, parent, columns: List[Dict], data: List[Dict],
                 on_edit: Optional[Callable] = None, on_delete: Optional[Callable] = None,
                 on_add: Optional[Callable] = None):
        """
        Crée un tableau de données.
        
        Args:
            parent: Widget parent
            columns: Liste des colonnes [{'name': 'id', 'label': 'ID', 'width': 50}, ...]
            data: Données à afficher
            on_edit: Callback pour l'édition (reçoit l'index et les données)
            on_delete: Callback pour la suppression (reçoit l'index et les données)
            on_add: Callback pour l'ajout
        """
        super().__init__(parent)
        self.columns = columns
        self.data = data
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_add = on_add
        
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialise l'interface."""
        # Barre d'outils
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 10))
        
        if self.on_add:
            add_btn = ctk.CTkButton(toolbar, text="➕ Ajouter", command=self.on_add, width=120)
            add_btn.pack(side="left")
        
        # Scrollable frame pour le tableau
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("#E8E8E8", "#2B2B2B"))
        self.header_frame.pack(fill="x", pady=(0, 2))
        
        # Body (sera rempli par refresh)
        self.body_frame = None
    
    def refresh(self, data: Optional[List[Dict]] = None):
        """Rafraîchit le tableau."""
        if data is not None:
            self.data = data
        
        # Supprimer l'ancien body
        if self.body_frame:
            self.body_frame.destroy()
        
        # Créer le header
        for i, col in enumerate(self.columns):
            label = ctk.CTkLabel(
                self.header_frame, 
                text=col.get('label', col['name']),
                font=ctk.CTkFont(size=12, weight="bold"),
                width=col.get('width', 100)
            )
            label.grid(row=0, column=i, padx=2, pady=8, sticky="ew")
            self.header_frame.grid_columnconfigure(i, weight=col.get('weight', 1))
        
        # Créer le body
        self.body_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.body_frame.pack(fill="x")
        
        if not self.data:
            no_data = ctk.CTkLabel(self.body_frame, text="Aucune donnée disponible", text_color="gray")
            no_data.pack(pady=20)
            return
        
        # Lignes de données
        for row_idx, row_data in enumerate(self.data):
            row_frame = ctk.CTkFrame(self.body_frame, fg_color=("#F8F8F8", "#1E1E1E") if row_idx % 2 == 0 else "transparent")
            row_frame.pack(fill="x", pady=1)
            
            for col_idx, col in enumerate(self.columns):
                col_name = col['name']
                value = str(row_data.get(col_name, ''))
                
                cell = ctk.CTkLabel(
                    row_frame,
                    text=value[:50] + "..." if len(value) > 50 else value,
                    font=ctk.CTkFont(size=11),
                    width=col.get('width', 100)
                )
                cell.grid(row=0, column=col_idx, padx=2, pady=6, sticky="ew")
                row_frame.grid_columnconfigure(col_idx, weight=col.get('weight', 1))
            
            # Actions
            if self.on_edit or self.on_delete:
                actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                actions_frame.grid(row=0, column=len(self.columns), padx=5, sticky="e")
                
                if self.on_edit:
                    edit_btn = ctk.CTkButton(
                        actions_frame, text="✏️", width=30, height=30,
                        command=lambda idx=row_idx: self.on_edit(idx, self.data[idx])
                    )
                    edit_btn.pack(side="left", padx=2)
                
                if self.on_delete:
                    delete_btn = ctk.CTkButton(
                        actions_frame, text="🗑️", width=30, height=30,
                        fg_color="transparent", hover_color="#FF4444",
                        command=lambda idx=row_idx: self._confirm_delete(idx)
                    )
                    delete_btn.pack(side="left", padx=2)
    
    def _confirm_delete(self, idx: int):
        """Demande confirmation avant suppression."""
        import tkinter.messagebox as messagebox
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cet élément ?"):
            if self.on_delete:
                self.on_delete(idx, self.data[idx])
