"""Generate hashed secrets from plain text for manual DB insertion."""  # noqa: INP001

import bcrypt


def gen_secret_hashed(geheimnis: str) -> str:
    """Hash a plain text secret using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(geheimnis.encode("utf-8"), salt)
    return hashed.decode("utf-8")


if __name__ == "__main__":
    password = input("Password: ").strip()
    hashed = gen_secret_hashed(password)
    print("Secret hashed: " + hashed)
