from passlib.context import CryptContext


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_pass_hash(password: str) -> str:
    return password_context.hash(password)


def verify_pass(password: str, password_hash: str):
    return password_context.verify(str(password), str(password_hash))
