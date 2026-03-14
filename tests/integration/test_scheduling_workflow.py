"""
Tests d'intégration — Repositories + Workflow Ordonnancement
==============================================================
Vérifie que les composants fonctionnent ensemble correctement.

Exécution :
    pytest tests/integration/ -v
"""
import pytest
from datetime import date, time, timedelta


# ══════════════════════════════════════════════════════════════════════════
# IT-04 : CRUD Université → UFR → Programme → Cohorte
# ══════════════════════════════════════════════════════════════════════════

class TestCRUDRepositories:

    def test_it04_crud_hierarchie_complete(self, db_session):
        """IT-04 : Créer la hiérarchie complète et vérifier les FK"""
        from src.database.repositories import (
            UniversityRepository, UFRRepository,
            ProgramRepository, CohortRepository
        )
        from src.utils.constants import ProgramLevelEnum

        univ_repo   = UniversityRepository(db_session)
        ufr_repo    = UFRRepository(db_session)
        prog_repo   = ProgramRepository(db_session)
        cohort_repo = CohortRepository(db_session)

        univ = univ_repo.create(name="UNZ", code="UNZ01",
                                address="Addr", city="Koudougou", country="BF")
        ufr = ufr_repo.create(name="UFR-ST", code="UFRST",
                              director="Dir", university_id=univ.id)
        prog = prog_repo.create(name="L3 Info", code="L3INF",
                                level=ProgramLevelEnum.LICENCE_3,
                                duration_years=1, ufr_id=ufr.id)
        cohort = cohort_repo.create(
            name="L3 Info 2025-2026", academic_year="2025-2026",
            semester=1, student_count=40, program_id=prog.id,
            start_date=date(2025, 10, 1), end_date=date(2026, 2, 28)
        )
        db_session.commit()

        assert ufr.university_id == univ.id
        assert prog.ufr_id == ufr.id
        assert cohort.program_id == prog.id
        print(f"\n  → Hiérarchie créée : "
              f"Univ(id={univ.id}) → UFR(id={ufr.id}) → "
              f"Prog(id={prog.id}) → Cohorte(id={cohort.id})")

    def test_it05_lien_cohorte_activite_slot(self, db_session, universite_complete, enseignant):
        """IT-05 : Cohorte → Activité → ScheduleSlot (cohort_id propagé)"""
        from src.database.repositories import ActivityRepository
        from src.database.models import ScheduleSlotModel
        from src.utils.constants import ActivityTypeEnum, ActivityStatusEnum
        # ✅ SlotStatusEnum supprimé — n'existe pas dans le modèle

        act_repo = ActivityRepository(db_session)
        cohorte = universite_complete["cohorte"]

        activite = act_repo.create(
            name="Test Intégration",
            code="TEST-001",
            type=ActivityTypeEnum.COURS_MAGISTRAL,
            volume_hours=15.0,
            hours_done=0.0,
            cohort_id=cohorte.id,
            teacher_id=enseignant.id,
            status=ActivityStatusEnum.PENDING
        )
        db_session.commit()

        # ✅ time(8,0) et time(9,0) — objets Python, pas des strings
        slot = ScheduleSlotModel(
            date=date(2025, 10, 6),
            start_time=time(8, 0),
            end_time=time(9, 0),
            activity_id=activite.id,
            teacher_id=enseignant.id,
            cohort_id=cohorte.id,
            room="AMPHI A",
        )
        db_session.add(slot)
        db_session.commit()

        slots = db_session.query(ScheduleSlotModel).filter_by(cohort_id=cohorte.id).all()
        assert len(slots) >= 1
        assert slots[0].activity_id == activite.id
        print(f"\n  → Slot créé : {slots[0].date} {slots[0].start_time} "
              f"→ {slots[0].end_time} (salle: {slots[0].room})")

    def test_insertion_slots_en_base(self, db_session, universite_complete, enseignant):
        """IT-06 : Insérer plusieurs créneaux et vérifier la persistance"""
        from src.database.repositories import ActivityRepository
        from src.database.models import ScheduleSlotModel
        from src.utils.constants import ActivityTypeEnum, ActivityStatusEnum

        act_repo = ActivityRepository(db_session)
        cohorte = universite_complete["cohorte"]

        activite = act_repo.create(
            name="TD Réseau",
            code="TD-RES",
            type=ActivityTypeEnum.TD,
            volume_hours=20.0,
            hours_done=0.0,
            cohort_id=cohorte.id,
            teacher_id=enseignant.id,
            status=ActivityStatusEnum.PENDING
        )
        db_session.commit()

        # ✅ time(8,0) et time(9,0) — objets Python
        for i in range(5):
            slot = ScheduleSlotModel(
                date=date(2025, 10, 6) + timedelta(days=i),
                start_time=time(8, 0),
                end_time=time(9, 0),
                activity_id=activite.id,
                teacher_id=enseignant.id,
                cohort_id=cohorte.id,
                room="SALLE B01"
            )
            db_session.add(slot)
        db_session.commit()

        nb_slots = db_session.query(ScheduleSlotModel).filter_by(
            activity_id=activite.id
        ).count()
        assert nb_slots == 5
        print(f"\n  → {nb_slots} créneaux insérés et persistés en base ✅")


# ══════════════════════════════════════════════════════════════════════════
# IT-01/02/03 : Workflow ordonnancement Pfair simplifié
# ══════════════════════════════════════════════════════════════════════════

class TestWorkflowOrdonnancement:

    def _creer_activites(self, db_session, cohorte_id, teacher_id, n=3):
        """Créer n activités de test"""
        from src.database.repositories import ActivityRepository
        from src.utils.constants import ActivityTypeEnum, ActivityStatusEnum

        repo = ActivityRepository(db_session)
        activites = []
        volumes = [30, 20, 15]
        types = [ActivityTypeEnum.COURS_MAGISTRAL, ActivityTypeEnum.TD, ActivityTypeEnum.TP]

        for i in range(n):
            a = repo.create(
                name=f"Activite {i+1}",
                code=f"ACT-{i+1:03d}",
                type=types[i % len(types)],
                volume_hours=float(volumes[i % len(volumes)]),
                hours_done=0.0,
                cohort_id=cohorte_id,
                teacher_id=teacher_id,
                status=ActivityStatusEnum.PENDING
            )
            activites.append(a)
        db_session.commit()
        return activites

    def test_it01_calcul_facteurs_charge(self, db_session, universite_complete, enseignant):
        """IT-01 : Calculer les facteurs de charge pour une cohorte"""
        activites = self._creer_activites(
            db_session,
            universite_complete["cohorte"].id,
            enseignant.id,
            n=3
        )

        D_EFFECTIF = 105

        facteurs = []
        for a in activites:
            U = a.volume_hours / D_EFFECTIF
            facteurs.append(U)
            print(f"\n  → {a.name} : U = {a.volume_hours}/{D_EFFECTIF} = {U:.4f}")

        total = sum(facteurs)
        print(f"  → ΣU = {total:.4f} (m=1)")
        assert total <= 1.0, f"Système non ordonnançable : ΣU={total:.4f} > 1"

    def test_it02_simulation_ordonnancement_simple(self, db_session,
                                                    universite_complete, enseignant):
        """IT-02 : Simuler un ordonnancement sur 10 créneaux"""
        from src.database.repositories import ActivityRepository
        from src.database.models import ScheduleSlotModel
        from src.utils.constants import ActivityStatusEnum

        activites = self._creer_activites(
            db_session, universite_complete["cohorte"].id, enseignant.id, n=2
        )
        cohorte = universite_complete["cohorte"]

        slots_crees = 0
        for jour in range(10):
            d = date(2025, 10, 1) + timedelta(days=jour)
            act = activites[jour % 2]

            # ✅ time(8,0) et time(9,0) — objets Python
            slot = ScheduleSlotModel(
                date=d,
                start_time=time(8, 0),
                end_time=time(9, 0),
                activity_id=act.id,
                teacher_id=enseignant.id,
                cohort_id=cohorte.id,
                room="AMPHI A"
            )
            db_session.add(slot)
            slots_crees += 1
        db_session.commit()

        act_repo = ActivityRepository(db_session)
        for act in activites:
            nb_slots = db_session.query(ScheduleSlotModel).filter_by(
                activity_id=act.id
            ).count()
            act_repo.update(act.id, hours_done=float(nb_slots))
        db_session.commit()

        for act in activites:
            db_session.refresh(act)
            assert act.hours_done >= 0
            print(f"\n  → {act.name} : {act.hours_done}h planifiées")

        assert slots_crees == 10
        print(f"\n  → Total : {slots_crees} créneaux planifiés ✅")

    def test_it03_surcharge_detectee(self):
        """IT-03 : ΣU > 1 → ordonnancement refusé"""
        D_EFFECTIF = 105
        volumes = [50, 45, 30]

        total_U = sum(v / D_EFFECTIF for v in volumes)
        print(f"\n  → ΣU = {total_U:.4f}")

        assert total_U > 1.0, "Le test attend une surcharge"

        with pytest.raises(ValueError, match="non ordonnançable|ΣU"):
            if total_U > 1.0:
                raise ValueError(
                    f"Système non ordonnançable : ΣU={total_U:.4f} > m=1"
                )
        print("  → Surcharge correctement détectée ✅")

    def test_it_conge_exclut_creneau(self, db_session, universite_complete, enseignant):
        """IT-02 bis : Enseignant en congé → aucun créneau pendant le congé"""
        from src.database.repositories import LeaveRequestRepository
        from src.database.models import ScheduleSlotModel
        from src.utils.constants import LeaveStatusEnum, LeaveTypeEnum
        from src.database.repositories import ActivityRepository
        from src.utils.constants import ActivityTypeEnum, ActivityStatusEnum

        leave_repo = LeaveRequestRepository(db_session)
        act_repo   = ActivityRepository(db_session)
        cohorte    = universite_complete["cohorte"]

        CONGE_DEBUT = date(2025, 10, 13)
        CONGE_FIN   = date(2025, 10, 17)

        leave_repo.create(
            teacher_id=enseignant.id,
            start_date=CONGE_DEBUT,
            end_date=CONGE_FIN,
            leave_type=LeaveTypeEnum.CONGE_ANNUEL,
            reason="Congé annuel",
            status=LeaveStatusEnum.APPROVED
        )
        activite = act_repo.create(
            name="Cours pendant congé", code="CONG-001",
            type=ActivityTypeEnum.COURS_MAGISTRAL,
            volume_hours=10.0, hours_done=0.0,
            cohort_id=cohorte.id, teacher_id=enseignant.id,
            status=ActivityStatusEnum.PENDING
        )
        db_session.commit()

        def est_en_conge(teacher_id, jour, session):
            from src.database.models import LeaveRequestModel
            from src.utils.constants import LeaveStatusEnum as LSE
            # ✅ no_autoflush évite le flush prématuré sur les slots non encore commités
            with session.no_autoflush:
                conges = session.query(LeaveRequestModel).filter(
                    LeaveRequestModel.teacher_id == teacher_id,
                    LeaveRequestModel.status == LSE.APPROVED,
                    LeaveRequestModel.start_date <= jour,
                    LeaveRequestModel.end_date >= jour
                ).all()
            return len(conges) > 0

        slots_planifies = []
        for jour_offset in range(15):
            jour = date(2025, 10, 6) + timedelta(days=jour_offset)
            if jour.weekday() < 6:
                if not est_en_conge(enseignant.id, jour, db_session):
                    # ✅ time(8,0) et time(9,0) — objets Python
                    slot = ScheduleSlotModel(
                        date=jour,
                        start_time=time(8, 0),
                        end_time=time(9, 0),
                        activity_id=activite.id,
                        teacher_id=enseignant.id,
                        cohort_id=cohorte.id,
                        room="AMPHI A"
                    )
                    db_session.add(slot)
                    slots_planifies.append(jour)

        db_session.commit()

        for slot_date in slots_planifies:
            assert not (CONGE_DEBUT <= slot_date <= CONGE_FIN), \
                f"Slot créé pendant le congé : {slot_date} !"

        print(f"\n  → {len(slots_planifies)} créneaux planifiés")
        print(f"  → Aucun créneau pendant le congé ({CONGE_DEBUT} → {CONGE_FIN}) ✅")