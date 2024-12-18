from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import schemas, crud, database


# Initialize the APIRouter instance for user-related endpoints
router = APIRouter()


@router.post("/register")
async def register_user(user: schemas.UserRegister,
                        db: Session = Depends(database.get_db)):
    """
    Endpoint to register a new user.
    Checks if the username or email already exists before creating a new user.
    If the user exists, it raises an HTTP 400 error.
    If the user is successfully created,
    it returns a success message with the user's ID.
    """
    # Check if the user with the same username or email already exists
    existing_user = crud.get_user_by_username_or_email(
        db, user.username, user.email)

    # If user already exists, raise a 400 error with a message
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered")

    # create a new user
    new_user = crud.create_user(db, user)

    # Return a success message with the user ID
    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post("/login")
async def login_user(user: schemas.UserLogin,
                     db: Session = Depends(database.get_db)):
    """
    Endpoint for user login.
    Verifies username and password.
    If data is correct, returns message and JWT token.
    If data is incorrect, returns HTTP error 401.
    """
    # User verification based on username and password
    authenticated_user = crud.authenticate_user(
        db, user.username, user.password)

    # If verification failed, we return HTTP error 401
    if not authenticated_user:
        raise HTTPException(
            status_code=401, detail="Invalid username or password"
        )

    # Generate JWT token for a logged user
    access_token = crud.create_access_token(data={"sub": user.username})

    # Return message
    return {
        "message": f"{user.username} - you are logged in",
        "access_token": access_token,
        "token_type": "bearer",
    }
