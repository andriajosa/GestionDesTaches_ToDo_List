import base64
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(clear_text: str) -> str:
    return generate_password_hash(clear_text)


def verifier_password(clear_text: str, hash_value: str) -> bool:
    return check_password_hash(hash_value, clear_text)


def chiffrer_texte(plain: str) -> str:
    """Simple encodage base64 pour éviter d'introduire une dépendance lourde.
    Ce n'est PAS un chiffrement sécurisé mais suffit pour l'exemple.
    """
    if plain is None:
        return None
    return base64.b64encode(plain.encode("utf-8")).decode("ascii")


def dechiffrer_texte(cipher: str) -> str:
    if cipher is None:
        return None
    try:
        return base64.b64decode(cipher.encode("ascii")).decode("utf-8")
    except Exception:
        return None
import bcrypt
from cryptography.fernet import Fernet
from flask import current_app



def hash_password(mot_de_passe: str) -> str:
    return bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verifier_password(mot_de_passe: str, hash_stocke: str) -> bool:
    return bcrypt.checkpw(mot_de_passe.encode("utf-8"), hash_stocke.encode("utf-8"))



def _get_fernet():
    cle = current_app.config["FERNET_KEY"]
    return Fernet(cle.encode("utf-8"))


def chiffrer_texte(texte: str) -> str:
    if texte is None:
        return None
    f = _get_fernet()
    return f.encrypt(texte.encode("utf-8")).decode("utf-8")


def dechiffrer_texte(texte_chiffre: str) -> str:
    if texte_chiffre is None:
        return None
    f = _get_fernet()
    return f.decrypt(texte_chiffre.encode("utf-8")).decode("utf-8")
