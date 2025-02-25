from fastapi import APIRouter, Depends
from app.agents import AgentsGraph, WorkflowState
from langchain_core.runnables import RunnableConfig
from typing import Annotated
from app.config import logger
from langgraph.types import Command

agent = AgentsGraph()
graph = agent.graph

router = APIRouter()


async def get_config(session_id: str) -> RunnableConfig:
    return RunnableConfig(configurable={"thread_id": session_id})


Config = Annotated[RunnableConfig, Depends(get_config)]


@router.post("/test")
async def test(msg: str, config: Config):
    state = WorkflowState(user_input=msg)
    res = agent.run_workflow(state, config)
    if agent.graph.get_state(config).tasks:
        return agent.graph.get_state(config).tasks[0].interrupts[0].value
    return res


@router.post("/validate_data")
async def validate_data(config: Config):
    res = agent.graph.invoke(Command(resume=""), config)
    if agent.graph.get_state(config).tasks:
        return agent.graph.get_state(config).tasks[0].interrupts[0].value
    return res


@router.post("/validate_plot")
async def validate_plot(human_input: str, config: Config):
    res = agent.graph.invoke(Command(resume=human_input), config)
    return res


@router.get("/memory")
async def memory(config: Config):
    return agent.get_memory(config)
