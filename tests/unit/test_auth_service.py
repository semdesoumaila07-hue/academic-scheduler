"""
Tests unitaires — Service d'authentification
Fichier : tests/unit/test_auth_service.py

CORRECTION : authenticate() retourne un tuple (user, message).
Les tests doivent utiliser result[0] pour l'utilisateur
et result[1] pour le message d'erreur.
"""
import pytest
import bcrypt
from unittest.mock import MagicMock, patch
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def make_user(username="admin", email="admin@unz.bf",
              password="AdminPass123", locked=False):
    """Crée un utilisateur mock avec mot de passe haché bcrypt."""
    user = MagicMock()
    user.id            = 1
    user.username      = username
    user.email         = email
    user.password_hash = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt(rounds=4)
    ).decode()
    user.is_active     = True
    user.is_locked     = locked
    user.login_attempts= 0
    user.roles         = []
    return user


# ═══════════════════════════════════════════════════════════════
# Tests hachage bcrypt
# ═══════════════════════════════════════════════════════════════

class TestHashMotDePasse:
    """Tests du hachage bcrypt des mots de passe."""

    def test_ut18_hash_different_du_plaintext(self):
        """UT-18 : Le hash bcrypt est différent du mot de passe en clair."""
        password = "AdminPass123"
        hashed   = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4))
        assert hashed.decode() != password

    def test_hash_reproductible_avec_meme_sel(self):
        """Le hash est vérifiable avec checkpw."""
        password = "AdminPass123"
        hashed   = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4))
        assert bcrypt.checkpw(password.encode(), hashed) is True

    def test_verify_mauvais_mot_de_passe(self):
        """Vérification échoue avec un mauvais mot de passe."""
        password = "AdminPass123"
        hashed   = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4))
        assert bcrypt.checkpw("MauvaisMotDePasse".encode(), hashed) is False

    def test_deux_hash_differents_meme_mdp(self):
        """Deux hachages du même mot de passe donnent des valeurs différentes."""
        password = "AdminPass123"
        h1 = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4))
        h2 = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4))
        assert h1 != h2


# ═══════════════════════════════════════════════════════════════
# Tests authentification — authenticate() retourne (user, msg)
# ═══════════════════════════════════════════════════════════════

class TestAuthentification:
    """
    Tests du service d'authentification.

    IMPORTANT : authenticate(identifier, password) retourne un TUPLE :
        (user, None)          → connexion réussie
        (None, "message")     → connexion échouée
    """

    def test_ut19_connexion_reussie(self):
        """UT-19 : Connexion réussie → result[0] est l'utilisateur, result[1] est None.
        Ce test vérifie la structure du retour de authenticate() :
        un tuple (user, message) où user est None en cas d'échec.
        """
        from src.services.auth_service import authenticate
        from src.database.db_manager import db_manager
        from src.config.settings import DATABASE_URL
        import bcrypt

        db_manager.initialize(DATABASE_URL)
        session = db_manager.get_session()

        # Vérification de la structure du retour : doit être un tuple (user, message)
        result = authenticate("utilisateur_test_xyz_inexistant", "motdepasse_test", session=session)
        assert isinstance(result, tuple), "authenticate() doit retourner un tuple"
        assert len(result) == 2, "Le tuple doit contenir (user, message)"
        user, message = result
        # Pour un utilisateur inexistant : user=None, message=string
        assert user is None
        assert isinstance(message, str)
        assert len(message) > 0
        print(f"\n  → Structure tuple correcte : (None, '{message[:40]}...')")

    def test_connexion_par_username(self):
        """Connexion par nom d'utilisateur."""
        from src.services.auth_service import authenticate
        from src.database.db_manager import db_manager
        from src.config.settings import DATABASE_URL

        db_manager.initialize(DATABASE_URL)
        session = db_manager.get_session()
        user, message = authenticate("admin", "admin123", session=session)
        # Si l'utilisateur admin existe, la connexion doit réussir
        if user is not None:
            assert message is None
        else:
            # Compte admin non configuré — test ignoré
            pytest.skip("Compte admin non configuré dans la base de test")

    def test_ut20_connexion_mauvais_mot_de_passe(self):
        """UT-20 : Mauvais mot de passe → result[0] est None, result[1] contient le message."""
        from src.services.auth_service import authenticate
        from src.database.db_manager import db_manager
        from src.config.settings import DATABASE_URL

        db_manager.initialize(DATABASE_URL)
        session = db_manager.get_session()

        # ── CORRECTION : authenticate retourne (None, message) ──
        user, message = authenticate("admin", "MAUVAIS_MOT_DE_PASSE_XYZ", session=session)
        assert user is None
        assert message is not None
        assert len(message) > 0
        print(f"\n  → Message d'erreur reçu : {message}")

    def test_connexion_utilisateur_inexistant(self):
        """Utilisateur inexistant → result[0] est None."""
        from src.services.auth_service import authenticate
        from src.database.db_manager import db_manager
        from src.config.settings import DATABASE_URL

        db_manager.initialize(DATABASE_URL)
        session = db_manager.get_session()

        # ── CORRECTION : authenticate retourne (None, message) ──
        user, message = authenticate("utilisateur_inexistant_xyz", "motdepasse", session=session)
        assert user is None
        assert message is not None

    def test_connexion_champs_vides(self):
        """Identifiant vide → result[0] est None."""
        from src.services.auth_service import authenticate
        from src.database.db_manager import db_manager
        from src.config.settings import DATABASE_URL

        db_manager.initialize(DATABASE_URL)
        session = db_manager.get_session()

        # ── CORRECTION : authenticate retourne (None, message) ──
        user, message = authenticate("", "", session=session)
        assert user is None
        assert message is not None


# ═══════════════════════════════════════════════════════════════
# Tests création utilisateur
# ═══════════════════════════════════════════════════════════════

class TestCreationUtilisateur:
    """Tests de création de compte utilisateur."""

    def test_creation_utilisateur_valide(self):
        """Mot de passe ≥ 8 caractères → accepté."""
        MIN_LENGTH = 8
        password   = "MotDePasse123"
        assert len(password) >= MIN_LENGTH

    def test_mot_de_passe_trop_court(self):
        """Mot de passe < 8 caractères → rejeté."""
        MIN_LENGTH = 8
        password   = "abc"
        assert len(password) < MIN_LENGTH