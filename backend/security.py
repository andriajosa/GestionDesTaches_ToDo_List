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
