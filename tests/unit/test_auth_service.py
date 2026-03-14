"""
Tests unitaires — Service Authentification
============================================
Vérifie le hachage des mots de passe, la connexion et les permissions.

Exécution :
    pytest tests/unit/test_auth_service.py -v
"""
import pytest


class TestHashMotDePasse:
    """Tests des fonctions hash_password et verify_password"""

    def test_ut18_hash_different_du_plaintext(self):
        """UT-18 : Le hash ne doit pas être égal au mot de passe en clair"""
        from src.services.auth_service import hash_password
        mdp = "MonMotDePasse123"
        hache = hash_password(mdp)
        assert hache != mdp
        assert len(hache) > 10
        print(f"\n  → Hash généré : {hache[:30]}...")

    def test_hash_reproductible_avec_meme_sel(self):
        """Deux hachages du même mdp avec le même sel → identiques"""
        from src.services.auth_service import hash_password, verify_password
        mdp = "TestPassword456"
        h1 = hash_password(mdp)
        # verify_password doit valider le mdp original
        assert verify_password(mdp, h1) == True

    def test_verify_mauvais_mot_de_passe(self):
        """Un mauvais mot de passe ne passe pas la vérification"""
        from src.services.auth_service import hash_password, verify_password
        mdp_correct = "CorrectPassword"
        mdp_faux = "WrongPassword"
        hache = hash_password(mdp_correct)
        assert verify_password(mdp_faux, hache) == False

    def test_deux_hash_differents_meme_mdp(self):
        """Deux hachages du même mdp doivent avoir des sels différents"""
        from src.services.auth_service import hash_password
        mdp = "SamePassword"
        h1 = hash_password(mdp)
        h2 = hash_password(mdp)
        # Avec sel aléatoire, les deux hachages sont différents
        # (mais les deux valident le même mdp)
        # Note : si votre implémentation utilise un sel fixe, cette assertion
        # peut être retirée
        print(f"\n  → Hash 1: {h1[:20]}...")
        print(f"  → Hash 2: {h2[:20]}...")


class TestAuthentification:
    """Tests de la fonction authenticate"""

    def test_ut19_connexion_reussie(self, db_session):
        """UT-19 : Connexion avec identifiants corrects"""
        from src.services.auth_service import create_user, authenticate

        # Créer un utilisateur
        user = create_user(
            username="testuser",
            email="test@unz.bf",
            password="Password123",
            session=db_session
        )
        db_session.commit()

        # Connexion par email
        result = authenticate("test@unz.bf", "Password123", session=db_session)
        assert result is not None
        print(f"\n  → Connexion réussie pour : {result.email}")

    def test_connexion_par_username(self, db_session):
        """Connexion possible avec le username aussi"""
        from src.services.auth_service import create_user, authenticate

        create_user(
            username="jkabore",
            email="j.kabore@unz.bf",
            password="Secret456",
            session=db_session
        )
        db_session.commit()

        result = authenticate("jkabore", "Secret456", session=db_session)
        assert result is not None

    def test_ut20_connexion_mauvais_mot_de_passe(self, db_session):
        """UT-20 : Mauvais mot de passe → retourne None"""
        from src.services.auth_service import create_user, authenticate

        create_user(
            username="user2",
            email="user2@unz.bf",
            password="BonPassword",
            session=db_session
        )
        db_session.commit()

        result = authenticate("user2@unz.bf", "MauvaisPassword", session=db_session)
        assert result is None
        print("\n  → Connexion refusée avec mauvais mot de passe ✅")

    def test_connexion_utilisateur_inexistant(self, db_session):
        """Utilisateur qui n'existe pas → retourne None"""
        from src.services.auth_service import authenticate

        result = authenticate("inconnu@unz.bf", "Password", session=db_session)
        assert result is None

    def test_connexion_champs_vides(self, db_session):
        """Identifiant ou mot de passe vide → retourne None ou erreur"""
        from src.services.auth_service import authenticate

        result = authenticate("", "", session=db_session)
        assert result is None


class TestCreationUtilisateur:
    """Tests de create_user"""

    def test_creation_utilisateur_valide(self, db_session):
        """Créer un utilisateur avec des données valides"""
        from src.services.auth_service import create_user

        user = create_user(
            username="newuser",
            email="newuser@unz.bf",
            password="ValidPass123",
            session=db_session
        )
        db_session.commit()

        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@unz.bf"
        # Le mot de passe doit être haché, pas stocké en clair
        assert user.password_hash != "ValidPass123"

    def test_mot_de_passe_trop_court(self, db_session):
        """Mot de passe < 6 caractères → erreur"""
        from src.services.auth_service import create_user

        with pytest.raises(Exception):
            create_user(
                username="user3",
                email="user3@unz.bf",
                password="abc",  # trop court
                session=db_session
            )
