"""
Composant de dialogue de formulaire réutilisable pour CustomTkinter.
"""
import customtkinter as ctk
from typing import Dict, List, Optional, Callable


class FormDialog(ctk.CTkToplevel):
    """Dialogue de formulaire réutilisable."""
    
    def __init__(self, parent, title: str, fields: List[Dict], 
                 on_submit: Optional[Callable] = None, initial_data: Optional[Dict] = None):
        """
        Crée un dialogue de formulaire.
        
        Args:
            parent: Fenêtre parente
            title: Titre du dialogue
            fields: Liste de champs du formulaire
                Format: [{'name': 'nom', 'label': 'Nom', 'type': 'text', 'required': True}, ...]
            on_submit: Callback appelé lors de la soumission (reçoit les données)
            initial_data: Données initiales pour pré-remplir le formulaire
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("600x500")
        self.resizable(False, False)
        
        self.fields = fields
        self.on_submit = on_submit
        self.values = {}
        self.widgets = {}
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ctk.CTkLabel(main_frame, text=title, font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Scrollable frame pour les champs
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True)
        
        # Créer les champs
        for field in fields:
            self._create_field(scroll_frame, field, initial_data)
        
        # Boutons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(button_frame, text="Annuler", command=self.cancel, width=120)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        submit_btn = ctk.CTkButton(button_frame, text="Enregistrer", command=self.submit, width=120)
        submit_btn.pack(side="right")
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_field(self, parent, field: Dict, initial_data: Optional[Dict]):
        """Crée un champ du formulaire."""
        name = field['name']
        label = field.get('label', name)
        field_type = field.get('type', 'text')
        required = field.get('required', False)
        default = field.get('default', '')
        options = field.get('options', [])
        
        # Frame pour le champ
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Label
        label_text = f"{label}{' *' if required else ''}"
        ctk.CTkLabel(field_frame, text=label_text, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 5))
        
        # Widget selon le type
        initial_value = initial_data.get(name, default) if initial_data else default
        
        if field_type == 'text':
            widget = ctk.CTkEntry(field_frame, height=35)
            if initial_value:
                widget.insert(0, str(initial_value))
            widget.pack(fill="x")
            
        elif field_type == 'number':
            widget = ctk.CTkEntry(field_frame, height=35)
            if initial_value:
                widget.insert(0, str(initial_value))
            widget.pack(fill="x")
            
        elif field_type == 'textarea':
            widget = ctk.CTkTextbox(field_frame, height=100)
            if initial_value:
                widget.insert("1.0", str(initial_value))
            widget.pack(fill="x")
            
        elif field_type == 'select':
            widget = ctk.CTkComboBox(field_frame, height=35, values=options)
            if initial_value and initial_value in options:
                widget.set(initial_value)
            elif options:
                widget.set(options[0])
            widget.pack(fill="x")
            
        elif field_type == 'date':
            widget = ctk.CTkEntry(field_frame, height=35, placeholder_text="JJ/MM/AAAA")
            if initial_value:
                widget.insert(0, str(initial_value))
            widget.pack(fill="x")
            
        else:
            widget = ctk.CTkEntry(field_frame, height=35)
            if initial_value:
                widget.insert(0, str(initial_value))
            widget.pack(fill="x")
        
        self.widgets[name] = widget
    
    def get_values(self) -> Dict:
        """Récupère les valeurs du formulaire."""
        values = {}
        for field in self.fields:
            name = field['name']
            field_type = field.get('type', 'text')
            widget = self.widgets[name]
            
            if field_type == 'textarea':
                values[name] = widget.get("1.0", "end-1c")
            elif field_type == 'select':
                values[name] = widget.get()
            else:
                values[name] = widget.get()
        
        return values
    
    def validate(self) -> bool:
        """Valide le formulaire."""
        import tkinter.messagebox as messagebox
        for field in self.fields:
            if field.get('required', False):
                name = field['name']
                value = self.get_values().get(name, '').strip()
                if not value:
                    messagebox.showerror("Erreur", f"Le champ '{field.get('label', name)}' est obligatoire")
                    return False
        return True
    
    def submit(self):
        """Soumet le formulaire."""
        if not self.validate():
            return
        
        values = self.get_values()
        if self.on_submit:
            self.on_submit(values)
        self.destroy()
    
    def cancel(self):
        """Annule le formulaire."""
        self.destroy()
