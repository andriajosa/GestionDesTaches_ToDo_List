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
