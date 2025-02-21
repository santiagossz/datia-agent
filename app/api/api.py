from fastapi import FastAPI, APIRouter
from app.agents.graph import AgentsGraph


app = FastAPI()
api_router = APIRouter()

agent = AgentsGraph()
graph = agent.graph


@api_router.post("/test")
async def test(msg: str):
    res = await agent.run_workflow({"messages": msg})
    return res


@app.get("/")
async def root():
    return {"message": "Datia Agent API"}


app.include_router(api_router)
