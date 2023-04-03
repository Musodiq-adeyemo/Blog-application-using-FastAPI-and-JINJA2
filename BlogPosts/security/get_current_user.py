from fastapi_jwt_auth import AuthJWT
from fastapi import Depends,HTTPException,status

def get_current_user(Authorize:AuthJWT = Depends()):
    try:

        Authorize.jwt_required()
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to verify your access token")
    

    current_user = Authorize.get_jwt_subject()
    return current_user