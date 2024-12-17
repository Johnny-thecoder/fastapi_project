from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import models, schemas

# secret key and algorithm to JWT
SECRET_KEY = "your_secret_key" # to be changed in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize bcrypt context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes the password before storing it in the database."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_username_or_email(db: Session, username: str = None, email: str = None):
    """Fetches a user from the database by either username or email."""
    query = db.query(models.User)

    if username:
        query = query.filter(models.User.username == username)
    if email:
        query = query.filter(models.User.email == email)

    return query.first()


def create_user(db: Session, user_data: schemas.UserRegister):
    """Creates a new user in the database."""
    hashed_password = hash_password(user_data.password)
    db_user = models.User(
        username = user_data.username,
        email=user_data.email,
        password=hashed_password
    )

    # Add the new user to the session
    db.add(db_user)
    # Commit the transaction to save the user in the database
    db.commit()
    # Refresh the instance to get the latest data (e.g., generated ID)
    db.refresh(db_user)


def authenticate_user(db: Session, username: str, password: str):
    """Authenticates a user by checking if the username and password are correct."""
     # Fetch user by username
    user = get_user_by_username_or_email(db, username=username)
    # Verify the provided password
    if user and verify_password(password, user.password):
        return user
    # If user doesn't exist or password is incorrect, return None
    return None


def create_access_token(data: dict,
                        expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """Generates JWT token for a user."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """Verifies the JWT token and returns the decoded data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload["exp"] >= datetime.utcnow() else None
    except JWTError:
        return None