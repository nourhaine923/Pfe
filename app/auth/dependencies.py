from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.auth.auth_utils import SECRET_KEY, ALGORITHM

security = HTTPBearer()


def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def doctor_or_admin(user=Depends(get_current_user)):

    if user["role"] not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    return user