from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    # 1. Validasi token
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau kadaluwarsa",
        )
    
    # 2. Normalisasi: Pastikan ada 'uid' di dalam payload
    # Jika token pakai 'sub', kita copy nilainya ke 'uid' agar backend tidak error
    if "uid" not in payload and "sub" in payload:
        payload["uid"] = payload["sub"]
        
    # 3. Cek apakah setelah dinormalisasi, 'uid' benar-benar ada
    if "uid" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak mengandung informasi pengguna (uid/sub)",
        )
    
    return payload