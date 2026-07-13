from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_access_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    
    # 1. Validasi token menggunakan fungsi verify_access_token Anda
    payload = verify_access_token(token)
    
    # 2. Jika payload kosong (token tidak valid/expired), lempar error 401
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau kadaluwarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Pastikan 'uid' ada di dalam payload
    # Jika di database Anda kuncinya bukan 'uid', ubah 'uid' di bawah ini
    if "uid" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak mengandung informasi pengguna yang valid",
        )

    return payload