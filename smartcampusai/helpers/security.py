import bcrypt
import logging

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt and return the string hash."""
    try:
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise RuntimeError("Password secure hashing failed.")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify if plaintext password matches the hashed password."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False
