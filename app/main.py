import uvicorn
from app.config import api_cfg, LOGGING_CONFIG

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=api_cfg.HOST,
        port=api_cfg.PORT,
        reload=True,
        log_config=LOGGING_CONFIG,
    )
