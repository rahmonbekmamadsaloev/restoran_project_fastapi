from src.account.models import User, UserProfile
from src.account.schemas import CreateUserModelSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException

def create_user_with_profile(db: Session, user_data: CreateUserModelSchema):

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")


    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,  
        role=user_data.role
    )
    db.add(new_user)
    db.flush() 

    profile = UserProfile(user_id=new_user.id)
    db.add(profile)
    db.commit()
    db.refresh(new_user)

    return new_user
