from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_session
from .models import SessionModel, UserType, UserModel


async def is_authenticated(request: Request, db: AsyncSession = Depends(get_session)):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized"
    )

    session_id = request.cookies.get("session_token")
    if not session_id:
        raise credentials_error

    result = await db.execute(select(SessionModel).where(SessionModel.token == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise credentials_error

    return session.user 


async def is_admin(user: UserModel = Depends(is_authenticated)):
    if user.role != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def is_owner(user: UserModel = Depends(is_authenticated)):
    if str(user.role).lower() != UserType.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return user
