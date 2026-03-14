"""
Exporteur PDF pour les emplois du temps.

Génère des documents PDF formatés pour les emplois du temps.
"""
from typing import List, Dict, Optional
from datetime import date, datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas

from ..database.models import ScheduleSlotModel, CohortModel, TeacherModel


class PDFExporter:
    """
    Exporteur pour générer des PDFs d'emplois du temps.
    
    Formats supportés :
    - Emploi du temps d'une cohorte
    - Emploi du temps d'un enseignant
    - Rapport de retards
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialise l'exporteur PDF.
        
        Args:
            output_dir: Répertoire de sortie (outputs/schedules par défaut)
        """
        if output_dir is None:
            output_dir = Path("outputs/schedules")
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=1  # Centre
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=6
        )
    
    def export_cohort_schedule(self, cohort: CohortModel, slots: List[ScheduleSlotModel],
                               start_date: date, end_date: date) -> Path:
        """
        Exporte l'emploi du temps d'une cohorte en PDF.
        
        Args:
            cohort: Cohorte
            slots: Créneaux horaires
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Chemin du fichier PDF généré
        """
        filename = f"emploi_du_temps_{cohort.name.replace(' ', '_')}_{start_date}_{end_date}.pdf"
        filepath = self.output_dir / filename
        
        # Créer le document en mode paysage
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1*cm
        )
        
        story = []
        
        # Titre
        title = Paragraph(f"Emploi du Temps - {cohort.name}", self.title_style)
        story.append(title)
        
        # Informations
        info_text = f"Période : {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}<br/>"
        info_text += f"Année académique : {cohort.academic_year}<br/>"
        info_text += f"Semestre : {cohort.semester}"
        info = Paragraph(info_text, self.styles['Normal'])
        story.append(info)
        story.append(Spacer(1, 0.5*cm))
        
        # Organiser les créneaux par semaine
        weeks = self._organize_by_weeks(slots, start_date, end_date)
        
        for week_num, week_slots in weeks.items():
            # Titre de la semaine
            week_title = Paragraph(f"<b>Semaine {week_num}</b>", self.subtitle_style)
            story.append(week_title)
            
            # Créer la grille hebdomadaire
            table = self._create_weekly_table(week_slots)
            story.append(table)
            story.append(Spacer(1, 0.5*cm))
        
        # Générer le PDF
        doc.build(story)
        
        return filepath
    
    def export_teacher_schedule(self, teacher: TeacherModel, slots: List[ScheduleSlotModel],
                               start_date: date, end_date: date) -> Path:
        """
        Exporte l'emploi du temps d'un enseignant en PDF.
        
        Args:
            teacher: Enseignant
            slots: Créneaux horaires
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Chemin du fichier PDF généré
        """
        filename = f"emploi_du_temps_{teacher.full_name.replace(' ', '_')}_{start_date}_{end_date}.pdf"
        filepath = self.output_dir / filename
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1*cm
        )
        
        story = []
        
        # Titre
        title = Paragraph(f"Emploi du Temps - {teacher.full_name}", self.title_style)
        story.append(title)
        
        # Informations
        info_text = f"Email : {teacher.email}<br/>"
        info_text += f"Spécialité : {teacher.speciality}<br/>"
        info_text += f"Période : {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        info = Paragraph(info_text, self.styles['Normal'])
        story.append(info)
        story.append(Spacer(1, 0.5*cm))
        
        # Organiser par semaine
        weeks = self._organize_by_weeks(slots, start_date, end_date)
        
        for week_num, week_slots in weeks.items():
            week_title = Paragraph(f"<b>Semaine {week_num}</b>", self.subtitle_style)
            story.append(week_title)
            
            table = self._create_weekly_table(week_slots, teacher_view=True)
            story.append(table)
            story.append(Spacer(1, 0.5*cm))
        
        doc.build(story)
        
        return filepath
    
    def _organize_by_weeks(self, slots: List[ScheduleSlotModel], 
                          start_date: date, end_date: date) -> Dict[int, List[ScheduleSlotModel]]:
        """Organise les créneaux par semaine."""
        weeks = {}
        
        for slot in slots:
            if start_date <= slot.date <= end_date:
                # Calculer le numéro de semaine
                week_num = (slot.date - start_date).days // 7 + 1
                
                if week_num not in weeks:
                    weeks[week_num] = []
                
                weeks[week_num].append(slot)
        
        return weeks
    
    def _create_weekly_table(self, slots: List[ScheduleSlotModel], 
                            teacher_view: bool = False) -> Table:
        """
        Crée une table pour une semaine.
        
        Args:
            slots: Créneaux de la semaine
            teacher_view: Si True, affiche les cohortes au lieu des enseignants
            
        Returns:
            Table formatée
        """
        # En-têtes
        headers = ['Heure', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
        
        # Créneaux horaires (8h-18h)
        hours = ['8h-9h', '9h-10h', '10h-11h', '11h-12h', '12h-13h', 
                '13h-14h', '14h-15h', '15h-16h', '16h-17h', '17h-18h']
        
        # Créer la grille
        data = [headers]
        
        for hour in hours:
            row = [hour]
            
            # Pour chaque jour de la semaine
            for day in range(6):  # 0=Lundi, 5=Samedi
                cell_content = ''
                
                # Trouver les créneaux correspondants
                for slot in slots:
                    if slot.date.weekday() == day:
                        slot_hour = f"{slot.start_time.strftime('%H')}h-{slot.end_time.strftime('%H')}h"
                        
                        if slot_hour == hour or hour in slot_hour:
                            # Contenu de la cellule
                            if teacher_view:
                                # Vue enseignant : afficher la cohorte
                                cell_content = f"{slot.activity.name if slot.activity else 'N/A'}\n"
                                cell_content += f"Cohorte: {slot.cohort.name if slot.cohort else 'N/A'}\n"
                            else:
                                # Vue cohorte : afficher l'enseignant
                                cell_content = f"{slot.activity.name if slot.activity else 'N/A'}\n"
                                cell_content += f"Prof: {slot.teacher.full_name if slot.teacher else 'N/A'}\n"
                            
                            if slot.room:
                                cell_content += f"Salle: {slot.room}"
                            
                            break
                
                row.append(cell_content)
            
            data.append(row)
        
        # Créer la table
        table = Table(data, colWidths=[2*cm] + [4*cm]*6)
        
        # Style de la table
        table.setStyle(TableStyle([
            # En-têtes
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Première colonne (heures)
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            
            # Cellules
            ('FONTSIZE', (1, 1), (-1, -1), 7),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (1, 1), (-1, -1), 'MIDDLE'),
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        return table
    
    def export_delays_report(self, cohort: CohortModel, activities_delays: List[Dict]) -> Path:
        """
        Exporte un rapport de retards en PDF.
        
        Args:
            cohort: Cohorte
            activities_delays: Liste des activités avec leurs retards
            
        Returns:
            Chemin du fichier PDF généré
        """
        filename = f"rapport_retards_{cohort.name.replace(' ', '_')}_{date.today()}.pdf"
        filepath = self.output_dir / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        
        # Titre
        title = Paragraph(f"Rapport de Retards - {cohort.name}", self.title_style)
        story.append(title)
        
        # Date
        date_text = f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Résumé
        total_delay = sum(a.get('delay', 0) for a in activities_delays if a.get('delay', 0) > 0)
        urgent_count = sum(1 for a in activities_delays if a.get('urgency') == 'Critique')
        
        summary = f"<b>Résumé :</b><br/>"
        summary += f"Retard total : {total_delay:.1f} heures<br/>"
        summary += f"Activités critiques : {urgent_count}<br/>"
        summary += f"Activités analysées : {len(activities_delays)}"
        
        story.append(Paragraph(summary, self.styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Table des retards
        data = [['Activité', 'Volume', 'Réalisé', 'Retard', 'α', 'Urgence']]
        
        for activity_info in activities_delays:
            row = [
                activity_info.get('activity_name', 'N/A'),
                f"{activity_info.get('volume_hours', 0):.1f}h",
                f"{activity_info.get('hours_done', 0):.1f}h",
                f"{activity_info.get('delay', 0):.1f}h",
                f"{activity_info.get('alpha', 0):.2f}",
                activity_info.get('urgency', 'Normal')
            ]
            data.append(row)
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        story.append(table)
        
        doc.build(story)
        
        return filepath