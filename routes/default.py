from fastapi import APIRouter

defaultRouter = APIRouter()


# Entry point to the API
@defaultRouter.get("/")
async def entry_point():
    return {"message": "welcome to Application Server!"}
