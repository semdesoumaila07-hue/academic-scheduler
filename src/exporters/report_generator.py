"""
Générateur de rapports complets.

Crée des rapports analytiques combinant plusieurs sources de données.
"""
from typing import List, Dict, Optional
from datetime import date, datetime
from pathlib import Path

from ..database.models import CohortModel, AcademicActivityModel
from .pdf_exporter import PDFExporter
from .excel_exporter import ExcelExporter


class ReportGenerator:
    """
    Générateur de rapports complets.
    
    Types de rapports :
    - Rapport d'activité d'une cohorte
    - Rapport de performance
    - Rapport de charge enseignants
    - Bilan de période
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialise le générateur de rapports.
        
        Args:
            output_dir: Répertoire de sortie (outputs/reports par défaut)
        """
        if output_dir is None:
            output_dir = Path("outputs/reports")
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.pdf_exporter = PDFExporter(output_dir)
        self.excel_exporter = ExcelExporter(output_dir)
    
    def generate_cohort_report(self, cohort: CohortModel, 
                              activities: List[AcademicActivityModel],
                              schedule_slots: List,
                              delays_info: Dict) -> Dict[str, Path]:
        """
        Génère un rapport complet pour une cohorte.
        
        Args:
            cohort: Cohorte
            activities: Activités de la cohorte
            schedule_slots: Créneaux planifiés
            delays_info: Informations sur les retards
            
        Returns:
            Dictionnaire avec les chemins des fichiers générés
        """
        generated_files = {}
        
        # Rapport PDF des retards
        if delays_info.get('activities'):
            pdf_path = self.pdf_exporter.export_delays_report(
                cohort, 
                delays_info['activities']
            )
            generated_files['delays_pdf'] = pdf_path
        
        # Rapport Excel des retards
        if delays_info.get('activities'):
            excel_path = self.excel_exporter.export_delays_report(
                cohort,
                delays_info['activities']
            )
            generated_files['delays_excel'] = excel_path
        
        # Emploi du temps PDF
        if schedule_slots:
            start_date = min(s.date for s in schedule_slots)
            end_date = max(s.date for s in schedule_slots)
            
            schedule_pdf = self.pdf_exporter.export_cohort_schedule(
                cohort, schedule_slots, start_date, end_date
            )
            generated_files['schedule_pdf'] = schedule_pdf
        
        # Liste des activités Excel
        if activities:
            activities_excel = self.excel_exporter.export_activities(activities)
            generated_files['activities_excel'] = activities_excel
        
        return generated_files
    
    def generate_performance_report(self, cohort: CohortModel,
                                   activities_delays: List[Dict]) -> Dict:
        """
        Génère un rapport de performance.
        
        Args:
            cohort: Cohorte
            activities_delays: Informations détaillées sur les retards
            
        Returns:
            Dictionnaire avec les statistiques de performance
        """
        report = {
            'cohort_name': cohort.name,
            'academic_year': cohort.academic_year,
            'semester': cohort.semester,
            'generated_date': datetime.now(),
            'statistics': {}
        }
        
        if not activities_delays:
            return report
        
        # Calculer les statistiques
        total_activities = len(activities_delays)
        
        total_volume = sum(a.get('volume_hours', 0) for a in activities_delays)
        total_done = sum(a.get('hours_done', 0) for a in activities_delays)
        total_remaining = sum(a.get('remaining_hours', 0) for a in activities_delays)
        
        total_delay = sum(a.get('delay', 0) for a in activities_delays if a.get('delay', 0) > 0)
        
        critical_count = sum(1 for a in activities_delays if a.get('urgency') == 'Critique')
        urgent_count = sum(1 for a in activities_delays if a.get('urgency') == 'Urgent')
        normal_count = sum(1 for a in activities_delays if a.get('urgency') == 'Normal')
        
        global_completion = (total_done / total_volume * 100) if total_volume > 0 else 0
        
        # Activité la plus en retard
        max_delay_activity = max(activities_delays, key=lambda a: a.get('delay', 0))
        
        # Activité la plus avancée
        max_completion_activity = max(activities_delays, key=lambda a: a.get('completion', 0))
        
        report['statistics'] = {
            'total_activities': total_activities,
            'total_volume_hours': round(total_volume, 1),
            'total_hours_done': round(total_done, 1),
            'total_hours_remaining': round(total_remaining, 1),
            'global_completion_percent': round(global_completion, 1),
            'total_delay_hours': round(total_delay, 1),
            'activities_critical': critical_count,
            'activities_urgent': urgent_count,
            'activities_normal': normal_count,
            'most_delayed_activity': {
                'name': max_delay_activity.get('activity_name'),
                'delay': round(max_delay_activity.get('delay', 0), 1),
                'alpha': round(max_delay_activity.get('alpha', 0), 2)
            },
            'most_advanced_activity': {
                'name': max_completion_activity.get('activity_name'),
                'completion': round(max_completion_activity.get('completion', 0), 1)
            }
        }
        
        return report
    
    def generate_teacher_workload_report(self, teachers_data: List[Dict]) -> Dict:
        """
        Génère un rapport de charge des enseignants.
        
        Args:
            teachers_data: Données sur les enseignants et leur charge
            
        Returns:
            Dictionnaire avec les statistiques
        """
        report = {
            'generated_date': datetime.now(),
            'total_teachers': len(teachers_data),
            'teachers': []
        }
        
        for teacher_info in teachers_data:
            teacher_stat = {
                'name': teacher_info.get('name'),
                'email': teacher_info.get('email'),
                'speciality': teacher_info.get('speciality'),
                'total_hours_scheduled': teacher_info.get('total_hours', 0),
                'activities_count': teacher_info.get('activities_count', 0),
                'max_hours_per_week': teacher_info.get('max_hours_per_week', 40),
                'utilization_rate': 0
            }
            
            # Taux d'utilisation
            if teacher_stat['max_hours_per_week'] > 0:
                teacher_stat['utilization_rate'] = round(
                    (teacher_stat['total_hours_scheduled'] / teacher_stat['max_hours_per_week']) * 100,
                    1
                )
            
            report['teachers'].append(teacher_stat)
        
        # Trier par charge décroissante
        report['teachers'].sort(key=lambda t: t['total_hours_scheduled'], reverse=True)
        
        # Statistiques globales
        if report['teachers']:
            avg_hours = sum(t['total_hours_scheduled'] for t in report['teachers']) / len(report['teachers'])
            max_hours = max(t['total_hours_scheduled'] for t in report['teachers'])
            min_hours = min(t['total_hours_scheduled'] for t in report['teachers'])
            
            report['global_stats'] = {
                'average_hours': round(avg_hours, 1),
                'max_hours': round(max_hours, 1),
                'min_hours': round(min_hours, 1),
                'overloaded_count': sum(1 for t in report['teachers'] if t['utilization_rate'] > 100),
                'underloaded_count': sum(1 for t in report['teachers'] if t['utilization_rate'] < 50)
            }
        
        return report
    
    def generate_period_summary(self, start_date: date, end_date: date,
                               statistics: Dict) -> Dict:
        """
        Génère un bilan de période.
        
        Args:
            start_date: Date de début de la période
            end_date: Date de fin de la période
            statistics: Statistiques de la période
            
        Returns:
            Dictionnaire avec le bilan
        """
        summary = {
            'period': {
                'start': start_date,
                'end': end_date,
                'duration_days': (end_date - start_date).days + 1
            },
            'generated_date': datetime.now(),
            'statistics': statistics,
            'recommendations': []
        }
        
        # Générer des recommandations
        if statistics.get('total_delay_hours', 0) > 10:
            summary['recommendations'].append({
                'type': 'WARNING',
                'message': 'Retard important détecté. Planifier des rattrapages.'
            })
        
        if statistics.get('activities_critical', 0) > 0:
            summary['recommendations'].append({
                'type': 'URGENT',
                'message': f"{statistics['activities_critical']} activité(s) critique(s) nécessitent une attention immédiate."
            })
        
        if statistics.get('global_completion_percent', 0) < 50:
            summary['recommendations'].append({
                'type': 'WARNING',
                'message': 'Progression globale faible. Vérifier la faisabilité de l\'ordonnancement.'
            })
        
        if statistics.get('global_completion_percent', 0) > 90:
            summary['recommendations'].append({
                'type': 'SUCCESS',
                'message': 'Excellente progression ! Continuer sur cette voie.'
            })
        
        return summary
    
    def export_summary_text(self, summary: Dict) -> Path:
        """
        Exporte un résumé en fichier texte.
        
        Args:
            summary: Dictionnaire de résumé
            
        Returns:
            Chemin du fichier texte
        """
        filename = f"resume_{date.today()}.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RÉSUMÉ DE PÉRIODE\n")
            f.write("=" * 60 + "\n\n")
            
            # Période
            period = summary.get('period', {})
            f.write(f"Période : {period.get('start')} - {period.get('end')}\n")
            f.write(f"Durée : {period.get('duration_days')} jours\n\n")
            
            # Statistiques
            stats = summary.get('statistics', {})
            f.write("STATISTIQUES :\n")
            f.write("-" * 40 + "\n")
            
            for key, value in stats.items():
                f.write(f"{key.replace('_', ' ').title()} : {value}\n")
            
            f.write("\n")
            
            # Recommandations
            recommendations = summary.get('recommendations', [])
            if recommendations:
                f.write("RECOMMANDATIONS :\n")
                f.write("-" * 40 + "\n")
                
                for rec in recommendations:
                    f.write(f"[{rec['type']}] {rec['message']}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"Généré le : {summary.get('generated_date')}\n")
        
        return filepath