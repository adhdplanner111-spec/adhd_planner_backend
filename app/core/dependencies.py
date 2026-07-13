from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    
    # TAMBAHKAN INI UNTUK DEBUGGING
    print("DEBUG PAYLOAD:", payload) 
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token tidak valid")
    
    # CEK APA ISINYA DI SINI
    if "sub" not in payload and "uid" not in payload:
        raise HTTPException(
            status_code=401, 
            detail=f"Token hanya berisi: {list(payload.keys())}" # Ini akan memberitahu kita kunci apa yang ada
        )
    return payload
    
    # 3. Pastikan 'uid' ada di dalam payload
    # Jika di database Anda kuncinya bukan 'uid', ubah 'uid' di bawah ini
    if "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak mengandung informasi pengguna yang valid",
        )

    return payload