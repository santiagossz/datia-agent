import uvicorn
from app.config import api_cfg, LOGGING_CONFIG
from fastapi import FastAPI
from app.api import agents

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Datia Agent API"}


app.include_router(agents.router)
app.add_api_route

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=api_cfg.HOST,
        port=api_cfg.PORT,
        reload=True,
        log_config=LOGGING_CONFIG,
    )
