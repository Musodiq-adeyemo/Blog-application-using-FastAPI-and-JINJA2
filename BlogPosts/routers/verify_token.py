from fastapi import Depends,APIRouter,WebSocket,Query,Request,FastAPI
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from BlogPosts.schemas import VerifyToken


router = APIRouter(
    tags=["Verify Token"]
)
"""app = FastAPI()
@app.exception_handler(AuthJWTException)
async def authjwt_exception_handler(request:Request, exc:AuthJWTException):
    return JSONResponse(
        status_code= exc.status_code,
        content={"detail":exc.message}
    )"""

@router.get("/ws")
async def websocket(websocket:WebSocket,request:VerifyToken,Authorize:AuthJWT=Depends()):
#async def websocket(websocket:WebSocket,token:str=Query(...),Authorize:AuthJWT=Depends()):
    await websocket.accept()
    try:
        Authorize.jwt_required("websocket",token=request.token)
        await websocket.send_text("Successfully Login!")
        decoded_token = Authorize.get_raw_jwt(request.token)
        await websocket.send_text(f"Here is your decoded token:{decoded_token}")

    except AuthJWTException as err:
        await websocket.send_text(err.message)
        await websocket.close()

    return {"decoded_token":decoded_token}
