"""
Composant de carte KPI réutilisable.
"""
import customtkinter as ctk


class KPICard(ctk.CTkFrame):
    """Carte d'indicateur clé de performance."""
    
    def __init__(self, parent, value: str, label: str, icon: str = "", color: str = "#2196F3"):
        """
        Crée une carte KPI.
        
        Args:
            parent: Widget parent
            value: Valeur à afficher
            label: Libellé
            icon: Icône (emoji ou texte)
            color: Couleur de fond
        """
        super().__init__(parent, fg_color=(color, color), corner_radius=10)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Valeur
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        value_label.pack(anchor="w", pady=(0, 4))
        
        # Label avec icône
        label_text = f"{icon} {label}" if icon else label
        label_widget = ctk.CTkLabel(
            content,
            text=label_text,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        label_widget.pack(anchor="w")
